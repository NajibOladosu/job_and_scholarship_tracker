"""
Reminder and Notification models for the notifications app.
"""
from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone


class ReminderManager(models.Manager):
    """
    Custom manager for Reminder model.
    """
    def pending(self):
        """
        Get reminders that haven't been sent yet.
        """
        return self.filter(is_sent=False, scheduled_for__lte=timezone.now())

    def upcoming(self, hours=24):
        """
        Get reminders scheduled within the next X hours.
        """
        now = timezone.now()
        future = now + timezone.timedelta(hours=hours)
        return self.filter(is_sent=False, scheduled_for__range=[now, future])


class Reminder(models.Model):
    """
    Model for scheduling reminders about applications.
    """

    REMINDER_TYPE_CHOICES = [
        ('deadline', _('Deadline Reminder')),
        ('follow_up', _('Follow-up Reminder')),
        ('interview', _('Interview Reminder')),
        ('custom', _('Custom Reminder')),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reminders',
        help_text=_('User to be reminded')
    )
    application = models.ForeignKey(
        'tracker.Application',
        on_delete=models.CASCADE,
        related_name='reminders',
        help_text=_('Application this reminder is for')
    )
    reminder_type = models.CharField(
        _('reminder type'),
        max_length=20,
        choices=REMINDER_TYPE_CHOICES,
        default='custom',
        help_text=_('Type of reminder')
    )
    message = models.TextField(
        _('message'),
        help_text=_('Reminder message text')
    )
    scheduled_for = models.DateTimeField(
        _('scheduled for'),
        help_text=_('When to send this reminder')
    )
    is_sent = models.BooleanField(
        _('is sent'),
        default=False,
        help_text=_('Whether reminder has been sent')
    )
    sent_at = models.DateTimeField(
        _('sent at'),
        null=True,
        blank=True,
        help_text=_('When reminder was sent')
    )
    created_at = models.DateTimeField(
        _('created at'),
        auto_now_add=True
    )

    objects = ReminderManager()

    class Meta:
        verbose_name = _('reminder')
        verbose_name_plural = _('reminders')
        ordering = ['scheduled_for']
        indexes = [
            models.Index(fields=['user', 'is_sent']),
            models.Index(fields=['scheduled_for']),
            models.Index(fields=['is_sent', 'scheduled_for']),
        ]

    def __str__(self):
        return f"{self.get_reminder_type_display()} for {self.application.title}"

    @property
    def is_overdue(self):
        """
        Check if reminder time has passed without being sent.
        """
        return not self.is_sent and timezone.now() > self.scheduled_for

    def mark_as_sent(self):
        """
        Mark reminder as sent with current timestamp.
        """
        self.is_sent = True
        self.sent_at = timezone.now()
        self.save(update_fields=['is_sent', 'sent_at'])


class NotificationManager(models.Manager):
    """
    Custom manager for Notification model.
    """
    def unread(self):
        """
        Get unread notifications.
        """
        return self.filter(is_read=False)

    def recent(self, days=7):
        """
        Get notifications from the last X days.
        """
        cutoff = timezone.now() - timezone.timedelta(days=days)
        return self.filter(created_at__gte=cutoff)


class Notification(models.Model):
    """
    Model for user notifications.
    """

    NOTIFICATION_TYPE_CHOICES = [
        ('reminder', _('Reminder')),
        ('status_change', _('Status Change')),
        ('system', _('System Notification')),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications',
        help_text=_('User to notify')
    )
    notification_type = models.CharField(
        _('notification type'),
        max_length=20,
        choices=NOTIFICATION_TYPE_CHOICES,
        help_text=_('Type of notification')
    )
    title = models.CharField(
        _('title'),
        max_length=200,
        help_text=_('Notification title')
    )
    message = models.TextField(
        _('message'),
        help_text=_('Notification message content')
    )
    link = models.URLField(
        _('link'),
        max_length=500,
        blank=True,
        null=True,
        help_text=_('Optional link related to notification')
    )
    is_read = models.BooleanField(
        _('is read'),
        default=False,
        help_text=_('Whether notification has been read')
    )
    created_at = models.DateTimeField(
        _('created at'),
        auto_now_add=True
    )
    read_at = models.DateTimeField(
        _('read at'),
        null=True,
        blank=True,
        help_text=_('When notification was read')
    )

    objects = NotificationManager()

    class Meta:
        verbose_name = _('notification')
        verbose_name_plural = _('notifications')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_read']),
            models.Index(fields=['user', '-created_at']),
        ]

    def __str__(self):
        return f"{self.title} for {self.user.email}"

    def mark_as_read(self):
        """
        Mark notification as read with current timestamp.
        """
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save(update_fields=['is_read', 'read_at'])

    @property
    def time_since_created(self):
        """
        Get human-readable time since notification was created.
        """
        delta = timezone.now() - self.created_at
        if delta.days > 0:
            return f"{delta.days} day{'s' if delta.days != 1 else ''} ago"
        elif delta.seconds > 3600:
            hours = delta.seconds // 3600
            return f"{hours} hour{'s' if hours != 1 else ''} ago"
        elif delta.seconds > 60:
            minutes = delta.seconds // 60
            return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
        else:
            return "just now"
