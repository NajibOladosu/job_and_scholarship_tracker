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
            'is_optional', 'order', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class ResponseSerializer(serializers.ModelSerializer):
    """Serializer for Response model."""
    question_text = serializers.CharField(source='question.question_text', read_only=True)

    class Meta:
        model = Response
        fields = [
            'id', 'question', 'question_text', 'response_text',
            'is_generated', 'confidence_score', 'source_documents',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class TagSerializer(serializers.ModelSerializer):
    """Serializer for Tag model."""

    class Meta:
        model = Tag
        fields = ['id', 'name', 'color', 'created_at']
        read_only_fields = ['created_at']


class NoteSerializer(serializers.ModelSerializer):
    """Serializer for Note model."""

    class Meta:
        model = Note
        fields = [
            'id', 'application', 'title', 'content',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class InterviewerSerializer(serializers.ModelSerializer):
    """Serializer for Interviewer model."""

    class Meta:
        model = Interviewer
        fields = [
            'id', 'interview', 'name', 'role', 'email',
            'linkedin_url', 'notes'
        ]


class InterviewSerializer(serializers.ModelSerializer):
    """Serializer for Interview model."""
    interviewers = InterviewerSerializer(many=True, read_only=True)

    class Meta:
        model = Interview
        fields = [
            'id', 'application', 'interview_type', 'scheduled_at',
            'duration_minutes', 'location', 'is_virtual', 'meeting_link',
            'status', 'preparation_notes', 'feedback', 'rating',
            'interviewers', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class ReferralSerializer(serializers.ModelSerializer):
    """Serializer for Referral model."""

    class Meta:
        model = Referral
        fields = [
            'id', 'application', 'referrer_name', 'referrer_email',
            'referrer_company_position', 'relationship',
            'contact_date', 'notes', 'created_at'
        ]
        read_only_fields = ['created_at']


class ApplicationStatusSerializer(serializers.ModelSerializer):
    """Serializer for ApplicationStatus model."""

    class Meta:
        model = ApplicationStatus
        fields = [
            'id', 'application', 'status', 'notes',
            'changed_at', 'created_at'
        ]
        read_only_fields = ['created_at']


class ApplicationListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list views."""
    tags = TagSerializer(many=True, read_only=True)
    question_count = serializers.SerializerMethodField()
    response_count = serializers.SerializerMethodField()

    class Meta:
        model = Application
        fields = [
            'id', 'application_type', 'company_name', 'position_title',
            'status', 'priority', 'deadline', 'tags',
            'question_count', 'response_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def get_question_count(self, obj):
        return obj.questions.count()

    def get_response_count(self, obj):
        return Response.objects.filter(question__application=obj).count()


class ApplicationDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for single application views."""
    questions = QuestionSerializer(many=True, read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    notes = NoteSerializer(many=True, read_only=True)
    interviews = InterviewSerializer(many=True, read_only=True)
    referral = ReferralSerializer(read_only=True)
    status_history = ApplicationStatusSerializer(many=True, read_only=True, source='applicationstatus_set')

    class Meta:
        model = Application
        fields = [
            'id', 'user', 'application_type', 'company_name',
            'position_title', 'application_url', 'job_description',
            'requirements', 'status', 'priority', 'deadline',
            'submission_date', 'follow_up_date', 'salary_range',
            'location', 'is_remote', 'company_website',
            'contact_person_name', 'contact_person_email',
            'cover_letter', 'resume_version', 'additional_documents',
            'questions', 'tags', 'notes', 'interviews', 'referral',
            'status_history', 'created_at', 'updated_at'
        ]
        read_only_fields = ['user', 'created_at', 'updated_at']

    def create(self, validated_data):
        # Set the user from the request context
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class ApplicationCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating applications."""

    class Meta:
        model = Application
        fields = [
            'application_type', 'company_name', 'position_title',
            'application_url', 'job_description', 'requirements',
            'status', 'priority', 'deadline', 'submission_date',
            'follow_up_date', 'salary_range', 'location', 'is_remote',
            'company_website', 'contact_person_name', 'contact_person_email',
            'cover_letter', 'resume_version', 'additional_documents'
        ]

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)
