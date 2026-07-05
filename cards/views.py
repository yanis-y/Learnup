import json
import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib import messages
from django.db.models import Count, Q
from django.urls import reverse
from .models import Theme, Card, ReviewLog


def dashboard(request):
    today = datetime.date.today()
    themes = Theme.objects.annotate(
        total=Count('cards'),
        due=Count('cards', filter=Q(cards__due_date__lte=today))
    )
    total_due = Card.objects.filter(due_date__lte=today).count()
    total_cards = Card.objects.count()

    thirty_days_ago = today - datetime.timedelta(days=29)
    logs = (ReviewLog.objects
            .filter(reviewed_at__gte=thirty_days_ago)
            .values('reviewed_at')
            .annotate(count=Count('id')))
    review_counts = {str(log['reviewed_at']): log['count'] for log in logs}

    max_count = max((review_counts.values()), default=1) or 1
    chart_data = []
    for i in range(30):
        d = thirty_days_ago + datetime.timedelta(days=i)
        count = review_counts.get(str(d), 0)
        chart_data.append({
            'date': str(d),
            'count': count,
            'height_pct': round((count / max_count) * 100),
        })

    return render(request, 'cards/dashboard.html', {
        'themes': themes,
        'total_due': total_due,
        'total_cards': total_cards,
        'chart_data': chart_data,
        'today': today,
    })


def theme_create(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        if not name:
            messages.error(request, 'Le nom du thème est requis.')
            return render(request, 'cards/theme_form.html', {'title': 'Nouveau thème', 'name': ''})
        if Theme.objects.filter(name=name).exists():
            messages.error(request, 'Un thème avec ce nom existe déjà.')
            return render(request, 'cards/theme_form.html', {'title': 'Nouveau thème', 'name': name})
        Theme.objects.create(name=name)
        messages.success(request, f'Thème « {name} » créé.')
        return redirect('dashboard')
    return render(request, 'cards/theme_form.html', {'title': 'Nouveau thème', 'name': ''})


def theme_detail(request, theme_id):
    theme = get_object_or_404(Theme, id=theme_id)
    today = datetime.date.today()
    cards = theme.cards.all()
    due_count = cards.filter(due_date__lte=today).count()
    return render(request, 'cards/theme_detail.html', {
        'theme': theme,
        'cards': cards,
        'due_count': due_count,
        'today': today,
    })


def theme_edit(request, theme_id):
    theme = get_object_or_404(Theme, id=theme_id)
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        if not name:
            messages.error(request, 'Le nom du thème est requis.')
            return render(request, 'cards/theme_form.html', {'title': 'Modifier le thème', 'theme': theme, 'name': theme.name})
        if Theme.objects.filter(name=name).exclude(id=theme_id).exists():
            messages.error(request, 'Un thème avec ce nom existe déjà.')
            return render(request, 'cards/theme_form.html', {'title': 'Modifier le thème', 'theme': theme, 'name': name})
        theme.name = name
        theme.save()
        messages.success(request, 'Thème renommé.')
        return redirect('theme_detail', theme_id=theme_id)
    return render(request, 'cards/theme_form.html', {'title': 'Modifier le thème', 'theme': theme, 'name': theme.name})


def theme_delete(request, theme_id):
    theme = get_object_or_404(Theme, id=theme_id)
    if request.method == 'POST':
        card_count = theme.cards.count()
        name = theme.name
        theme.delete()
        messages.success(request, f'Thème « {name} » et ses {card_count} carte(s) supprimés.')
        return redirect('dashboard')
    return render(request, 'cards/confirm_delete.html', {
        'title': 'Supprimer le thème',
        'object_name': theme.name,
        'warning': f'Toutes les cartes ({theme.cards.count()}) seront supprimées définitivement.',
        'cancel_url': reverse('theme_detail', kwargs={'theme_id': theme_id}),
    })


def card_create(request, theme_id):
    theme = get_object_or_404(Theme, id=theme_id)
    if request.method == 'POST':
        question = request.POST.get('question', '').strip()
        answer = request.POST.get('answer', '').strip()
        if not question or not answer:
            messages.error(request, 'La question et la réponse sont requises.')
            return render(request, 'cards/card_form.html', {
                'title': 'Nouvelle carte', 'theme': theme,
                'question': question, 'answer': answer,
            })
        Card.objects.create(theme=theme, question=question, answer=answer)
        if request.POST.get('add_another'):
            messages.success(request, 'Carte créée. Ajoutez-en une autre.')
            return redirect('card_create', theme_id=theme_id)
        messages.success(request, 'Carte créée.')
        return redirect('theme_detail', theme_id=theme_id)
    return render(request, 'cards/card_form.html', {
        'title': 'Nouvelle carte', 'theme': theme, 'question': '', 'answer': '',
    })


def card_edit(request, card_id):
    card = get_object_or_404(Card, id=card_id)
    if request.method == 'POST':
        question = request.POST.get('question', '').strip()
        answer = request.POST.get('answer', '').strip()
        if not question or not answer:
            messages.error(request, 'La question et la réponse sont requises.')
            return render(request, 'cards/card_form.html', {
                'title': 'Modifier la carte', 'theme': card.theme,
                'card': card, 'question': question, 'answer': answer,
            })
        card.question = question
        card.answer = answer
        card.save()
        messages.success(request, 'Carte modifiée.')
        return redirect('theme_detail', theme_id=card.theme_id)
    return render(request, 'cards/card_form.html', {
        'title': 'Modifier la carte', 'theme': card.theme,
        'card': card, 'question': card.question, 'answer': card.answer,
    })


def card_delete(request, card_id):
    card = get_object_or_404(Card, id=card_id)
    theme_id = card.theme_id
    if request.method == 'POST':
        card.delete()
        messages.success(request, 'Carte supprimée.')
        return redirect('theme_detail', theme_id=theme_id)
    return render(request, 'cards/confirm_delete.html', {
        'title': 'Supprimer la carte',
        'object_name': (card.question[:80] + '…') if len(card.question) > 80 else card.question,
        'warning': 'Cette action est irréversible.',
        'cancel_url': reverse('theme_detail', kwargs={'theme_id': theme_id}),
    })


def card_reset(request, card_id):
    """Reset SM-2 stats so the card is due today and starts fresh."""
    card = get_object_or_404(Card, id=card_id)
    if request.method == 'POST':
        card.repetitions = 0
        card.easiness_factor = 2.5
        card.interval = 0
        card.due_date = datetime.date.today()
        card.save()
        messages.success(request, 'Progression de la carte réinitialisée.')
    return redirect('theme_detail', theme_id=card.theme_id)


def review_start(request, theme_id=None):
    today = datetime.date.today()
    if theme_id:
        theme = get_object_or_404(Theme, id=theme_id)
        cards_qs = Card.objects.filter(theme=theme, due_date__lte=today)
    else:
        theme = None
        cards_qs = Card.objects.filter(due_date__lte=today)

    card_ids = list(cards_qs.order_by('?').values_list('id', flat=True))

    if not card_ids:
        messages.info(request, 'Aucune carte à réviser pour le moment.')
        return redirect('theme_detail', theme_id=theme_id) if theme_id else redirect('dashboard')

    request.session['review_queue'] = card_ids
    request.session['review_index'] = 0
    request.session['review_stats'] = {'total': len(card_ids), 'fail': 0, 'hard': 0, 'easy': 0}
    request.session['review_theme_id'] = theme_id
    request.session['show_answer'] = False

    return redirect('review_session')


def review_session(request):
    queue = request.session.get('review_queue')
    if not queue:
        return redirect('dashboard')

    index = request.session.get('review_index', 0)
    if index >= len(queue):
        return redirect('review_complete')

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'show':
            request.session['show_answer'] = True
            return redirect('review_session')

        if action == 'rate':
            quality = int(request.POST.get('quality', 2))
            if quality not in (2, 3, 5):
                quality = 2
            card = get_object_or_404(Card, id=queue[index])
            card.apply_sm2(quality)
            ReviewLog.objects.create(card=card, quality=quality)

            stats = request.session['review_stats']
            if quality == 2:
                stats['fail'] += 1
            elif quality == 3:
                stats['hard'] += 1
            else:
                stats['easy'] += 1
            request.session['review_stats'] = stats
            request.session['review_index'] = index + 1
            request.session['show_answer'] = False
            request.session.modified = True
            return redirect('review_session')

    card = get_object_or_404(Card, id=queue[index])
    show_answer = request.session.get('show_answer', False)
    total = len(queue)
    progress_pct = round((index / total) * 100) if total else 0

    return render(request, 'cards/review_session.html', {
        'card': card,
        'show_answer': show_answer,
        'current': index + 1,
        'total': total,
        'progress_pct': progress_pct,
    })


def review_complete(request):
    stats = request.session.get('review_stats', {'total': 0, 'fail': 0, 'hard': 0, 'easy': 0})
    theme_id = request.session.get('review_theme_id')
    for key in ['review_queue', 'review_index', 'review_stats', 'review_theme_id', 'show_answer']:
        request.session.pop(key, None)
    return render(request, 'cards/review_complete.html', {'stats': stats, 'theme_id': theme_id})


def export_data(request):
    themes = Theme.objects.prefetch_related('cards').all()
    data = {
        'export_date': str(datetime.date.today()),
        'version': '1.0',
        'themes': [
            {
                'name': theme.name,
                'cards': [
                    {
                        'question': card.question,
                        'answer': card.answer,
                        'repetitions': card.repetitions,
                        'easiness_factor': round(card.easiness_factor, 4),
                        'interval': card.interval,
                        'due_date': str(card.due_date),
                    }
                    for card in theme.cards.all()
                ],
            }
            for theme in themes
        ],
    }
    response = HttpResponse(
        json.dumps(data, indent=2, ensure_ascii=False),
        content_type='application/json; charset=utf-8',
    )
    response['Content-Disposition'] = f'attachment; filename="flashcards_{datetime.date.today()}.json"'
    return response


def import_data(request):
    if request.method != 'POST':
        return redirect('dashboard')
    file = request.FILES.get('file')
    if not file:
        messages.error(request, 'Aucun fichier sélectionné.')
        return redirect('dashboard')
    try:
        data = json.loads(file.read().decode('utf-8'))
        created_themes = created_cards = 0
        for theme_data in data.get('themes', []):
            theme, created = Theme.objects.get_or_create(name=theme_data['name'])
            if created:
                created_themes += 1
            for c in theme_data.get('cards', []):
                Card.objects.create(
                    theme=theme,
                    question=c['question'],
                    answer=c['answer'],
                    repetitions=int(c.get('repetitions', 0)),
                    easiness_factor=float(c.get('easiness_factor', 2.5)),
                    interval=int(c.get('interval', 0)),
                    due_date=c.get('due_date', str(datetime.date.today())),
                )
                created_cards += 1
        messages.success(request, f'Import OK : {created_themes} thème(s), {created_cards} carte(s) créés.')
    except Exception as e:
        messages.error(request, f"Erreur lors de l'import : {e}")
    return redirect('dashboard')
