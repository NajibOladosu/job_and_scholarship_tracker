"""
URL configuration for Job & Scholarship Tracker (Trackly).
"""
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from core.views import home_view, react_app_view

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),

    # API endpoints
    path('api/', include('config.api_urls')),

    # Django Template-based Apps (Legacy - can be removed if using React exclusively)
    path('accounts/', include('accounts.urls')),
    path('tracker/', include('tracker.urls')),
    path('documents/', include('documents.urls')),
    path('notifications/', include('notifications.urls')),

    # Home page
    path('', home_view, name='home'),
]

# Error handlers
handler404 = 'core.views.handler404'
handler500 = 'core.views.handler500'

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Serve React app (catch-all route) - COMMENTED OUT TEMPORARILY FOR DEBUGGING
# Uncomment once frontend build is working
# urlpatterns += [
#     re_path(r'^.*', react_app_view, name='react_app'),
# ]
