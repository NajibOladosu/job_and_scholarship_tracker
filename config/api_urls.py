"""
API URL Configuration for the Job & Scholarship Tracker.
All API routes are prefixed with /api/
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView

# Import viewsets
from tracker.api_views import (
    ApplicationViewSet, QuestionViewSet, ResponseViewSet,
    TagViewSet, NoteViewSet, InterviewViewSet, ReferralViewSet
)
from documents.api_views import DocumentViewSet
from notifications.api_views import NotificationViewSet, ReminderViewSet
from accounts.api_views import (
    UserRegistrationView, UserProfileView, ChangePasswordView, current_user
)

# Create router
router = DefaultRouter()

# Tracker app endpoints
router.register(r'applications', ApplicationViewSet, basename='application')
router.register(r'questions', QuestionViewSet, basename='question')
router.register(r'responses', ResponseViewSet, basename='response')
router.register(r'tags', TagViewSet, basename='tag')
router.register(r'notes', NoteViewSet, basename='note')
router.register(r'interviews', InterviewViewSet, basename='interview')
router.register(r'referrals', ReferralViewSet, basename='referral')

# Documents app endpoints
router.register(r'documents', DocumentViewSet, basename='document')

# Notifications app endpoints
router.register(r'notifications', NotificationViewSet, basename='notification')
router.register(r'reminders', ReminderViewSet, basename='reminder')

urlpatterns = [
    # JWT Authentication
    path('auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('auth/register/', UserRegistrationView.as_view(), name='register'),

    # User endpoints
    path('auth/me/', current_user, name='current_user'),
    path('auth/profile/', UserProfileView.as_view(), name='user_profile'),
    path('auth/change-password/', ChangePasswordView.as_view(), name='change_password'),

    # Router URLs
    path('', include(router.urls)),
]
