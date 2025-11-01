"""
Celery tasks for application tracking.

This module contains background tasks for scraping application URLs,
extracting questions using AI, and generating responses.
"""
import logging
from typing import Dict, List, Optional

from celery import shared_task, group, chain
from django.utils import timezone

from core.tasks import BaseTask, exponential_backoff_retry, TaskStatusTracker
from tracker.models import Application, Question, Response, ApplicationStatus

logger = logging.getLogger(__name__)


@shared_task(base=BaseTask, bind=True, max_retries=5)
@exponential_backoff_retry(max_retries=5, base_delay=30)
def scrape_url_task(self, application_id: int) -> Dict[str, any]:
    """
    Scrape content from an application URL.

    This task fetches and parses content from the application URL to extract
    relevant information such as job description, requirements, and questions.

    Args:
        application_id: ID of the Application to scrape

    Returns:
        Dict containing scraped content and metadata

    Raises:
        Application.DoesNotExist: If application doesn't exist
        ValueError: If application has no URL
        Exception: For network or parsing errors

    Example:
        # Scrape application URL
        result = scrape_url_task.delay(application_id=123)

        # Chain with question extraction
        chain(
            scrape_url_task.si(123),
            extract_questions_task.s(123)
        ).apply_async()
    """
    tracker = TaskStatusTracker()
    tracker.log_start(self.name, self.request.id, application_id=application_id)

    try:
        application = Application.objects.get(id=application_id)

        if not application.url:
            raise ValueError(f"Application {application_id} has no URL to scrape")

        logger.info(f"Scraping URL: {application.url}")

        # TODO: Implement actual web scraping logic
        # The Web Scraping agent will implement this
        # from services.scraper_service import scrape_application_url
        # scraped_data = scrape_application_url(application.url)

        # Placeholder for scraped content
        scraped_content = {
            'url': application.url,
            'title': None,
            'description': None,
            'requirements': [],
            'questions': [],
            'raw_html': None,
            'raw_text': None,
        }

        # TODO: Update application description if not set
        # if scraped_content.get('description') and not application.description:
        #     application.description = scraped_content['description']
        #     application.save(update_fields=['description'])

        # Trigger question extraction task
        if scraped_content.get('raw_text'):
            extract_questions_task.delay(application_id, scraped_content)

        result = {
            'status': 'success',
            'application_id': application_id,
            'url': application.url,
            'has_questions': bool(scraped_content.get('questions')),
            'scraped_at': timezone.now().isoformat()
        }

        tracker.log_completion(self.name, self.request.id, **result)
        return result

    except Application.DoesNotExist:
        logger.error(f"Application with id {application_id} does not exist")
        raise
    except Exception as e:
        logger.error(f"Error scraping URL for application {application_id}: {e}", exc_info=True)
        raise


@shared_task(base=BaseTask, bind=True, max_retries=3)
@exponential_backoff_retry(max_retries=3, base_delay=60)
def extract_questions_task(self, application_id: int, scraped_content: Optional[Dict] = None) -> Dict[str, any]:
    """
    Extract questions from scraped content using Gemini AI.

    This task analyzes scraped content or application description to identify
    and extract application questions using AI.

    Args:
        application_id: ID of the Application
        scraped_content: Optional dict containing scraped content from scrape_url_task

    Returns:
        Dict containing extracted questions and metadata

    Example:
        # Extract questions from application
        result = extract_questions_task.delay(application_id=123)

        # Extract from scraped content
        result = extract_questions_task.delay(
            application_id=123,
            scraped_content={'raw_text': 'Job description...'}
        )
    """
    tracker = TaskStatusTracker()
    tracker.log_start(self.name, self.request.id, application_id=application_id)

    try:
        application = Application.objects.get(id=application_id)
        logger.info(f"Extracting questions for: {application.title}")

        # Determine content source
        if scraped_content:
            content = scraped_content.get('raw_text', '')
        else:
            content = application.description

        if not content:
            logger.warning(f"No content available for question extraction: {application_id}")
            return {
                'status': 'skipped',
                'application_id': application_id,
                'message': 'No content available for extraction'
            }

        # TODO: Use Gemini API to extract questions
        # The AI Integration agent will implement this
        # from services.gemini_service import extract_application_questions
        # extracted_questions = extract_application_questions(
        #     content=content,
        #     application_type=application.application_type
        # )

        # Placeholder for extracted questions
        extracted_questions = []
        # Format: [
        #     {
        #         'text': 'Tell us about yourself',
        #         'type': 'essay',
        #         'is_required': True
        #     },
        #     ...
        # ]

        # Save extracted questions to database
        created_questions = []
        for i, q_data in enumerate(extracted_questions, start=1):
            question = Question.objects.create(
                application=application,
                question_text=q_data.get('text', ''),
                question_type=q_data.get('type', 'custom'),
                is_required=q_data.get('is_required', False),
                is_extracted=True,
                order=i
            )
            created_questions.append(question.id)

        result = {
            'status': 'success',
            'application_id': application_id,
            'questions_extracted': len(created_questions),
            'question_ids': created_questions
        }

        tracker.log_completion(self.name, self.request.id, **result)
        return result

    except Application.DoesNotExist:
        logger.error(f"Application with id {application_id} does not exist")
        raise
    except Exception as e:
        logger.error(f"Error extracting questions for application {application_id}: {e}", exc_info=True)
        raise


@shared_task(base=BaseTask, bind=True, max_retries=3)
@exponential_backoff_retry(max_retries=3, base_delay=60)
def generate_response_task(self, question_id: int, context: Optional[Dict] = None) -> Dict[str, any]:
    """
    Generate AI response for a specific question.

    This task uses Gemini AI to generate a tailored response to an application
    question based on user's profile, documents, and context.

    Args:
        question_id: ID of the Question to generate response for
        context: Optional dict containing additional context (user info, documents, etc.)

    Returns:
        Dict containing generated response and metadata

    Example:
        # Generate response for a question
        result = generate_response_task.delay(question_id=456)

        # Generate with custom context
        result = generate_response_task.delay(
            question_id=456,
            context={'focus_on': 'technical skills'}
        )
    """
    tracker = TaskStatusTracker()
    tracker.log_start(self.name, self.request.id, question_id=question_id)

    try:
        question = Question.objects.select_related('application', 'application__user').get(id=question_id)
        logger.info(f"Generating response for question: {question.question_text[:50]}...")

        # Get user and application context
        user = question.application.user
        application = question.application

        # TODO: Gather context from user's documents and profile
        # from documents.models import Document, ExtractedInformation
        # user_documents = Document.objects.filter(user=user, is_processed=True)
        # extracted_info = ExtractedInformation.objects.filter(document__user=user)

        # TODO: Build prompt for Gemini
        # prompt_context = {
        #     'question': question.question_text,
        #     'question_type': question.question_type,
        #     'application_type': application.application_type,
        #     'job_title': application.title,
        #     'company': application.company_or_institution,
        #     'user_info': extracted_info,
        #     'custom_context': context or {}
        # }

        # TODO: Use Gemini API to generate response
        # The AI Integration agent will implement this
        # from services.gemini_service import generate_question_response
        # generated_text = generate_question_response(prompt_context)

        # Placeholder for generated response
        generated_text = ""  # Will be implemented by AI Integration agent

        # Create or update response
        response, created = Response.objects.update_or_create(
            question=question,
            defaults={
                'generated_response': generated_text,
                'is_ai_generated': True,
                'generated_at': timezone.now(),
                'generation_prompt': ''  # TODO: Store actual prompt used
            }
        )

        result = {
            'status': 'success',
            'question_id': question_id,
            'response_id': response.id,
            'created': created,
            'response_length': len(generated_text) if generated_text else 0
        }

        tracker.log_completion(self.name, self.request.id, **result)
        return result

    except Question.DoesNotExist:
        logger.error(f"Question with id {question_id} does not exist")
        raise
    except Exception as e:
        logger.error(f"Error generating response for question {question_id}: {e}", exc_info=True)
        raise


@shared_task(base=BaseTask, bind=True)
def batch_generate_responses_task(self, application_id: int, regenerate: bool = False) -> Dict[str, any]:
    """
    Generate AI responses for all questions in an application.

    This task creates a batch job to generate responses for all questions
    associated with an application.

    Args:
        application_id: ID of the Application
        regenerate: If True, regenerate even if responses already exist

    Returns:
        Dict containing batch generation results

    Example:
        # Generate responses for all questions
        result = batch_generate_responses_task.delay(application_id=123)

        # Force regenerate all responses
        result = batch_generate_responses_task.delay(
            application_id=123,
            regenerate=True
        )
    """
    tracker = TaskStatusTracker()
    tracker.log_start(self.name, self.request.id, application_id=application_id)

    try:
        application = Application.objects.get(id=application_id)
        questions = application.questions.all()

        if not questions.exists():
            logger.warning(f"No questions found for application {application_id}")
            return {
                'status': 'skipped',
                'application_id': application_id,
                'message': 'No questions found'
            }

        # Filter questions that need responses
        if regenerate:
            questions_to_process = list(questions.values_list('id', flat=True))
        else:
            # Only process questions without responses
            questions_to_process = list(
                questions.exclude(response__isnull=False).values_list('id', flat=True)
            )

        if not questions_to_process:
            logger.info(f"All questions already have responses for application {application_id}")
            return {
                'status': 'skipped',
                'application_id': application_id,
                'message': 'All questions already have responses'
            }

        # Create a group of tasks to generate responses in parallel
        job = group(generate_response_task.si(q_id) for q_id in questions_to_process)
        group_result = job.apply_async()

        result = {
            'status': 'success',
            'application_id': application_id,
            'total_questions': questions.count(),
            'questions_to_process': len(questions_to_process),
            'group_task_id': group_result.id
        }

        tracker.log_completion(self.name, self.request.id, **result)
        return result

    except Application.DoesNotExist:
        logger.error(f"Application with id {application_id} does not exist")
        raise
    except Exception as e:
        logger.error(f"Error batch generating responses for application {application_id}: {e}", exc_info=True)
        raise


@shared_task(base=BaseTask, bind=True)
def scrape_and_extract_workflow_task(self, application_id: int) -> Dict[str, any]:
    """
    Complete workflow: scrape URL, extract questions, and generate responses.

    This is a convenience task that chains together the scraping, extraction,
    and generation tasks in a single workflow.

    Args:
        application_id: ID of the Application

    Returns:
        Dict containing workflow results

    Example:
        # Run complete workflow
        result = scrape_and_extract_workflow_task.delay(application_id=123)
    """
    tracker = TaskStatusTracker()
    tracker.log_start(self.name, self.request.id, application_id=application_id)

    try:
        # Create a workflow chain
        workflow = chain(
            scrape_url_task.si(application_id),
            extract_questions_task.si(application_id),
            batch_generate_responses_task.si(application_id)
        )

        # Execute the workflow
        workflow_result = workflow.apply_async()

        result = {
            'status': 'success',
            'application_id': application_id,
            'workflow_task_id': workflow_result.id,
            'started_at': timezone.now().isoformat()
        }

        tracker.log_completion(self.name, self.request.id, **result)
        return result

    except Exception as e:
        logger.error(f"Error starting workflow for application {application_id}: {e}", exc_info=True)
        raise


@shared_task(base=BaseTask, bind=True)
def update_application_status_task(self, application_id: int, new_status: str, notes: str = '') -> Dict[str, any]:
    """
    Update application status and create status history record.

    Args:
        application_id: ID of the Application
        new_status: New status value
        notes: Optional notes about the status change

    Returns:
        Dict containing update results

    Example:
        # Update status
        result = update_application_status_task.delay(
            application_id=123,
            new_status='submitted',
            notes='Applied via company website'
        )
    """
    tracker = TaskStatusTracker()
    tracker.log_start(self.name, self.request.id, application_id=application_id)

    try:
        application = Application.objects.get(id=application_id)
        old_status = application.status

        if old_status == new_status:
            logger.info(f"Status unchanged for application {application_id}: {new_status}")
            return {
                'status': 'unchanged',
                'application_id': application_id,
                'current_status': new_status
            }

        # Update application status
        application.status = new_status
        if new_status == 'submitted' and not application.submitted_at:
            application.submitted_at = timezone.now()
        application.save()

        # Create status history record
        status_history = ApplicationStatus.objects.create(
            application=application,
            status=new_status,
            changed_by='manual',
            notes=notes
        )

        result = {
            'status': 'success',
            'application_id': application_id,
            'old_status': old_status,
            'new_status': new_status,
            'status_history_id': status_history.id
        }

        logger.info(f"Updated application {application_id} status: {old_status} -> {new_status}")
        tracker.log_completion(self.name, self.request.id, **result)
        return result

    except Application.DoesNotExist:
        logger.error(f"Application with id {application_id} does not exist")
        raise
    except Exception as e:
        logger.error(f"Error updating status for application {application_id}: {e}", exc_info=True)
        raise


@shared_task(base=BaseTask, bind=True)
def check_application_deadlines_task(self) -> Dict[str, any]:
    """
    Check for upcoming application deadlines and create reminders.

    This task should be run periodically to identify applications with
    approaching deadlines and trigger reminder notifications.

    Returns:
        Dict containing check results and reminder statistics

    Example:
        # Check deadlines (usually scheduled via Celery Beat)
        result = check_application_deadlines_task.delay()
    """
    from datetime import timedelta
    from notifications.tasks import create_deadline_reminders_task

    tracker = TaskStatusTracker()
    tracker.log_start(self.name, self.request.id)

    try:
        now = timezone.now()
        # Check for deadlines in next 7 days
        upcoming_deadline = now + timedelta(days=7)

        # Find applications with upcoming deadlines
        applications_with_deadlines = Application.objects.filter(
            deadline__isnull=False,
            deadline__gt=now,
            deadline__lte=upcoming_deadline,
            status__in=['draft', 'in_review']
        )

        reminder_tasks = []
        for app in applications_with_deadlines:
            # Create reminder for this application
            task_result = create_deadline_reminders_task.delay(app.id)
            reminder_tasks.append(task_result.id)

        result = {
            'status': 'success',
            'checked_at': now.isoformat(),
            'upcoming_deadlines': applications_with_deadlines.count(),
            'reminders_created': len(reminder_tasks),
            'reminder_task_ids': reminder_tasks
        }

        tracker.log_completion(self.name, self.request.id, **result)
        return result

    except Exception as e:
        logger.error(f"Error checking application deadlines: {e}", exc_info=True)
        raise
