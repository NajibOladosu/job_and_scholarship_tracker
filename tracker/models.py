"""
Application tracking models for the tracker app.
"""
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

User = get_user_model()


class Application(models.Model):
    """
    Model for tracking job and scholarship applications.
    """

    APPLICATION_TYPE_CHOICES = [
        ('job', _('Job Application')),
        ('scholarship', _('Scholarship Application')),
    ]

    STATUS_CHOICES = [
        ('draft', _('Draft')),
        ('submitted', _('Submitted')),
        ('in_review', _('In Review')),
        ('interview', _('Interview')),
        ('offer', _('Offer')),
        ('rejected', _('Rejected')),
        ('withdrawn', _('Withdrawn')),
    ]

    PRIORITY_CHOICES = [
        ('high', _('High')),
        ('medium', _('Medium')),
        ('low', _('Low')),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='applications',
        help_text=_('User who created this application')
    )
    application_type = models.CharField(
        _('application type'),
        max_length=20,
        choices=APPLICATION_TYPE_CHOICES,
        help_text=_('Type of application (job or scholarship)')
    )
    title = models.CharField(
        _('title'),
        max_length=200,
        help_text=_('Job title or scholarship name')
    )
    company_or_institution = models.CharField(
        _('company or institution'),
        max_length=200,
        help_text=_('Company name or educational institution')
    )
    url = models.URLField(
        _('URL'),
        max_length=500,
        blank=True,
        help_text=_('Application URL or posting link')
    )
    description = models.TextField(
        _('description'),
        blank=True,
        help_text=_('Job or scholarship description')
    )
    deadline = models.DateTimeField(
        _('deadline'),
        null=True,
        blank=True,
        help_text=_('Application deadline')
    )
    status = models.CharField(
        _('status'),
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft',
        help_text=_('Current application status')
    )
    priority = models.CharField(
        _('priority'),
        max_length=10,
        choices=PRIORITY_CHOICES,
        default='medium',
        help_text=_('Application priority level')
    )
    created_at = models.DateTimeField(
        _('created at'),
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        _('updated at'),
        auto_now=True
    )
    submitted_at = models.DateTimeField(
        _('submitted at'),
        null=True,
        blank=True,
        help_text=_('Date and time when application was submitted')
    )
    notes = models.TextField(
        _('notes'),
        blank=True,
        help_text=_('Additional notes or comments')
    )
    is_archived = models.BooleanField(
        _('is archived'),
        default=False,
        help_text=_('Whether this application has been archived')
    )
    archived_at = models.DateTimeField(
        _('archived at'),
        null=True,
        blank=True,
        help_text=_('Date and time when application was archived')
    )
    tags = models.ManyToManyField(
        'Tag',
        blank=True,
        related_name='applications',
        verbose_name=_('tags'),
        help_text=_('Tags for organizing and categorizing applications')
    )

    class Meta:
        verbose_name = _('application')
        verbose_name_plural = _('applications')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['deadline']),
            models.Index(fields=['created_at']),
            models.Index(fields=['user', 'application_type']),
        ]

    def __str__(self):
        return f"{self.title} at {self.company_or_institution}"

    @property
    def is_overdue(self):
        """
        Check if application deadline has passed.
        """
        if self.deadline and self.status in ['draft', 'in_review']:
            return timezone.now() > self.deadline
        return False

    @property
    def days_until_deadline(self):
        """
        Calculate days remaining until deadline.
        """
        if self.deadline:
            delta = self.deadline - timezone.now()
            return delta.days
        return None

    @property
    def question_count(self):
        """
        Get the number of questions associated with this application.
        """
        return self.questions.count()


class Question(models.Model):
    """
    Model for storing application questions.
    """

    QUESTION_TYPE_CHOICES = [
        ('short_answer', _('Short Answer')),
        ('essay', _('Essay')),
        ('experience', _('Work Experience')),
        ('education', _('Education')),
        ('skills', _('Skills')),
        ('custom', _('Custom')),
    ]

    application = models.ForeignKey(
        Application,
        on_delete=models.CASCADE,
        related_name='questions',
        help_text=_('Application this question belongs to')
    )
    question_text = models.TextField(
        _('question text'),
        help_text=_('The question or prompt text')
    )
    question_type = models.CharField(
        _('question type'),
        max_length=20,
        choices=QUESTION_TYPE_CHOICES,
        default='custom',
        help_text=_('Type of question')
    )
    is_required = models.BooleanField(
        _('is required'),
        default=False,
        help_text=_('Whether this question is required')
    )
    is_extracted = models.BooleanField(
        _('is extracted'),
        default=False,
        help_text=_('Whether this question was auto-extracted from application')
    )
    order = models.PositiveIntegerField(
        _('order'),
        default=0,
        help_text=_('Display order of the question')
    )
    created_at = models.DateTimeField(
        _('created at'),
        auto_now_add=True
    )

    class Meta:
        verbose_name = _('question')
        verbose_name_plural = _('questions')
        ordering = ['application', 'order', 'created_at']
        indexes = [
            models.Index(fields=['application', 'order']),
        ]

    def __str__(self):
        return f"Q{self.order}: {self.question_text[:50]}..."


class Response(models.Model):
    """
    Model for storing responses to application questions.
    """

    question = models.OneToOneField(
        Question,
        on_delete=models.CASCADE,
        related_name='response',
        help_text=_('Question this response answers')
    )
    generated_response = models.TextField(
        _('generated response'),
        blank=True,
        help_text=_('AI-generated response text')
    )
    edited_response = models.TextField(
        _('edited response'),
        blank=True,
        null=True,
        help_text=_('User-edited version of the response')
    )
    is_ai_generated = models.BooleanField(
        _('is AI generated'),
        default=False,
        help_text=_('Whether response was generated by AI')
    )
    generation_prompt = models.TextField(
        _('generation prompt'),
        blank=True,
        help_text=_('Prompt used to generate AI response')
    )
    generated_at = models.DateTimeField(
        _('generated at'),
        null=True,
        blank=True,
        help_text=_('When AI response was generated')
    )
    last_edited_at = models.DateTimeField(
        _('last edited at'),
        null=True,
        blank=True,
        help_text=_('When response was last edited')
    )
    version = models.PositiveIntegerField(
        _('version'),
        default=1,
        help_text=_('Version number for tracking edits')
    )

    class Meta:
        verbose_name = _('response')
        verbose_name_plural = _('responses')
        ordering = ['question']

    def __str__(self):
        return f"Response to: {self.question.question_text[:30]}..."

    @property
    def final_response(self):
        """
        Get the final response (edited if available, otherwise generated).
        """
        return self.edited_response or self.generated_response

    def save(self, *args, **kwargs):
        """
        Override save to update version and timestamps.
        """
        if self.pk and self.edited_response:
            self.last_edited_at = timezone.now()
            self.version += 1
        super().save(*args, **kwargs)


class ApplicationStatus(models.Model):
    """
    Model for tracking application status changes over time.
    """

    STATUS_CHOICES = Application.STATUS_CHOICES

    CHANGED_BY_CHOICES = [
        ('manual', _('Manual Update')),
        ('ai_detected', _('AI Detected')),
        ('user_update', _('User Update')),
    ]

    application = models.ForeignKey(
        Application,
        on_delete=models.CASCADE,
        related_name='status_history',
        help_text=_('Application whose status changed')
    )
    status = models.CharField(
        _('status'),
        max_length=20,
        choices=STATUS_CHOICES,
        help_text=_('New status value')
    )
    changed_by = models.CharField(
        _('changed by'),
        max_length=20,
        choices=CHANGED_BY_CHOICES,
        default='manual',
        help_text=_('How the status was changed')
    )
    notes = models.TextField(
        _('notes'),
        blank=True,
        help_text=_('Notes about the status change')
    )
    created_at = models.DateTimeField(
        _('created at'),
        auto_now_add=True
    )

    class Meta:
        verbose_name = _('application status')
        verbose_name_plural = _('application statuses')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['application', '-created_at']),
        ]

    def __str__(self):
        return f"{self.application.title} - {self.get_status_display()} ({self.created_at.strftime('%Y-%m-%d')})"


class Tag(models.Model):
    """
    Model for organizing applications with custom tags.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='tags',
        help_text=_('User who created this tag')
    )
    name = models.CharField(
        _('name'),
        max_length=50,
        help_text=_('Tag name (e.g., Remote, High Salary, Dream Company)')
    )
    color = models.CharField(
        _('color'),
        max_length=7,
        default='#6366f1',
        help_text=_('Hex color code for the tag (e.g., #6366f1)')
    )
    created_at = models.DateTimeField(
        _('created at'),
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        _('updated at'),
        auto_now=True
    )

    class Meta:
        verbose_name = _('tag')
        verbose_name_plural = _('tags')
        ordering = ['name']
        unique_together = [['user', 'name']]
        indexes = [
            models.Index(fields=['user', 'name']),
        ]

    def __str__(self):
        return self.name

    @property
    def application_count(self):
        """
        Get the number of applications using this tag.
        """
        return self.applications.count()


class Note(models.Model):
    """
    Model for user notes (standalone or linked to applications).
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notes',
        help_text=_('User who created this note')
    )
    application = models.ForeignKey(
        Application,
        on_delete=models.CASCADE,
        related_name='notes_list',
        null=True,
        blank=True,
        help_text=_('Application this note is linked to (optional)')
    )
    title = models.CharField(
        _('title'),
        max_length=200,
        help_text=_('Note title')
    )
    content = models.TextField(
        _('content'),
        help_text=_('Rich text content (stored as HTML from Quill.js)')
    )
    plain_text = models.TextField(
        _('plain text'),
        blank=True,
        help_text=_('Plain text version for search')
    )
    is_pinned = models.BooleanField(
        _('is pinned'),
        default=False,
        help_text=_('Pin note to top of list')
    )
    created_at = models.DateTimeField(
        _('created at'),
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        _('updated at'),
        auto_now=True
    )

    class Meta:
        verbose_name = _('note')
        verbose_name_plural = _('notes')
        ordering = ['-is_pinned', '-updated_at']
        indexes = [
            models.Index(fields=['user', '-is_pinned', '-updated_at']),
            models.Index(fields=['application', '-updated_at']),
            models.Index(fields=['user', 'application']),
        ]

    def __str__(self):
        return self.title


class Interview(models.Model):
    """
    Model for tracking interviews for applications.
    """

    INTERVIEW_TYPE_CHOICES = [
        ('phone', _('Phone Interview')),
        ('video', _('Video Interview')),
        ('onsite', _('Onsite Interview')),
        ('panel', _('Panel Interview')),
    ]

    INTERVIEW_STATUS_CHOICES = [
        ('scheduled', _('Scheduled')),
        ('completed', _('Completed')),
        ('cancelled', _('Cancelled')),
        ('rescheduled', _('Rescheduled')),
    ]

    application = models.ForeignKey(
        Application,
        on_delete=models.CASCADE,
        related_name='interviews',
        help_text=_('Application this interview is for')
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='interviews',
        help_text=_('User who created this interview')
    )
    interview_type = models.CharField(
        _('interview type'),
        max_length=20,
        choices=INTERVIEW_TYPE_CHOICES,
        help_text=_('Type of interview')
    )
    scheduled_date = models.DateTimeField(
        _('scheduled date'),
        help_text=_('Date and time of the interview')
    )
    duration_minutes = models.PositiveIntegerField(
        _('duration (minutes)'),
        default=60,
        help_text=_('Expected duration of the interview in minutes')
    )
    location = models.TextField(
        _('location'),
        blank=True,
        help_text=_('Physical location for onsite interviews')
    )
    meeting_link = models.URLField(
        _('meeting link'),
        blank=True,
        max_length=500,
        help_text=_('Video conferencing link (Zoom, Google Meet, etc.)')
    )
    notes = models.TextField(
        _('notes'),
        blank=True,
        help_text=_('Notes about the interview (preparation, topics, feedback)')
    )
    status = models.CharField(
        _('status'),
        max_length=20,
        choices=INTERVIEW_STATUS_CHOICES,
        default='scheduled',
        help_text=_('Current status of the interview')
    )
    created_at = models.DateTimeField(
        _('created at'),
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        _('updated at'),
        auto_now=True
    )

    class Meta:
        verbose_name = _('interview')
        verbose_name_plural = _('interviews')
        ordering = ['scheduled_date']
        indexes = [
            models.Index(fields=['application', 'scheduled_date']),
            models.Index(fields=['user', 'scheduled_date']),
            models.Index(fields=['status', 'scheduled_date']),
        ]

    def __str__(self):
        return f"{self.get_interview_type_display()} - {self.application.title} ({self.scheduled_date.strftime('%Y-%m-%d %H:%M')})"

    @property
    def is_upcoming(self):
        """
        Check if interview is in the future.
        """
        return self.scheduled_date > timezone.now() and self.status == 'scheduled'

    @property
    def is_past(self):
        """
        Check if interview is in the past.
        """
        return self.scheduled_date < timezone.now()


class Interviewer(models.Model):
    """
    Model for storing information about interviewers.
    """

    interview = models.ForeignKey(
        Interview,
        on_delete=models.CASCADE,
        related_name='interviewers',
        help_text=_('Interview this person is conducting')
    )
    name = models.CharField(
        _('name'),
        max_length=200,
        help_text=_('Full name of the interviewer')
    )
    title = models.CharField(
        _('title'),
        max_length=200,
        help_text=_('Job title/position of the interviewer')
    )
    email = models.EmailField(
        _('email'),
        blank=True,
        help_text=_('Email address of the interviewer')
    )
    phone = models.CharField(
        _('phone'),
        max_length=20,
        blank=True,
        help_text=_('Phone number of the interviewer')
    )
    linkedin_url = models.URLField(
        _('LinkedIn URL'),
        blank=True,
        max_length=500,
        help_text=_('LinkedIn profile URL')
    )
    notes = models.TextField(
        _('notes'),
        blank=True,
        help_text=_('Additional notes about the interviewer')
    )
    created_at = models.DateTimeField(
        _('created at'),
        auto_now_add=True
    )

    class Meta:
        verbose_name = _('interviewer')
        verbose_name_plural = _('interviewers')
        ordering = ['name']

    def __str__(self):
        return f"{self.name} - {self.title}"


class Referral(models.Model):
    """
    Model for tracking referrals for applications.
    """

    application = models.ForeignKey(
        Application,
        on_delete=models.CASCADE,
        related_name='referrals',
        help_text=_('Application this referral is for')
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='referrals',
        help_text=_('User who received this referral')
    )
    name = models.CharField(
        _('name'),
        max_length=200,
        help_text=_('Name of the person providing the referral')
    )
    relationship = models.CharField(
        _('relationship'),
        max_length=200,
        help_text=_('Your relationship to the referrer (e.g., former colleague, friend, mentor)')
    )
    company = models.CharField(
        _('company'),
        max_length=200,
        help_text=_('Company where the referrer works')
    )
    email = models.EmailField(
        _('email'),
        help_text=_('Email address of the referrer')
    )
    phone = models.CharField(
        _('phone'),
        max_length=20,
        blank=True,
        help_text=_('Phone number of the referrer')
    )
    referred_date = models.DateField(
        _('referred date'),
        help_text=_('Date when the referral was made')
    )
    notes = models.TextField(
        _('notes'),
        blank=True,
        help_text=_('Additional notes about the referral')
    )
    created_at = models.DateTimeField(
        _('created at'),
        auto_now_add=True
    )

    class Meta:
        verbose_name = _('referral')
        verbose_name_plural = _('referrals')
        ordering = ['-referred_date']
        indexes = [
            models.Index(fields=['application', '-referred_date']),
            models.Index(fields=['user', '-referred_date']),
        ]

    def __str__(self):
        return f"Referral from {self.name} for {self.application.title}"
