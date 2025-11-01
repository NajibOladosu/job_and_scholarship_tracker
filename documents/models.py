"""
Document and ExtractedInformation models for the documents app.
"""
from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
import os


def user_document_path(instance, filename):
    """
    Generate file upload path: documents/user_<id>/<filename>
    """
    return f'documents/user_{instance.user.id}/{filename}'


class Document(models.Model):
    """
    Model for storing user-uploaded documents (resumes, transcripts, etc.).
    """

    DOCUMENT_TYPE_CHOICES = [
        ('resume', _('Resume')),
        ('transcript', _('Transcript')),
        ('certificate', _('Certificate')),
        ('other', _('Other')),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='documents',
        help_text=_('User who uploaded this document')
    )
    document_type = models.CharField(
        _('document type'),
        max_length=20,
        choices=DOCUMENT_TYPE_CHOICES,
        default='other',
        help_text=_('Type of document')
    )
    file = models.FileField(
        _('file'),
        upload_to=user_document_path,
        help_text=_('Upload document file')
    )
    original_filename = models.CharField(
        _('original filename'),
        max_length=255,
        help_text=_('Original name of the uploaded file')
    )
    uploaded_at = models.DateTimeField(
        _('uploaded at'),
        auto_now_add=True
    )
    file_size = models.PositiveIntegerField(
        _('file size'),
        help_text=_('File size in bytes'),
        null=True,
        blank=True
    )
    is_processed = models.BooleanField(
        _('is processed'),
        default=False,
        help_text=_('Whether the document has been processed for information extraction')
    )
    processed_at = models.DateTimeField(
        _('processed at'),
        null=True,
        blank=True,
        help_text=_('Timestamp when document was processed')
    )

    class Meta:
        verbose_name = _('document')
        verbose_name_plural = _('documents')
        ordering = ['-uploaded_at']
        indexes = [
            models.Index(fields=['user', 'document_type']),
            models.Index(fields=['is_processed']),
            models.Index(fields=['user', 'is_processed']),
        ]

    def __str__(self):
        return f"{self.get_document_type_display()} - {self.original_filename}"

    def save(self, *args, **kwargs):
        """
        Override save to store original filename and file size.
        """
        if self.file and not self.original_filename:
            self.original_filename = os.path.basename(self.file.name)
        if self.file and not self.file_size:
            self.file_size = self.file.size
        super().save(*args, **kwargs)

    @property
    def file_size_mb(self):
        """
        Return file size in megabytes.
        """
        if self.file_size:
            return round(self.file_size / (1024 * 1024), 2)
        return 0


class ExtractedInformation(models.Model):
    """
    Model for storing information extracted from documents using AI.
    """

    DATA_TYPE_CHOICES = [
        ('name', _('Name')),
        ('email', _('Email')),
        ('education', _('Education')),
        ('experience', _('Work Experience')),
        ('skills', _('Skills')),
        ('certifications', _('Certifications')),
    ]

    document = models.ForeignKey(
        Document,
        on_delete=models.CASCADE,
        related_name='extracted_info',
        help_text=_('Document from which information was extracted')
    )
    data_type = models.CharField(
        _('data type'),
        max_length=20,
        choices=DATA_TYPE_CHOICES,
        help_text=_('Type of extracted data')
    )
    content = models.JSONField(
        _('content'),
        help_text=_('Extracted information stored as JSON')
    )
    confidence_score = models.FloatField(
        _('confidence score'),
        default=0.0,
        help_text=_('Confidence score of the extraction (0.0 to 1.0)')
    )
    extracted_at = models.DateTimeField(
        _('extracted at'),
        auto_now_add=True
    )

    class Meta:
        verbose_name = _('extracted information')
        verbose_name_plural = _('extracted information')
        ordering = ['-extracted_at']
        indexes = [
            models.Index(fields=['document', 'data_type']),
            models.Index(fields=['data_type']),
        ]

    def __str__(self):
        return f"{self.get_data_type_display()} from {self.document.original_filename}"

    @property
    def confidence_percentage(self):
        """
        Return confidence score as a percentage.
        """
        return round(self.confidence_score * 100, 1)
