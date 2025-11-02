"""
Admin configuration for documents app models.
"""
from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from .models import Document, ExtractedInformation


class ExtractedInformationInline(admin.TabularInline):
    """
    Inline admin for extracted information within document.
    """
    model = ExtractedInformation
    extra = 0
    fields = ('data_type', 'content', 'confidence_percentage', 'extracted_at')
    readonly_fields = ('extracted_at', 'confidence_percentage')


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    """
    Admin interface for Document model.
    """
    list_display = (
        'original_filename', 'user', 'document_type',
        'file_size_display', 'is_processed', 'uploaded_at', 'info_count'
    )
    list_filter = ('document_type', 'is_processed', 'uploaded_at')
    search_fields = ('original_filename', 'user__email', 'user__first_name', 'user__last_name')
    readonly_fields = ('uploaded_at', 'processed_at', 'file_size', 'file_size_mb')
    date_hierarchy = 'uploaded_at'
    inlines = [ExtractedInformationInline]

    fieldsets = (
        (_('Document Information'), {
            'fields': ('user', 'document_type', 'file', 'original_filename')
        }),
        (_('Processing Status'), {
            'fields': ('is_processed', 'processed_at')
        }),
        (_('File Details'), {
            'fields': ('file_size', 'file_size_mb', 'uploaded_at'),
            'classes': ('collapse',)
        }),
    )

    def file_size_display(self, obj):
        """Display file size in human-readable format."""
        if obj.file_size_mb >= 1:
            return f"{obj.file_size_mb} MB"
        elif obj.file_size:
            return f"{round(obj.file_size / 1024, 1)} KB"
        return "0 KB"
    file_size_display.short_description = _('File Size')

    def info_count(self, obj):
        """Get number of extracted information records."""
        return obj.extracted_info.count()
    info_count.short_description = _('Extracted Info')

    def get_queryset(self, request):
        """Optimize queryset."""
        return super().get_queryset(request).select_related('user')


@admin.register(ExtractedInformation)
class ExtractedInformationAdmin(admin.ModelAdmin):
    """
    Admin interface for ExtractedInformation model.
    """
    list_display = (
        'data_type', 'document_link', 'user', 'confidence_percentage',
        'content_preview', 'extracted_at'
    )
    list_filter = ('data_type', 'extracted_at', 'document__document_type')
    search_fields = ('document__original_filename', 'document__user__email', 'content')
    readonly_fields = ('extracted_at', 'confidence_percentage')

    fieldsets = (
        (_('Source'), {
            'fields': ('document',)
        }),
        (_('Extracted Data'), {
            'fields': ('data_type', 'content', 'confidence_score', 'confidence_percentage')
        }),
        (_('Metadata'), {
            'fields': ('extracted_at',),
            'classes': ('collapse',)
        }),
    )

    def document_link(self, obj):
        """Return link to document."""
        return format_html(
            '<a href="/admin/documents/document/{}/change/">{}</a>',
            obj.document.id,
            obj.document.original_filename
        )
    document_link.short_description = _('Document')

    def user(self, obj):
        """Get document owner."""
        return obj.document.user
    user.short_description = _('User')

    def content_preview(self, obj):
        """Show preview of extracted content."""
        content_str = str(obj.content)
        return content_str[:100] + '...' if len(content_str) > 100 else content_str
    content_preview.short_description = _('Content Preview')

    def get_queryset(self, request):
        """Optimize queryset."""
        return super().get_queryset(request).select_related('document', 'document__user')
