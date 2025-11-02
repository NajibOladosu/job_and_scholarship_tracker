"""
Root conftest.py for pytest configuration and shared fixtures.
"""
import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from unittest.mock import Mock, patch, MagicMock
import json

User = get_user_model()


# ==================== Database Fixtures ====================

@pytest.fixture(scope='function')
def db_setup(db):
    """
    Ensure database is set up for each test function.
    """
    return db


# ==================== User Fixtures ====================

@pytest.fixture
def test_user(db):
    """
    Create a test user.
    """
    user = User.objects.create_user(
        email='testuser@example.com',
        password='testpass123',
        first_name='Test',
        last_name='User'
    )
    return user


@pytest.fixture
def test_user_with_profile(test_user):
    """
    Create a test user with profile.
    """
    from accounts.models import UserProfile

    # Profile should be created automatically via signal
    # If not, create it manually
    if not hasattr(test_user, 'profile'):
        UserProfile.objects.create(
            user=test_user,
            phone_number='+1234567890',
            current_position='Software Engineer',
            linkedin_url='https://linkedin.com/in/testuser',
            bio='Test user bio'
        )
    return test_user


@pytest.fixture
def another_user(db):
    """
    Create another test user for permission testing.
    """
    user = User.objects.create_user(
        email='another@example.com',
        password='testpass123',
        first_name='Another',
        last_name='User'
    )
    return user


@pytest.fixture
def superuser(db):
    """
    Create a superuser for admin testing.
    """
    user = User.objects.create_superuser(
        email='admin@example.com',
        password='adminpass123',
        first_name='Admin',
        last_name='User'
    )
    return user


# ==================== Application Fixtures ====================

@pytest.fixture
def test_application(test_user):
    """
    Create a test application.
    """
    from tracker.models import Application

    application = Application.objects.create(
        user=test_user,
        application_type='job',
        title='Software Engineer',
        company_or_institution='Test Company',
        url='https://example.com/job',
        description='Test job description',
        deadline=timezone.now() + timedelta(days=7),
        status='draft',
        priority='high',
        notes='Test notes'
    )
    return application


@pytest.fixture
def test_application_submitted(test_user):
    """
    Create a submitted test application.
    """
    from tracker.models import Application

    application = Application.objects.create(
        user=test_user,
        application_type='scholarship',
        title='Graduate Scholarship',
        company_or_institution='Test University',
        url='https://example.com/scholarship',
        description='Test scholarship description',
        deadline=timezone.now() + timedelta(days=14),
        status='submitted',
        priority='medium',
        submitted_at=timezone.now() - timedelta(days=1),
        notes='Submitted application'
    )
    return application


@pytest.fixture
def test_application_overdue(test_user):
    """
    Create an overdue test application.
    """
    from tracker.models import Application

    application = Application.objects.create(
        user=test_user,
        application_type='job',
        title='Overdue Job',
        company_or_institution='Test Corp',
        url='https://example.com/overdue',
        description='Overdue application',
        deadline=timezone.now() - timedelta(days=2),
        status='draft',
        priority='high'
    )
    return application


# ==================== Question and Response Fixtures ====================

@pytest.fixture
def test_question(test_application):
    """
    Create a test question.
    """
    from tracker.models import Question

    question = Question.objects.create(
        application=test_application,
        question_text='Why do you want to work here?',
        question_type='essay',
        is_required=True,
        is_extracted=False,
        order=1
    )
    return question


@pytest.fixture
def test_response(test_question):
    """
    Create a test response.
    """
    from tracker.models import Response

    response = Response.objects.create(
        question=test_question,
        generated_response='I am passionate about this opportunity...',
        is_ai_generated=True,
        generation_prompt='Generate a response for: Why do you want to work here?',
        generated_at=timezone.now()
    )
    return response


# ==================== Document Fixtures ====================

@pytest.fixture
def test_document(test_user, tmp_path):
    """
    Create a test document.
    """
    from documents.models import Document
    from django.core.files.uploadedfile import SimpleUploadedFile

    # Create a simple test file
    file_content = b"Test resume content"
    test_file = SimpleUploadedFile(
        "test_resume.pdf",
        file_content,
        content_type="application/pdf"
    )

    document = Document.objects.create(
        user=test_user,
        document_type='resume',
        file=test_file,
        original_filename='test_resume.pdf',
        file_size=len(file_content),
        is_processed=False
    )
    return document


@pytest.fixture
def test_document_processed(test_user, tmp_path):
    """
    Create a processed test document.
    """
    from documents.models import Document
    from django.core.files.uploadedfile import SimpleUploadedFile

    file_content = b"Test resume content - processed"
    test_file = SimpleUploadedFile(
        "processed_resume.pdf",
        file_content,
        content_type="application/pdf"
    )

    document = Document.objects.create(
        user=test_user,
        document_type='resume',
        file=test_file,
        original_filename='processed_resume.pdf',
        file_size=len(file_content),
        is_processed=True,
        processed_at=timezone.now()
    )
    return document


@pytest.fixture
def test_extracted_info(test_document_processed):
    """
    Create test extracted information.
    """
    from documents.models import ExtractedInformation

    info = ExtractedInformation.objects.create(
        document=test_document_processed,
        data_type='skills',
        content={'skills': ['Python', 'Django', 'Testing']},
        confidence_score=0.95
    )
    return info


# ==================== Notification Fixtures ====================

@pytest.fixture
def test_reminder(test_user, test_application):
    """
    Create a test reminder.
    """
    from notifications.models import Reminder

    reminder = Reminder.objects.create(
        user=test_user,
        application=test_application,
        reminder_type='deadline',
        message='Deadline approaching for Software Engineer application',
        scheduled_for=timezone.now() + timedelta(hours=24),
        is_sent=False
    )
    return reminder


@pytest.fixture
def test_notification(test_user):
    """
    Create a test notification.
    """
    from notifications.models import Notification

    notification = Notification.objects.create(
        user=test_user,
        notification_type='reminder',
        title='Test Notification',
        message='This is a test notification',
        is_read=False
    )
    return notification


# ==================== Factory Fixtures ====================

@pytest.fixture
def application_factory():
    """
    Factory for creating multiple applications.
    """
    from tracker.models import Application

    def create_application(user, **kwargs):
        defaults = {
            'application_type': 'job',
            'title': 'Test Job',
            'company_or_institution': 'Test Company',
            'url': 'https://example.com/job',
            'status': 'draft',
            'priority': 'medium',
            'deadline': timezone.now() + timedelta(days=7)
        }
        defaults.update(kwargs)
        return Application.objects.create(user=user, **defaults)

    return create_application


@pytest.fixture
def document_factory():
    """
    Factory for creating multiple documents.
    """
    from documents.models import Document
    from django.core.files.uploadedfile import SimpleUploadedFile

    def create_document(user, **kwargs):
        file_content = kwargs.pop('file_content', b"Test content")
        filename = kwargs.pop('filename', 'test.pdf')

        test_file = SimpleUploadedFile(
            filename,
            file_content,
            content_type=kwargs.pop('content_type', 'application/pdf')
        )

        defaults = {
            'document_type': 'resume',
            'file': test_file,
            'original_filename': filename,
            'file_size': len(file_content),
            'is_processed': False
        }
        defaults.update(kwargs)
        return Document.objects.create(user=user, **defaults)

    return create_document


# ==================== Mock Fixtures ====================

@pytest.fixture
def mock_celery_task():
    """
    Mock Celery task execution to prevent actual background task runs.
    """
    with patch('celery.app.task.Task.apply_async') as mock_apply_async:
        mock_result = Mock()
        mock_result.id = 'test-task-id'
        mock_apply_async.return_value = mock_result
        yield mock_apply_async


@pytest.fixture
def mock_gemini_service():
    """
    Mock GeminiService to prevent actual API calls.
    """
    with patch('services.gemini_service.GeminiService') as mock_service:
        mock_instance = MagicMock()

        # Mock extract_questions_from_content
        mock_instance.extract_questions_from_content.return_value = [
            {
                'question_text': 'Why do you want this position?',
                'question_type': 'essay',
                'is_required': True
            },
            {
                'question_text': 'Describe your experience.',
                'question_type': 'experience',
                'is_required': True
            }
        ]

        # Mock generate_response
        mock_instance.generate_response.return_value = {
            'response': 'This is a generated response to the question.',
            'prompt': 'Test prompt used for generation'
        }

        # Mock extract_document_information
        mock_instance.extract_document_information.return_value = {
            'name': 'Test User',
            'email': 'test@example.com',
            'education': [
                {
                    'institution': 'Test University',
                    'degree': 'Bachelor',
                    'field': 'Computer Science',
                    'graduation_year': '2020'
                }
            ],
            'experience': [
                {
                    'company': 'Test Company',
                    'title': 'Software Engineer',
                    'duration': '2020-2023',
                    'responsibilities': ['Development', 'Testing']
                }
            ],
            'skills': ['Python', 'Django', 'Testing'],
            'certifications': []
        }

        mock_service.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def mock_scraper_service():
    """
    Mock ScraperService to prevent actual web requests.
    """
    with patch('services.scraper_service.ScraperService') as mock_service:
        mock_instance = MagicMock()

        # Mock scrape_url
        mock_instance.scrape_url.return_value = {
            'success': True,
            'content': 'Job posting content with questions...',
            'title': 'Software Engineer Position',
            'error': ''
        }

        # Mock extract_metadata
        mock_instance.extract_metadata.return_value = {
            'title': 'Software Engineer',
            'company': 'Test Company',
            'location': 'Remote',
            'deadline': ''
        }

        mock_service.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def mock_document_parser():
    """
    Mock DocumentParser to prevent actual file parsing.
    """
    with patch('services.document_parser.DocumentParser') as mock_parser:
        mock_instance = MagicMock()

        # Mock parse_document
        mock_instance.parse_document.return_value = {
            'success': True,
            'text': 'Extracted resume text content...',
            'error': ''
        }

        mock_parser.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def mock_requests_get():
    """
    Mock requests.get for web scraping tests.
    """
    with patch('requests.Session.get') as mock_get:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b'<html><body><h1>Test Page</h1></body></html>'
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        yield mock_get


# ==================== Client Fixtures ====================

@pytest.fixture
def authenticated_client(client, test_user):
    """
    Django test client with authenticated test user.
    """
    client.force_login(test_user)
    return client


@pytest.fixture
def superuser_client(client, superuser):
    """
    Django test client with authenticated superuser.
    """
    client.force_login(superuser)
    return client


# ==================== Sample Data Fixtures ====================

@pytest.fixture
def sample_user_info():
    """
    Sample user information for testing response generation.
    """
    return {
        'name': 'Test User',
        'email': 'test@example.com',
        'phone': '+1234567890',
        'education': [
            {
                'institution': 'Test University',
                'degree': 'Bachelor of Science',
                'field': 'Computer Science',
                'graduation_year': '2020',
                'gpa': '3.8'
            }
        ],
        'experience': [
            {
                'company': 'Test Company',
                'title': 'Software Engineer',
                'duration': '2020-2023',
                'responsibilities': [
                    'Developed web applications',
                    'Wrote unit tests',
                    'Collaborated with team'
                ]
            }
        ],
        'skills': ['Python', 'Django', 'JavaScript', 'React', 'Testing'],
        'certifications': ['AWS Certified Developer']
    }


@pytest.fixture
def sample_scraped_content():
    """
    Sample scraped content for testing question extraction.
    """
    return """
    Software Engineer Position

    We are looking for a talented software engineer to join our team.

    Application Questions:
    1. Why do you want to work at our company?
    2. Describe your experience with Python and Django.
    3. What are your salary expectations?
    4. Tell us about a challenging project you've worked on.

    Requirements:
    - 3+ years of experience
    - Strong Python skills
    - Excellent communication
    """
