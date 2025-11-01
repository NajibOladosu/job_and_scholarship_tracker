"""
URL configuration for Job & Scholarship Tracker.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from core.views import home_view

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),

    # Home
    path('', home_view, name='home'),

    # Apps
    path('accounts/', include('accounts.urls')),
    path('tracker/', include('tracker.urls')),
    path('documents/', include('documents.urls')),
    # path('notifications/', include('notifications.urls')),  # TODO: Create notifications URLs
]

# Error handlers
handler404 = 'core.views.handler404'
handler500 = 'core.views.handler500'

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
