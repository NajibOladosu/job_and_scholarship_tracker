"""
Admin configuration for tracker app models.
"""
from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.db.models import Count
from .models import Application, Question, Response, ApplicationStatus


class QuestionInline(admin.TabularInline):
    """
    Inline admin for questions within application.
    """
    model = Question
    extra = 0
    fields = ('question_text', 'question_type', 'is_required', 'is_extracted', 'order')
    readonly_fields = ('is_extracted',)
    ordering = ('order', 'created_at')


class ApplicationStatusInline(admin.TabularInline):
    """
    Inline admin for application status history.
    """
    model = ApplicationStatus
    extra = 0
    fields = ('status', 'changed_by', 'notes', 'created_at')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    """
    Admin interface for Application model.
    """
    list_display = (
        'title', 'user', 'company_or_institution', 'application_type',
        'status', 'priority', 'deadline', 'question_count', 'created_at'
    )
    list_filter = ('application_type', 'status', 'priority', 'created_at', 'deadline')
    search_fields = ('title', 'company_or_institution', 'description', 'user__email', 'user__first_name', 'user__last_name')
    readonly_fields = ('created_at', 'updated_at', 'submitted_at', 'is_overdue', 'days_until_deadline')
    date_hierarchy = 'created_at'
    inlines = [QuestionInline, ApplicationStatusInline]

    fieldsets = (
        (_('Basic Information'), {
            'fields': ('user', 'application_type', 'title', 'company_or_institution', 'url')
        }),
        (_('Details'), {
            'fields': ('description', 'deadline', 'status', 'priority', 'notes')
        }),
        (_('Metadata'), {
            'fields': ('created_at', 'updated_at', 'submitted_at', 'is_overdue', 'days_until_deadline'),
            'classes': ('collapse',)
        }),
    )

    def question_count(self, obj):
        """Get number of questions for this application."""
        return obj.questions.count()
    question_count.short_description = _('Questions')
    question_count.admin_order_field = 'question_count'

    def get_queryset(self, request):
        """Optimize queryset with annotations."""
        qs = super().get_queryset(request)
        return qs.select_related('user').annotate(question_count=Count('questions'))


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    """
    Admin interface for Question model.
    """
    list_display = (
        'short_question', 'application', 'question_type',
        'is_required', 'is_extracted', 'has_response', 'order', 'created_at'
    )
    list_filter = ('question_type', 'is_required', 'is_extracted', 'created_at')
    search_fields = ('question_text', 'application__title', 'application__company_or_institution')
    readonly_fields = ('created_at',)

    fieldsets = (
        (_('Question'), {
            'fields': ('application', 'question_text', 'question_type')
        }),
        (_('Settings'), {
            'fields': ('is_required', 'is_extracted', 'order')
        }),
        (_('Metadata'), {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

    def short_question(self, obj):
        """Return shortened question text."""
        return obj.question_text[:75] + '...' if len(obj.question_text) > 75 else obj.question_text
    short_question.short_description = _('Question')

    def has_response(self, obj):
        """Check if question has a response."""
        return hasattr(obj, 'response')
    has_response.boolean = True
    has_response.short_description = _('Has Response')

    def get_queryset(self, request):
        """Optimize queryset."""
        return super().get_queryset(request).select_related('application', 'application__user')


@admin.register(Response)
class ResponseAdmin(admin.ModelAdmin):
    """
    Admin interface for Response model.
    """
    list_display = (
        'short_question', 'application', 'is_ai_generated',
        'version', 'generated_at', 'last_edited_at', 'response_length'
    )
    list_filter = ('is_ai_generated', 'generated_at', 'last_edited_at')
    search_fields = (
        'question__question_text', 'question__application__title',
        'generated_response', 'edited_response'
    )
    readonly_fields = ('generated_at', 'last_edited_at', 'version', 'generation_prompt')

    fieldsets = (
        (_('Question'), {
            'fields': ('question',)
        }),
        (_('Generated Response'), {
            'fields': ('generated_response', 'is_ai_generated', 'generation_prompt', 'generated_at')
        }),
        (_('Edited Response'), {
            'fields': ('edited_response', 'last_edited_at', 'version')
        }),
    )

    def short_question(self, obj):
        """Return shortened question text."""
        text = obj.question.question_text
        return text[:50] + '...' if len(text) > 50 else text
    short_question.short_description = _('Question')

    def application(self, obj):
        """Get application title."""
        return obj.question.application.title
    application.short_description = _('Application')

    def response_length(self, obj):
        """Get length of final response."""
        response = obj.final_response
        return len(response) if response else 0
    response_length.short_description = _('Length')

    def get_queryset(self, request):
        """Optimize queryset."""
        return super().get_queryset(request).select_related(
            'question', 'question__application', 'question__application__user'
        )


@admin.register(ApplicationStatus)
class ApplicationStatusAdmin(admin.ModelAdmin):
    """
    Admin interface for ApplicationStatus model.
    """
    list_display = ('application', 'status', 'changed_by', 'created_at')
    list_filter = ('status', 'changed_by', 'created_at')
    search_fields = ('application__title', 'application__company_or_institution', 'notes')
    readonly_fields = ('created_at',)
    date_hierarchy = 'created_at'

    fieldsets = (
        (_('Status Change'), {
            'fields': ('application', 'status', 'changed_by')
        }),
        (_('Details'), {
            'fields': ('notes', 'created_at')
        }),
    )

    def get_queryset(self, request):
        """Optimize queryset."""
        return super().get_queryset(request).select_related('application', 'application__user')
