"""
Admin configuration for notifications app models.
"""
from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from .models import Reminder, Notification


@admin.register(Reminder)
class ReminderAdmin(admin.ModelAdmin):
    """
    Admin interface for Reminder model.
    """
    list_display = (
        'short_message', 'user', 'application', 'reminder_type',
        'scheduled_for', 'is_sent', 'is_overdue_display', 'sent_at'
    )
    list_filter = ('reminder_type', 'is_sent', 'scheduled_for', 'created_at')
    search_fields = ('message', 'user__email', 'application__title', 'application__company_or_institution')
    readonly_fields = ('created_at', 'sent_at', 'is_overdue')
    date_hierarchy = 'scheduled_for'
    actions = ['mark_as_sent', 'mark_as_pending']

    fieldsets = (
        (_('Reminder Details'), {
            'fields': ('user', 'application', 'reminder_type', 'message')
        }),
        (_('Scheduling'), {
            'fields': ('scheduled_for', 'is_sent', 'sent_at')
        }),
        (_('Metadata'), {
            'fields': ('created_at', 'is_overdue'),
            'classes': ('collapse',)
        }),
    )

    def short_message(self, obj):
        """Display shortened message."""
        return obj.message[:75] + '...' if len(obj.message) > 75 else obj.message
    short_message.short_description = _('Message')

    def is_overdue_display(self, obj):
        """Display if reminder is overdue."""
        return obj.is_overdue
    is_overdue_display.boolean = True
    is_overdue_display.short_description = _('Overdue')

    def mark_as_sent(self, request, queryset):
        """Mark selected reminders as sent."""
        count = 0
        for reminder in queryset.filter(is_sent=False):
            reminder.mark_as_sent()
            count += 1
        self.message_user(request, f'{count} reminder(s) marked as sent.')
    mark_as_sent.short_description = _('Mark selected reminders as sent')

    def mark_as_pending(self, request, queryset):
        """Mark selected reminders as pending (not sent)."""
        count = queryset.update(is_sent=False, sent_at=None)
        self.message_user(request, f'{count} reminder(s) marked as pending.')
    mark_as_pending.short_description = _('Mark selected reminders as pending')

    def get_queryset(self, request):
        """Optimize queryset."""
        return super().get_queryset(request).select_related('user', 'application')


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    """
    Admin interface for Notification model.
    """
    list_display = (
        'title', 'user', 'notification_type', 'is_read',
        'created_at', 'time_since', 'read_at'
    )
    list_filter = ('notification_type', 'is_read', 'created_at')
    search_fields = ('title', 'message', 'user__email')
    readonly_fields = ('created_at', 'read_at', 'time_since_created')
    date_hierarchy = 'created_at'
    actions = ['mark_as_read', 'mark_as_unread']

    fieldsets = (
        (_('Notification'), {
            'fields': ('user', 'notification_type', 'title', 'message', 'link')
        }),
        (_('Status'), {
            'fields': ('is_read', 'read_at')
        }),
        (_('Metadata'), {
            'fields': ('created_at', 'time_since_created'),
            'classes': ('collapse',)
        }),
    )

    def time_since(self, obj):
        """Display time since notification was created."""
        return obj.time_since_created
    time_since.short_description = _('Time Since Created')

    def mark_as_read(self, request, queryset):
        """Mark selected notifications as read."""
        count = 0
        for notification in queryset.filter(is_read=False):
            notification.mark_as_read()
            count += 1
        self.message_user(request, f'{count} notification(s) marked as read.')
    mark_as_read.short_description = _('Mark selected notifications as read')

    def mark_as_unread(self, request, queryset):
        """Mark selected notifications as unread."""
        count = queryset.update(is_read=False, read_at=None)
        self.message_user(request, f'{count} notification(s) marked as unread.')
    mark_as_unread.short_description = _('Mark selected notifications as unread')

    def get_queryset(self, request):
        """Optimize queryset."""
        return super().get_queryset(request).select_related('user')
