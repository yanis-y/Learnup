from django.contrib import admin
from .models import Theme, Card, ReviewLog


@admin.register(Theme)
class ThemeAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at']
    search_fields = ['name']


@admin.register(Card)
class CardAdmin(admin.ModelAdmin):
    list_display = ['question', 'theme', 'due_date', 'repetitions', 'easiness_factor', 'interval']
    list_filter = ['theme']
    search_fields = ['question', 'answer']


@admin.register(ReviewLog)
class ReviewLogAdmin(admin.ModelAdmin):
    list_display = ['card', 'quality', 'reviewed_at']
    list_filter = ['quality', 'reviewed_at']
