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
]
