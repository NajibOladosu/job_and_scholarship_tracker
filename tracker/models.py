"""
Application tracking models for the tracker app.
"""
from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone


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
