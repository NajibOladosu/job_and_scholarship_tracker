"""
Core task utilities for Celery tasks.

This module provides base task classes, decorators, and utilities
for all Celery tasks in the application.
"""
import logging
from functools import wraps
from typing import Any, Callable

from celery import Task, shared_task
from celery.exceptions import MaxRetriesExceededError
from django.utils import timezone

logger = logging.getLogger(__name__)


class BaseTask(Task):
    """
    Base task class with enhanced logging and error handling.

    All custom tasks should inherit from this class to get
    consistent logging and error handling behavior.
    """

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """
        Error handler called when the task fails.

        Args:
            exc: The exception raised by the task
            task_id: Unique id of the failed task
            args: Original arguments for the task
            kwargs: Original keyword arguments for the task
            einfo: ExceptionInfo instance, containing the traceback
        """
        logger.error(
            f"Task {self.name}[{task_id}] failed: {exc}",
            extra={
                'task_name': self.name,
                'task_id': task_id,
                'task_args': str(args),
                'task_kwargs': str(kwargs),
                'exception': str(exc),
            },
            exc_info=einfo
        )
        super().on_failure(exc, task_id, args, kwargs, einfo)

    def on_retry(self, exc, task_id, args, kwargs, einfo):
        """
        Error handler called when the task is retried.

        Args:
            exc: The exception that caused the retry
            task_id: Unique id of the retried task
            args: Original arguments for the task
            kwargs: Original keyword arguments for the task
            einfo: ExceptionInfo instance, containing the traceback
        """
        logger.warning(
            f"Task {self.name}[{task_id}] retry: {exc}",
            extra={
                'task_name': self.name,
                'task_id': task_id,
                'task_args': str(args),
                'task_kwargs': str(kwargs),
                'exception': str(exc),
            }
        )
        super().on_retry(exc, task_id, args, kwargs, einfo)

    def on_success(self, retval, task_id, args, kwargs):
        """
        Success handler called when the task succeeds.

        Args:
            retval: The return value of the task
            task_id: Unique id of the executed task
            args: Original arguments for the task
            kwargs: Original keyword arguments for the task
        """
        logger.info(
            f"Task {self.name}[{task_id}] succeeded",
            extra={
                'task_name': self.name,
                'task_id': task_id,
                'task_args': str(args),
                'task_kwargs': str(kwargs),
            }
        )
        super().on_success(retval, task_id, args, kwargs)


def log_task_execution(func: Callable) -> Callable:
    """
    Decorator to log task execution start and completion.

    Usage:
        @shared_task
        @log_task_execution
        def my_task():
            pass
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        logger.info(f"Starting task: {func.__name__} with args={args}, kwargs={kwargs}")
        try:
            result = func(*args, **kwargs)
            logger.info(f"Completed task: {func.__name__}")
            return result
        except Exception as e:
            logger.error(f"Error in task {func.__name__}: {e}", exc_info=True)
            raise
    return wrapper


def exponential_backoff_retry(max_retries: int = 3, base_delay: int = 60):
    """
    Decorator for tasks that should retry with exponential backoff.

    Args:
        max_retries: Maximum number of retry attempts
        base_delay: Base delay in seconds (will be multiplied by 2^retry_count)

    Usage:
        @shared_task(bind=True)
        @exponential_backoff_retry(max_retries=5, base_delay=30)
        def my_task(self, arg):
            # Task logic here
            pass
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            try:
                return func(self, *args, **kwargs)
            except Exception as exc:
                # Calculate exponential backoff: base_delay * 2^retry_count
                retry_count = self.request.retries
                countdown = base_delay * (2 ** retry_count)

                logger.warning(
                    f"Task {self.name} failed, retrying in {countdown}s "
                    f"(attempt {retry_count + 1}/{max_retries})"
                )

                try:
                    raise self.retry(
                        exc=exc,
                        countdown=countdown,
                        max_retries=max_retries
                    )
                except MaxRetriesExceededError:
                    logger.error(
                        f"Task {self.name} failed after {max_retries} retries",
                        exc_info=True
                    )
                    raise
        return wrapper
    return decorator


class TaskStatusTracker:
    """
    Utility class for tracking task execution status.

    This can be extended to store task status in database if needed.
    Currently uses logging for status tracking.
    """

    @staticmethod
    def log_start(task_name: str, task_id: str, **context):
        """Log task start with context."""
        logger.info(
            f"Task started: {task_name}",
            extra={
                'task_name': task_name,
                'task_id': task_id,
                'started_at': timezone.now().isoformat(),
                **context
            }
        )

    @staticmethod
    def log_progress(task_name: str, task_id: str, progress: int, total: int, **context):
        """Log task progress."""
        logger.info(
            f"Task progress: {task_name} - {progress}/{total}",
            extra={
                'task_name': task_name,
                'task_id': task_id,
                'progress': progress,
                'total': total,
                'percentage': round((progress / total) * 100, 2) if total > 0 else 0,
                **context
            }
        )

    @staticmethod
    def log_completion(task_name: str, task_id: str, **context):
        """Log task completion with context."""
        logger.info(
            f"Task completed: {task_name}",
            extra={
                'task_name': task_name,
                'task_id': task_id,
                'completed_at': timezone.now().isoformat(),
                **context
            }
        )


def safe_task_execution(func: Callable) -> Callable:
    """
    Decorator to safely execute tasks and catch all exceptions.

    This decorator ensures that tasks never fail silently and
    all exceptions are properly logged.

    Usage:
        @shared_task
        @safe_task_execution
        def my_task():
            pass
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.exception(
                f"Unhandled exception in task {func.__name__}: {e}",
                extra={
                    'task_name': func.__name__,
                    'task_args': str(args),
                    'task_kwargs': str(kwargs),
                }
            )
            # Re-raise to ensure task is marked as failed
            raise
    return wrapper


# Example usage demonstrating the utilities
@shared_task(base=BaseTask, bind=True)
def example_task(self, param: str) -> str:
    """
    Example task demonstrating the use of BaseTask and utilities.

    Args:
        param: Example parameter

    Returns:
        str: Success message

    Usage:
        # Immediate execution
        result = example_task.delay('test')

        # Scheduled execution (5 minutes later)
        example_task.apply_async(args=['test'], countdown=300)
    """
    tracker = TaskStatusTracker()
    tracker.log_start(self.name, self.request.id, param=param)

    # Simulate some work
    logger.info(f"Processing with param: {param}")

    tracker.log_completion(self.name, self.request.id, result='success')
    return f"Task completed with param: {param}"
