import datetime
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    interval_multiplier = models.FloatField(default=1.0)

    def __str__(self):
        return f"Profil de {self.user.username}"


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.get_or_create(user=instance)


class Theme(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='themes', null=True, blank=True)
    name = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']
        unique_together = [('user', 'name')]

    def __str__(self):
        return self.name


class Card(models.Model):
    theme = models.ForeignKey(Theme, on_delete=models.CASCADE, related_name='cards')
    question = models.TextField()
    answer = models.TextField()
    repetitions = models.IntegerField(default=0)
    easiness_factor = models.FloatField(default=2.5)
    interval = models.IntegerField(default=0)
    due_date = models.DateField(default=datetime.date.today)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['due_date', 'created_at']

    def __str__(self):
        return self.question[:60]

    def apply_sm2(self, quality, multiplier=1.0):
        """SM-2 algorithm. quality: 2 (fail), 3 (hard), 5 (easy)."""
        q = quality

        if q < 3:
            self.repetitions = 0
            self.interval = 1
        else:
            if self.repetitions == 0:
                self.interval = 1
            elif self.repetitions == 1:
                self.interval = 6
            else:
                self.interval = round(self.interval * self.easiness_factor)
            self.repetitions += 1

        self.easiness_factor += 0.1 - (5 - q) * (0.08 + (5 - q) * 0.02)
        if self.easiness_factor < 1.3:
            self.easiness_factor = 1.3

        self.interval = max(1, round(self.interval * multiplier))
        self.due_date = datetime.date.today() + datetime.timedelta(days=self.interval)
        self.save()


class ReviewLog(models.Model):
    QUALITY_CHOICES = [(2, 'Echec'), (3, 'Approximatif'), (5, 'Valide')]

    card = models.ForeignKey(Card, on_delete=models.CASCADE, related_name='reviews')
    reviewed_at = models.DateField(auto_now_add=True)
    quality = models.IntegerField(choices=QUALITY_CHOICES)

    class Meta:
        ordering = ['-reviewed_at']
