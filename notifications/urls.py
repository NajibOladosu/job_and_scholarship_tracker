"""
URL configuration for notifications app.
"""
from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
    # Notifications
    path('', views.notification_list_view, name='list'),
    path('<int:pk>/mark-read/', views.notification_mark_read_view, name='mark_read'),
    path('mark-all-read/', views.notification_mark_all_read_view, name='mark_all_read'),

    # Reminders
    path('reminders/', views.reminder_list_view, name='reminders'),
    path('reminders/create/', views.reminder_create_view, name='reminder_create'),
    path('reminders/<int:pk>/edit/', views.reminder_edit_view, name='reminder_edit'),
    path('reminders/<int:pk>/delete/', views.reminder_delete_view, name='reminder_delete'),
]
