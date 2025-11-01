"""
Celery tasks for user account management.

This module contains background tasks for email verification,
user account cleanup, and other account-related operations.
"""
import logging
from typing import Dict
from datetime import timedelta

from celery import shared_task
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.html import strip_tags
from django.utils.crypto import get_random_string

from core.tasks import BaseTask, TaskStatusTracker

User = get_user_model()
logger = logging.getLogger(__name__)


@shared_task(base=BaseTask, bind=True, max_retries=3)
def send_verification_email_task(self, user_id: int) -> Dict[str, any]:
    """
    Send email verification link to a user.

    This task generates a verification token and sends an email with
    a verification link to the user.

    Args:
        user_id: ID of the User to send verification email to

    Returns:
        Dict containing email sending results

    Raises:
        User.DoesNotExist: If user doesn't exist
        Exception: For email sending errors

    Example:
        # Send verification email to new user
        result = send_verification_email_task.delay(user_id=123)
    """
    tracker = TaskStatusTracker()
    tracker.log_start(self.name, self.request.id, user_id=user_id)

    try:
        user = User.objects.get(id=user_id)

        if user.is_active:
            logger.info(f"User {user_id} is already verified")
            return {
                'status': 'skipped',
                'user_id': user_id,
                'message': 'User is already verified'
            }

        if not user.email:
            raise ValueError(f"User {user_id} has no email address")

        # TODO: Generate verification token
        # This will be implemented by the Email Verification agent
        # For now, we'll use a simple random token
        # In production, use proper token generation with expiration
        verification_token = get_random_string(length=64)

        # TODO: Store verification token in database
        # Option 1: Add verification_token field to User model
        # Option 2: Create separate EmailVerification model
        # For now, we'll just log it
        logger.info(f"Generated verification token for user {user_id}: {verification_token}")

        # Build verification URL
        # TODO: Use proper domain from settings
        verification_url = f"http://localhost:8000/accounts/verify/{verification_token}/"

        # Prepare email content
        context = {
            'user': user,
            'verification_url': verification_url,
        }

        try:
            # Try to render HTML template
            html_message = render_to_string('accounts/email/verification.html', context)
            plain_message = strip_tags(html_message)
        except Exception:
            # Fallback to plain text if template doesn't exist
            plain_message = (
                f"Hello {user.get_full_name()},\n\n"
                f"Please verify your email address by clicking the link below:\n\n"
                f"{verification_url}\n\n"
                f"If you didn't create an account, please ignore this email.\n\n"
                f"Thanks,\n"
                f"Job Tracker Team"
            )
            html_message = None

        # Send verification email
        send_mail(
            subject='Verify your email address - Job Tracker',
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )

        logger.info(f"Sent verification email to {user.email}")

        result = {
            'status': 'success',
            'user_id': user_id,
            'email': user.email,
            'sent_at': timezone.now().isoformat()
        }

        tracker.log_completion(self.name, self.request.id, **result)
        return result

    except User.DoesNotExist:
        logger.error(f"User with id {user_id} does not exist")
        raise
    except Exception as e:
        logger.error(f"Error sending verification email to user {user_id}: {e}", exc_info=True)
        # Retry with exponential backoff
        raise self.retry(exc=e, countdown=60 * (2 ** self.request.retries))


@shared_task(base=BaseTask, bind=True)
def cleanup_unverified_users_task(self, days: int = 7) -> Dict[str, any]:
    """
    Delete unverified user accounts older than specified days.

    This task removes user accounts that haven't been verified within
    the specified time period to keep the database clean.

    Args:
        days: Number of days after which to delete unverified users (default: 7)

    Returns:
        Dict containing cleanup statistics

    Example:
        # Clean up unverified users older than 7 days
        result = cleanup_unverified_users_task.delay(days=7)
    """
    tracker = TaskStatusTracker()
    tracker.log_start(self.name, self.request.id, days=days)

    try:
        cutoff_date = timezone.now() - timedelta(days=days)

        # Find unverified users created before cutoff date
        unverified_users = User.objects.filter(
            is_active=False,
            date_joined__lt=cutoff_date
        )

        # Exclude superusers from cleanup
        unverified_users = unverified_users.filter(is_superuser=False)

        user_count = unverified_users.count()
        user_emails = list(unverified_users.values_list('email', flat=True))

        # Delete unverified users
        deleted_count, _ = unverified_users.delete()

        logger.info(f"Deleted {deleted_count} unverified users older than {days} days")

        result = {
            'status': 'success',
            'cutoff_date': cutoff_date.isoformat(),
            'users_found': user_count,
            'users_deleted': deleted_count,
            'deleted_emails': user_emails[:10]  # Limit to first 10 for logging
        }

        tracker.log_completion(self.name, self.request.id, **result)
        return result

    except Exception as e:
        logger.error(f"Error cleaning up unverified users: {e}", exc_info=True)
        raise


@shared_task(base=BaseTask, bind=True, max_retries=3)
def send_password_reset_email_task(self, user_id: int, reset_token: str) -> Dict[str, any]:
    """
    Send password reset email to a user.

    Args:
        user_id: ID of the User
        reset_token: Password reset token

    Returns:
        Dict containing email sending results

    Example:
        # Send password reset email
        result = send_password_reset_email_task.delay(
            user_id=123,
            reset_token='abc123...'
        )
    """
    tracker = TaskStatusTracker()
    tracker.log_start(self.name, self.request.id, user_id=user_id)

    try:
        user = User.objects.get(id=user_id)

        if not user.email:
            raise ValueError(f"User {user_id} has no email address")

        # Build password reset URL
        # TODO: Use proper domain from settings
        reset_url = f"http://localhost:8000/accounts/password-reset/{reset_token}/"

        # Prepare email content
        context = {
            'user': user,
            'reset_url': reset_url,
        }

        try:
            # Try to render HTML template
            html_message = render_to_string('accounts/email/password_reset.html', context)
            plain_message = strip_tags(html_message)
        except Exception:
            # Fallback to plain text
            plain_message = (
                f"Hello {user.get_full_name()},\n\n"
                f"You requested to reset your password. Click the link below to reset it:\n\n"
                f"{reset_url}\n\n"
                f"If you didn't request this, please ignore this email.\n\n"
                f"Thanks,\n"
                f"Job Tracker Team"
            )
            html_message = None

        # Send password reset email
        send_mail(
            subject='Reset your password - Job Tracker',
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )

        logger.info(f"Sent password reset email to {user.email}")

        result = {
            'status': 'success',
            'user_id': user_id,
            'email': user.email,
            'sent_at': timezone.now().isoformat()
        }

        tracker.log_completion(self.name, self.request.id, **result)
        return result

    except User.DoesNotExist:
        logger.error(f"User with id {user_id} does not exist")
        raise
    except Exception as e:
        logger.error(f"Error sending password reset email to user {user_id}: {e}", exc_info=True)
        raise self.retry(exc=e, countdown=60 * (2 ** self.request.retries))


@shared_task(base=BaseTask, bind=True, max_retries=3)
def send_welcome_email_task(self, user_id: int) -> Dict[str, any]:
    """
    Send welcome email to a newly verified user.

    This task sends a welcome email with getting started information
    after a user successfully verifies their email.

    Args:
        user_id: ID of the User

    Returns:
        Dict containing email sending results

    Example:
        # Send welcome email
        result = send_welcome_email_task.delay(user_id=123)
    """
    tracker = TaskStatusTracker()
    tracker.log_start(self.name, self.request.id, user_id=user_id)

    try:
        user = User.objects.get(id=user_id)

        if not user.email:
            raise ValueError(f"User {user_id} has no email address")

        # Prepare email content
        context = {
            'user': user,
            'app_url': 'http://localhost:8000/',  # TODO: Use proper domain
        }

        try:
            # Try to render HTML template
            html_message = render_to_string('accounts/email/welcome.html', context)
            plain_message = strip_tags(html_message)
        except Exception:
            # Fallback to plain text
            plain_message = (
                f"Hello {user.get_full_name()},\n\n"
                f"Welcome to Job Tracker! Your account has been successfully verified.\n\n"
                f"You can now start tracking your job and scholarship applications.\n\n"
                f"Visit the app: http://localhost:8000/\n\n"
                f"Thanks,\n"
                f"Job Tracker Team"
            )
            html_message = None

        # Send welcome email
        send_mail(
            subject='Welcome to Job Tracker!',
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )

        logger.info(f"Sent welcome email to {user.email}")

        result = {
            'status': 'success',
            'user_id': user_id,
            'email': user.email,
            'sent_at': timezone.now().isoformat()
        }

        tracker.log_completion(self.name, self.request.id, **result)
        return result

    except User.DoesNotExist:
        logger.error(f"User with id {user_id} does not exist")
        raise
    except Exception as e:
        logger.error(f"Error sending welcome email to user {user_id}: {e}", exc_info=True)
        raise self.retry(exc=e, countdown=60 * (2 ** self.request.retries))


@shared_task(base=BaseTask, bind=True)
def cleanup_inactive_users_task(self, days: int = 365) -> Dict[str, any]:
    """
    Flag or notify users who haven't logged in for a long time.

    This task identifies inactive users and can be used to send them
    re-engagement emails or mark them for cleanup.

    Args:
        days: Number of days of inactivity to flag (default: 365)

    Returns:
        Dict containing inactive user statistics

    Example:
        # Find inactive users (1 year+)
        result = cleanup_inactive_users_task.delay(days=365)
    """
    tracker = TaskStatusTracker()
    tracker.log_start(self.name, self.request.id, days=days)

    try:
        cutoff_date = timezone.now() - timedelta(days=days)

        # Find users who haven't logged in since cutoff date
        inactive_users = User.objects.filter(
            is_active=True,
            last_login__lt=cutoff_date
        ).exclude(is_superuser=True)

        inactive_count = inactive_users.count()

        # TODO: Send re-engagement emails or mark for cleanup
        # For now, just log the inactive users
        logger.info(f"Found {inactive_count} users inactive for {days}+ days")

        result = {
            'status': 'success',
            'cutoff_date': cutoff_date.isoformat(),
            'inactive_users_found': inactive_count,
            'message': 'Inactive users identified (no action taken)'
        }

        tracker.log_completion(self.name, self.request.id, **result)
        return result

    except Exception as e:
        logger.error(f"Error identifying inactive users: {e}", exc_info=True)
        raise


@shared_task(base=BaseTask, bind=True)
def send_account_notification_task(
    self,
    user_id: int,
    subject: str,
    message: str,
    template_name: str = None
) -> Dict[str, any]:
    """
    Send a generic account-related notification email to a user.

    This is a general-purpose task for sending account notifications
    that don't fit into other specific categories.

    Args:
        user_id: ID of the User
        subject: Email subject
        message: Email message content
        template_name: Optional template name to use

    Returns:
        Dict containing email sending results

    Example:
        # Send custom notification
        result = send_account_notification_task.delay(
            user_id=123,
            subject="Important account update",
            message="Your account settings have been updated."
        )
    """
    tracker = TaskStatusTracker()
    tracker.log_start(self.name, self.request.id, user_id=user_id)

    try:
        user = User.objects.get(id=user_id)

        if not user.email:
            raise ValueError(f"User {user_id} has no email address")

        # Use template if provided
        if template_name:
            try:
                html_message = render_to_string(template_name, {
                    'user': user,
                    'message': message,
                })
                plain_message = strip_tags(html_message)
            except Exception as e:
                logger.warning(f"Could not render template {template_name}: {e}")
                plain_message = message
                html_message = None
        else:
            plain_message = message
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

        logger.info(f"Sent account notification to {user.email}")

        result = {
            'status': 'success',
            'user_id': user_id,
            'email': user.email,
            'subject': subject,
            'sent_at': timezone.now().isoformat()
        }

        tracker.log_completion(self.name, self.request.id, **result)
        return result

    except User.DoesNotExist:
        logger.error(f"User with id {user_id} does not exist")
        raise
    except Exception as e:
        logger.error(f"Error sending notification to user {user_id}: {e}", exc_info=True)
        raise
