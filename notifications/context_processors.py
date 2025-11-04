"""
Context processors for notifications app.
Adds notification-related variables to template context.
"""
from django.contrib.auth.models import AnonymousUser
from .models import Notification


def notifications(request):
    """
    Context processor that adds notification data to all templates.
    Provides unread_notifications_count and recent_notifications.

    Only adds data if user is authenticated (anonymous users get empty defaults).
    """
    context = {
        'unread_notifications_count': 0,
        'recent_notifications': [],
    }

    # Only process if user is authenticated
    if request.user and not isinstance(request.user, AnonymousUser) and request.user.is_authenticated:
        try:
            # Get unread notifications count
            unread_count = Notification.objects.filter(
                user=request.user,
                is_read=False
            ).count()
            context['unread_notifications_count'] = unread_count

            # Get recent notifications (last 5)
            recent = Notification.objects.filter(
                user=request.user
            ).order_by('-created_at')[:5]
            context['recent_notifications'] = recent
        except Exception:
            # If there's any error (e.g., migrations not run), provide safe defaults
            pass

    return context
