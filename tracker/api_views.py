"""
API Views for the tracker app.
"""
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count, Q

from .models import (
    Application, Question, Response as AppResponse, ApplicationStatus,
    Tag, Note, Interview, Interviewer, Referral
)
from .serializers import (
    ApplicationListSerializer, ApplicationDetailSerializer,
    ApplicationCreateUpdateSerializer, QuestionSerializer,
    ResponseSerializer, ApplicationStatusSerializer, TagSerializer,
    NoteSerializer, InterviewSerializer, InterviewerSerializer,
    ReferralSerializer
)


class ApplicationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Application model.
    Provides CRUD operations for job and scholarship applications.
    """
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['application_type', 'status', 'priority']
    search_fields = ['company_name', 'position_title', 'job_description']
    ordering_fields = ['created_at', 'deadline', 'priority']
    ordering = ['-created_at']

    def get_queryset(self):
        """Return applications for the current user only."""
        return Application.objects.filter(user=self.request.user).select_related('user').prefetch_related('tags', 'questions')

    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'list':
            return ApplicationListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return ApplicationCreateUpdateSerializer
        return ApplicationDetailSerializer

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get application statistics."""
        queryset = self.get_queryset()

        stats = {
            'total': queryset.count(),
            'by_status': dict(queryset.values('status').annotate(count=Count('id')).values_list('status', 'count')),
            'by_priority': dict(queryset.values('priority').annotate(count=Count('id')).values_list('priority', 'count')),
            'by_type': dict(queryset.values('application_type').annotate(count=Count('id')).values_list('application_type', 'count')),
        }

        return Response(stats)

    @action(detail=True, methods=['post'])
    def change_status(self, request, pk=None):
        """Change application status."""
        application = self.get_object()
        new_status = request.data.get('status')
        notes = request.data.get('notes', '')

        if not new_status:
            return Response(
                {'error': 'Status is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Create status history entry
        ApplicationStatus.objects.create(
            application=application,
            status=new_status,
            notes=notes
        )

        # Update application status
        application.status = new_status
        application.save()

        serializer = self.get_serializer(application)
        return Response(serializer.data)


class QuestionViewSet(viewsets.ModelViewSet):
    """ViewSet for Question model."""
    permission_classes = [IsAuthenticated]
    serializer_class = QuestionSerializer

    def get_queryset(self):
        """Return questions for applications owned by the current user."""
        return Question.objects.filter(application__user=self.request.user)


class ResponseViewSet(viewsets.ModelViewSet):
    """ViewSet for Response model."""
    permission_classes = [IsAuthenticated]
    serializer_class = ResponseSerializer

    def get_queryset(self):
        """Return responses for applications owned by the current user."""
        return AppResponse.objects.filter(question__application__user=self.request.user)


class TagViewSet(viewsets.ModelViewSet):
    """ViewSet for Tag model."""
    permission_classes = [IsAuthenticated]
    serializer_class = TagSerializer

    def get_queryset(self):
        """Return tags for applications owned by the current user."""
        return Tag.objects.filter(applications__user=self.request.user).distinct()


class NoteViewSet(viewsets.ModelViewSet):
    """ViewSet for Note model."""
    permission_classes = [IsAuthenticated]
    serializer_class = NoteSerializer

    def get_queryset(self):
        """Return notes for applications owned by the current user."""
        return Note.objects.filter(application__user=self.request.user)


class InterviewViewSet(viewsets.ModelViewSet):
    """ViewSet for Interview model."""
    permission_classes = [IsAuthenticated]
    serializer_class = InterviewSerializer

    def get_queryset(self):
        """Return interviews for applications owned by the current user."""
        return Interview.objects.filter(application__user=self.request.user)


class ReferralViewSet(viewsets.ModelViewSet):
    """ViewSet for Referral model."""
    permission_classes = [IsAuthenticated]
    serializer_class = ReferralSerializer

    def get_queryset(self):
        """Return referrals for applications owned by the current user."""
        return Referral.objects.filter(application__user=self.request.user)
