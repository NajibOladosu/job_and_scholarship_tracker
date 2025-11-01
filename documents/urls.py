"""
URL configuration for documents app.
"""
from django.urls import path
from . import views

app_name = 'documents'

urlpatterns = [
    # Document management
    path('', views.DocumentListView.as_view(), name='document_list'),
    path('upload/', views.document_upload_view, name='upload'),
    path('<int:pk>/', views.DocumentDetailView.as_view(), name='document_detail'),
    path('<int:pk>/delete/', views.DocumentDeleteView.as_view(), name='document_delete'),
    path('<int:pk>/reprocess/', views.reprocess_document_view, name='reprocess_document'),
]
