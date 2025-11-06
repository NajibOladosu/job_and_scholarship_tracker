"""
URL configuration for tracker app.
"""
from django.urls import path
from . import views

app_name = 'tracker'

urlpatterns = [
    # Dashboard
    path('', views.dashboard_view, name='dashboard'),

    # Application URLs
    path('application/create/', views.ApplicationCreateView.as_view(), name='application_create'),
    path('application/quick/', views.quick_application_create_view, name='quick_application_create'),
    path('application/<int:pk>/', views.ApplicationDetailView.as_view(), name='application_detail'),
    path('application/<int:pk>/edit/', views.ApplicationUpdateView.as_view(), name='application_edit'),
    path('application/<int:pk>/delete/', views.ApplicationDeleteView.as_view(), name='application_delete'),

    # Question URLs
    path('application/<int:application_pk>/question/add/', views.add_question_view, name='add_question'),

    # Response URLs
    path('question/<int:question_pk>/edit-response/', views.edit_response_view, name='edit_response'),
    path('question/<int:question_pk>/regenerate/', views.regenerate_response_view, name='regenerate_response'),
    path('application/<int:application_pk>/generate-all/', views.generate_responses_view, name='generate_responses'),

    # Note URLs
    path('notes/', views.NoteListView.as_view(), name='note_list'),
    path('notes/create/', views.NoteCreateView.as_view(), name='note_create'),
    path('notes/<int:pk>/edit/', views.NoteUpdateView.as_view(), name='note_edit'),
    path('notes/<int:pk>/delete/', views.NoteDeleteView.as_view(), name='note_delete'),

    # Note API endpoints
    path('api/notes/autosave/', views.note_autosave_api, name='note_autosave_api'),
    path('api/notes/<int:pk>/toggle-pin/', views.note_toggle_pin_api, name='note_toggle_pin_api'),

    # Analytics URLs
    path('analytics/', views.analytics_dashboard_view, name='analytics'),
    path('analytics/api/sankey/', views.sankey_data_api, name='sankey_data_api'),
    path('analytics/api/timeline/', views.timeline_data_api, name='timeline_data_api'),

    # Interview URLs
    path('application/<int:application_id>/interview/create/', views.interview_create_view, name='interview_create'),
    path('interview/<int:pk>/edit/', views.interview_update_view, name='interview_edit'),
    path('interview/<int:pk>/delete/', views.interview_delete_view, name='interview_delete'),
    path('interviews/', views.interview_list_view, name='interview_list'),

    # Archive URLs
    path('application/<int:pk>/archive/', views.application_archive_view, name='application_archive'),
    path('application/<int:pk>/unarchive/', views.application_unarchive_view, name='application_unarchive'),
    path('archive/', views.archive_list_view, name='archive_list'),

    # Referral URLs
    path('application/<int:application_id>/referral/create/', views.referral_create_view, name='referral_create'),
    path('referral/<int:pk>/edit/', views.referral_update_view, name='referral_edit'),
    path('referral/<int:pk>/delete/', views.referral_delete_view, name='referral_delete'),

    # Quick Actions API URLs
    path('api/application/<int:application_id>/quick-interview/', views.quick_add_interview_api, name='quick_add_interview_api'),
    path('api/applications/bulk-archive/', views.bulk_archive_api, name='bulk_archive_api'),
    path('api/applications/bulk-delete/', views.bulk_delete_api, name='bulk_delete'),
    path('api/applications/export/', views.export_applications_view, name='export_applications'),
    path('api/interviews/schedule/', views.schedule_interview_api, name='schedule_interview'),
]
