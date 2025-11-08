"""
API Serializers for the tracker app.
"""
from rest_framework import serializers
from .models import (
    Application, Question, Response, ApplicationStatus,
    Tag, Note, Interview, Interviewer, Referral
)


class QuestionSerializer(serializers.ModelSerializer):
    """Serializer for Question model."""

    class Meta:
        model = Question
        fields = [
            'id', 'application', 'question_text', 'question_type',
            'is_required', 'is_extracted', 'order', 'created_at'
        ]
        read_only_fields = ['created_at']


class ResponseSerializer(serializers.ModelSerializer):
    """Serializer for Response model."""
    question_text = serializers.CharField(source='question.question_text', read_only=True)
    final_response = serializers.CharField(read_only=True)

    class Meta:
        model = Response
        fields = [
            'id', 'question', 'question_text', 'generated_response',
            'edited_response', 'final_response', 'is_ai_generated',
            'generation_prompt', 'generated_at', 'last_edited_at', 'version'
        ]
        read_only_fields = ['generated_at', 'last_edited_at', 'version', 'final_response']


class TagSerializer(serializers.ModelSerializer):
    """Serializer for Tag model."""
    application_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Tag
        fields = ['id', 'name', 'color', 'application_count', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at', 'application_count']


class NoteSerializer(serializers.ModelSerializer):
    """Serializer for Note model."""

    class Meta:
        model = Note
        fields = [
            'id', 'application', 'title', 'content', 'plain_text',
            'is_pinned', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class InterviewerSerializer(serializers.ModelSerializer):
    """Serializer for Interviewer model."""

    class Meta:
        model = Interviewer
        fields = [
            'id', 'interview', 'name', 'title', 'email', 'phone',
            'linkedin_url', 'notes', 'created_at'
        ]
        read_only_fields = ['created_at']


class InterviewSerializer(serializers.ModelSerializer):
    """Serializer for Interview model."""
    interviewers = InterviewerSerializer(many=True, read_only=True)
    is_upcoming = serializers.BooleanField(read_only=True)
    is_past = serializers.BooleanField(read_only=True)

    class Meta:
        model = Interview
        fields = [
            'id', 'application', 'user', 'interview_type', 'scheduled_date',
            'duration_minutes', 'location', 'meeting_link', 'notes',
            'status', 'is_upcoming', 'is_past', 'interviewers',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['user', 'created_at', 'updated_at', 'is_upcoming', 'is_past']


class ReferralSerializer(serializers.ModelSerializer):
    """Serializer for Referral model."""

    class Meta:
        model = Referral
        fields = [
            'id', 'application', 'user', 'name', 'relationship',
            'company', 'email', 'phone', 'referred_date',
            'notes', 'created_at'
        ]
        read_only_fields = ['user', 'created_at']


class ApplicationStatusSerializer(serializers.ModelSerializer):
    """Serializer for ApplicationStatus model."""

    class Meta:
        model = ApplicationStatus
        fields = [
            'id', 'application', 'status', 'changed_by', 'notes', 'created_at'
        ]
        read_only_fields = ['created_at']


class ApplicationListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list views."""
    tags = TagSerializer(many=True, read_only=True)
    question_count = serializers.IntegerField(read_only=True)
    is_overdue = serializers.BooleanField(read_only=True)
    days_until_deadline = serializers.IntegerField(read_only=True)

    class Meta:
        model = Application
        fields = [
            'id', 'application_type', 'title', 'company_or_institution',
            'status', 'priority', 'deadline', 'submitted_at', 'is_archived',
            'tags', 'question_count', 'is_overdue', 'days_until_deadline',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'question_count', 'is_overdue', 'days_until_deadline']


class ApplicationDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for single application views."""
    questions = QuestionSerializer(many=True, read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    notes_list = NoteSerializer(many=True, read_only=True)
    interviews = InterviewSerializer(many=True, read_only=True)
    referrals = ReferralSerializer(many=True, read_only=True)
    status_history = ApplicationStatusSerializer(many=True, read_only=True)
    question_count = serializers.IntegerField(read_only=True)
    is_overdue = serializers.BooleanField(read_only=True)
    days_until_deadline = serializers.IntegerField(read_only=True)

    class Meta:
        model = Application
        fields = [
            'id', 'user', 'application_type', 'title', 'company_or_institution',
            'url', 'description', 'deadline', 'status', 'priority',
            'submitted_at', 'notes', 'is_archived', 'archived_at',
            'question_count', 'is_overdue', 'days_until_deadline',
            'questions', 'tags', 'notes_list', 'interviews', 'referrals',
            'status_history', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'user', 'created_at', 'updated_at', 'question_count',
            'is_overdue', 'days_until_deadline'
        ]

    def create(self, validated_data):
        # Set the user from the request context
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class ApplicationCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating applications."""

    class Meta:
        model = Application
        fields = [
            'application_type', 'title', 'company_or_institution',
            'url', 'description', 'deadline', 'status', 'priority',
            'submitted_at', 'notes', 'is_archived', 'archived_at'
        ]

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)
