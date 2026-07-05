from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),

    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    path('settings/', views.user_settings, name='user_settings'),
    path('how-it-works/', views.how_it_works, name='how_it_works'),

    path('themes/new/', views.theme_create, name='theme_create'),
    path('themes/<int:theme_id>/', views.theme_detail, name='theme_detail'),
    path('themes/<int:theme_id>/edit/', views.theme_edit, name='theme_edit'),
    path('themes/<int:theme_id>/delete/', views.theme_delete, name='theme_delete'),
    path('themes/<int:theme_id>/cards/new/', views.card_create, name='card_create'),

    path('cards/<int:card_id>/edit/', views.card_edit, name='card_edit'),
    path('cards/<int:card_id>/delete/', views.card_delete, name='card_delete'),
    path('cards/<int:card_id>/reset/', views.card_reset, name='card_reset'),

    path('review/all/', views.review_start, name='review_start'),
    path('review/theme/<int:theme_id>/', views.review_start, name='review_start_theme'),
    path('review/session/', views.review_session, name='review_session'),
    path('review/complete/', views.review_complete, name='review_complete'),

    path('export/', views.export_data, name='export_data'),
    path('import/', views.import_data, name='import_data'),
]
