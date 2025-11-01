"""
Celery tasks for notifications and reminders.

This module contains background tasks for checking due reminders,
sending notifications, and managing reminder schedules.
"""
import logging
from typing import Dict, List
from datetime import timedelta

from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.html import strip_tags

from core.tasks import BaseTask, TaskStatusTracker
from notifications.models import Reminder, Notification
from tracker.models import Application

logger = logging.getLogger(__name__)


@shared_task(base=BaseTask, bind=True)
def check_due_reminders_task(self) -> Dict[str, any]:
    """
    Check for due reminders and send them.

    This task should be run periodically (via Celery Beat) to check for
    reminders that are due and trigger the sending process.

    Returns:
        Dict containing check results and statistics

    Example:
        # Usually scheduled via Celery Beat, but can be called manually
        result = check_due_reminders_task.delay()
    """
    tracker = TaskStatusTracker()
    tracker.log_start(self.name, self.request.id)

    try:
        # Get all pending reminders that are due
        due_reminders = Reminder.objects.pending()
        reminder_count = due_reminders.count()

        logger.info(f"Found {reminder_count} due reminders to process")

        sent_count = 0
        failed_count = 0
        notification_task_ids = []

        for reminder in due_reminders:
            try:
                # Create notification for the reminder
                notification = Notification.objects.create(
                    user=reminder.user,
                    notification_type='reminder',
                    title=f"{reminder.get_reminder_type_display()}: {reminder.application.title}",
                    message=reminder.message,
                    link=f"/applications/{reminder.application.id}/"  # TODO: Use reverse URL
                )

                # Send notification email asynchronously
                task_result = send_notification_email_task.delay(notification.id)
                notification_task_ids.append(task_result.id)

                # Mark reminder as sent
                reminder.mark_as_sent()
                sent_count += 1

                logger.info(f"Sent reminder {reminder.id} for application {reminder.application.id}")

            except Exception as e:
                failed_count += 1
                logger.error(f"Failed to send reminder {reminder.id}: {e}", exc_info=True)

        result = {
            'status': 'success',
            'checked_at': timezone.now().isoformat(),
            'total_due': reminder_count,
            'sent': sent_count,
            'failed': failed_count,
            'notification_task_ids': notification_task_ids
        }

        tracker.log_completion(self.name, self.request.id, **result)
        return result

    except Exception as e:
        logger.error(f"Error checking due reminders: {e}", exc_info=True)
        raise


@shared_task(base=BaseTask, bind=True, max_retries=3)
def create_deadline_reminders_task(self, application_id: int, custom_intervals: List[int] = None) -> Dict[str, any]:
    """
    Create automatic deadline reminders for an application.

    Creates multiple reminders at different intervals before the deadline
    (e.g., 1 week before, 3 days before, 1 day before).

    Args:
        application_id: ID of the Application
        custom_intervals: Optional list of days before deadline to create reminders
                         (default: [7, 3, 1] for 1 week, 3 days, 1 day)

    Returns:
        Dict containing created reminders information

    Example:
        # Create default reminders (7, 3, 1 days before)
        result = create_deadline_reminders_task.delay(application_id=123)

        # Create custom interval reminders
        result = create_deadline_reminders_task.delay(
            application_id=123,
            custom_intervals=[14, 7, 3, 1]  # 2 weeks, 1 week, 3 days, 1 day
        )
    """
    tracker = TaskStatusTracker()
    tracker.log_start(self.name, self.request.id, application_id=application_id)

    try:
        application = Application.objects.select_related('user').get(id=application_id)

        if not application.deadline:
            logger.warning(f"Application {application_id} has no deadline set")
            return {
                'status': 'skipped',
                'application_id': application_id,
                'message': 'No deadline set for application'
            }

        # Default reminder intervals (days before deadline)
        intervals = custom_intervals or [7, 3, 1]
        now = timezone.now()

        created_reminders = []

        for days_before in intervals:
            reminder_time = application.deadline - timedelta(days=days_before)

            # Only create reminder if it's in the future
            if reminder_time > now:
                # Check if reminder already exists
                existing = Reminder.objects.filter(
                    application=application,
                    reminder_type='deadline',
                    scheduled_for=reminder_time
                ).exists()

                if not existing:
                    message = (
                        f"Reminder: Your application for {application.title} at "
                        f"{application.company_or_institution} is due in {days_before} day{'s' if days_before != 1 else ''}. "
                        f"Deadline: {application.deadline.strftime('%Y-%m-%d %H:%M')}"
                    )

                    reminder = Reminder.objects.create(
                        user=application.user,
                        application=application,
                        reminder_type='deadline',
                        message=message,
                        scheduled_for=reminder_time
                    )

                    created_reminders.append({
                        'id': reminder.id,
                        'days_before': days_before,
                        'scheduled_for': reminder_time.isoformat()
                    })

                    logger.info(f"Created deadline reminder for application {application_id}, {days_before} days before")

        result = {
            'status': 'success',
            'application_id': application_id,
            'deadline': application.deadline.isoformat(),
            'reminders_created': len(created_reminders),
            'reminders': created_reminders
        }

        tracker.log_completion(self.name, self.request.id, **result)
        return result

    except Application.DoesNotExist:
        logger.error(f"Application with id {application_id} does not exist")
        raise
    except Exception as e:
        logger.error(f"Error creating deadline reminders for application {application_id}: {e}", exc_info=True)
        raise


@shared_task(base=BaseTask, bind=True, max_retries=3)
def send_notification_email_task(self, notification_id: int) -> Dict[str, any]:
    """
    Send email for a notification.

    This task sends an email to the user about a notification.
    Uses Django's email backend configured in settings.

    Args:
        notification_id: ID of the Notification to send

    Returns:
        Dict containing email sending results

    Example:
        # Send notification email
        result = send_notification_email_task.delay(notification_id=789)
    """
    tracker = TaskStatusTracker()
    tracker.log_start(self.name, self.request.id, notification_id=notification_id)

    try:
        notification = Notification.objects.select_related('user').get(id=notification_id)
        user = notification.user

        # Skip sending if user has no email
        if not user.email:
            logger.warning(f"User {user.id} has no email address")
            return {
                'status': 'skipped',
                'notification_id': notification_id,
                'message': 'User has no email address'
            }

        # TODO: Use email template for better formatting
        # For now, use simple text email
        subject = f"[Job Tracker] {notification.title}"

        # Try to render HTML template if it exists
        try:
            html_message = render_to_string('notifications/email/notification.html', {
                'notification': notification,
                'user': user,
            })
            plain_message = strip_tags(html_message)
        except Exception:
            # Fallback to plain text if template doesn't exist
            plain_message = notification.message
            html_message = None

        # Send email
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )

        logger.info(f"Sent notification email to {user.email} for notification {notification_id}")

        result = {
            'status': 'success',
            'notification_id': notification_id,
            'recipient': user.email,
            'sent_at': timezone.now().isoformat()
        }

        tracker.log_completion(self.name, self.request.id, **result)
        return result

    except Notification.DoesNotExist:
        logger.error(f"Notification with id {notification_id} does not exist")
        raise
    except Exception as e:
        logger.error(f"Error sending notification email {notification_id}: {e}", exc_info=True)
        # Retry the task with exponential backoff
        raise self.retry(exc=e, countdown=60 * (2 ** self.request.retries))


@shared_task(base=BaseTask, bind=True)
def create_custom_reminder_task(
    self,
    user_id: int,
    application_id: int,
    message: str,
    scheduled_for: str,
    reminder_type: str = 'custom'
) -> Dict[str, any]:
    """
    Create a custom reminder for a user.

    Args:
        user_id: ID of the User
        application_id: ID of the Application
        message: Reminder message
        scheduled_for: ISO format datetime string for when to send reminder
        reminder_type: Type of reminder (default: 'custom')

    Returns:
        Dict containing created reminder information

    Example:
        # Create custom reminder
        result = create_custom_reminder_task.delay(
            user_id=1,
            application_id=123,
            message="Follow up with hiring manager",
            scheduled_for="2025-11-15T10:00:00Z",
            reminder_type="follow_up"
        )
    """
    from django.contrib.auth import get_user_model

    tracker = TaskStatusTracker()
    tracker.log_start(self.name, self.request.id, application_id=application_id)

    try:
        User = get_user_model()
        user = User.objects.get(id=user_id)
        application = Application.objects.get(id=application_id)

        # Parse scheduled_for datetime
        from dateutil import parser
        scheduled_datetime = parser.parse(scheduled_for)

        # Create reminder
        reminder = Reminder.objects.create(
            user=user,
            application=application,
            reminder_type=reminder_type,
            message=message,
            scheduled_for=scheduled_datetime
        )

        result = {
            'status': 'success',
            'reminder_id': reminder.id,
            'application_id': application_id,
            'scheduled_for': reminder.scheduled_for.isoformat()
        }

        tracker.log_completion(self.name, self.request.id, **result)
        return result

    except Exception as e:
        logger.error(f"Error creating custom reminder: {e}", exc_info=True)
        raise


@shared_task(base=BaseTask, bind=True)
def cleanup_old_notifications_task(self, days: int = 30) -> Dict[str, any]:
    """
    Clean up old read notifications.

    This task removes old notifications that have been read to keep
    the database clean. Unread notifications are never deleted.

    Args:
        days: Number of days after which to delete read notifications (default: 30)

    Returns:
        Dict containing cleanup statistics

    Example:
        # Clean up notifications older than 30 days
        result = cleanup_old_notifications_task.delay(days=30)
    """
    tracker = TaskStatusTracker()
    tracker.log_start(self.name, self.request.id, days=days)

    try:
        cutoff_date = timezone.now() - timedelta(days=days)

        # Only delete read notifications
        old_notifications = Notification.objects.filter(
            is_read=True,
            read_at__lt=cutoff_date
        )

        count = old_notifications.count()
        deleted_count, _ = old_notifications.delete()

        logger.info(f"Deleted {deleted_count} old notifications")

        result = {
            'status': 'success',
            'cutoff_date': cutoff_date.isoformat(),
            'notifications_deleted': deleted_count
        }

        tracker.log_completion(self.name, self.request.id, **result)
        return result

    except Exception as e:
        logger.error(f"Error cleaning up old notifications: {e}", exc_info=True)
        raise


@shared_task(base=BaseTask, bind=True)
def cleanup_old_reminders_task(self, days: int = 90) -> Dict[str, any]:
    """
    Clean up old sent reminders.

    This task removes old reminders that have been sent to keep
    the database clean. Pending reminders are never deleted.

    Args:
        days: Number of days after which to delete sent reminders (default: 90)

    Returns:
        Dict containing cleanup statistics

    Example:
        # Clean up reminders older than 90 days
        result = cleanup_old_reminders_task.delay(days=90)
    """
    tracker = TaskStatusTracker()
    tracker.log_start(self.name, self.request.id, days=days)

    try:
        cutoff_date = timezone.now() - timedelta(days=days)

        # Only delete sent reminders
        old_reminders = Reminder.objects.filter(
            is_sent=True,
            sent_at__lt=cutoff_date
        )

        count = old_reminders.count()
        deleted_count, _ = old_reminders.delete()

        logger.info(f"Deleted {deleted_count} old reminders")

        result = {
            'status': 'success',
            'cutoff_date': cutoff_date.isoformat(),
            'reminders_deleted': deleted_count
        }

        tracker.log_completion(self.name, self.request.id, **result)
        return result

    except Exception as e:
        logger.error(f"Error cleaning up old reminders: {e}", exc_info=True)
        raise


@shared_task(base=BaseTask, bind=True)
def send_digest_email_task(self, user_id: int, frequency: str = 'daily') -> Dict[str, any]:
    """
    Send a digest email to a user with their recent notifications and upcoming deadlines.

    Args:
        user_id: ID of the User
        frequency: Digest frequency ('daily' or 'weekly')

    Returns:
        Dict containing digest email results

    Example:
        # Send daily digest
        result = send_digest_email_task.delay(user_id=1, frequency='daily')
    """
    from django.contrib.auth import get_user_model

    tracker = TaskStatusTracker()
    tracker.log_start(self.name, self.request.id, user_id=user_id)

    try:
        User = get_user_model()
        user = User.objects.get(id=user_id)

        if not user.email:
            logger.warning(f"User {user_id} has no email address")
            return {
                'status': 'skipped',
                'user_id': user_id,
                'message': 'User has no email address'
            }

        # Get time range based on frequency
        if frequency == 'daily':
            since = timezone.now() - timedelta(days=1)
        else:  # weekly
            since = timezone.now() - timedelta(days=7)

        # Get recent notifications
        recent_notifications = Notification.objects.filter(
            user=user,
            created_at__gte=since
        ).order_by('-created_at')[:10]

        # Get upcoming reminders
        upcoming_reminders = Reminder.objects.filter(
            user=user,
            is_sent=False,
            scheduled_for__lte=timezone.now() + timedelta(days=7)
        ).order_by('scheduled_for')[:5]

        # Get applications with upcoming deadlines
        upcoming_deadlines = Application.objects.filter(
            user=user,
            deadline__isnull=False,
            deadline__gte=timezone.now(),
            deadline__lte=timezone.now() + timedelta(days=7),
            status__in=['draft', 'in_review']
        ).order_by('deadline')[:5]

        # TODO: Render email template with digest information
        # For now, just log that we would send it
        logger.info(
            f"Would send {frequency} digest to {user.email} with "
            f"{recent_notifications.count()} notifications, "
            f"{upcoming_reminders.count()} reminders, "
            f"{upcoming_deadlines.count()} deadlines"
        )

        # TODO: Actually send the email
        # subject = f"Your {frequency.capitalize()} Application Digest"
        # html_message = render_to_string('notifications/email/digest.html', {
        #     'user': user,
        #     'notifications': recent_notifications,
        #     'reminders': upcoming_reminders,
        #     'deadlines': upcoming_deadlines,
        #     'frequency': frequency,
        # })
        # send_mail(...)

        result = {
            'status': 'success',
            'user_id': user_id,
            'frequency': frequency,
            'notifications_count': recent_notifications.count(),
            'reminders_count': upcoming_reminders.count(),
            'deadlines_count': upcoming_deadlines.count(),
        }

        tracker.log_completion(self.name, self.request.id, **result)
        return result

    except Exception as e:
        logger.error(f"Error sending digest email to user {user_id}: {e}", exc_info=True)
        raise
