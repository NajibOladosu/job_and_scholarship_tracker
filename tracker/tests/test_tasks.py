"""
Tests for tracker tasks.
"""
import pytest
from unittest.mock import patch, MagicMock
from tracker.tasks import scrape_url_task, extract_questions_task, generate_response_task
from tracker.models import Application, Question, Response


@pytest.mark.django_db
@pytest.mark.celery
class TestScrapeUrlTask:
    """Test cases for scrape_url_task."""

    def test_scrape_url_task_success(self, test_application, mock_scraper_service):
        """Test scraping URL successfully."""
        with patch('tracker.tasks.get_scraper_service', return_value=mock_scraper_service):
            with patch('tracker.tasks.extract_questions_task') as mock_extract:
                result = scrape_url_task(test_application.id)

                assert result['status'] == 'success'
                assert result['application_id'] == test_application.id
                # Verify extract_questions_task was called
                assert mock_extract.apply_async.called

    def test_scrape_url_task_updates_application(self, test_user, mock_scraper_service):
        """Test scraping updates application with scraped data."""
        # Create application with placeholder data
        app = Application.objects.create(
            user=test_user,
            application_type='job',
            title='Processing...',
            company_or_institution='Processing...',
            url='https://example.com/job'
        )

        with patch('tracker.tasks.get_scraper_service', return_value=mock_scraper_service):
            with patch('tracker.tasks.extract_questions_task'):
                scrape_url_task(app.id)

                app.refresh_from_db()
                # Title should be updated from mock scraper
                assert app.title != 'Processing...'

    def test_scrape_url_task_no_url(self, test_user):
        """Test scraping fails when application has no URL."""
        app = Application.objects.create(
            user=test_user,
            application_type='job',
            title='No URL Job',
            company_or_institution='Test Company'
        )

        with pytest.raises(ValueError, match='has no URL to scrape'):
            scrape_url_task(app.id)

    def test_scrape_url_task_scraper_fails(self, test_application):
        """Test handling scraper failure."""
        mock_scraper = MagicMock()
        mock_scraper.scrape_url.return_value = {
            'success': False,
            'content': '',
            'title': '',
            'error': 'Network error'
        }

        with patch('tracker.tasks.get_scraper_service', return_value=mock_scraper):
            with pytest.raises(ValueError, match='Failed to scrape URL'):
                scrape_url_task(test_application.id)

    def test_scrape_url_task_nonexistent_application(self):
        """Test scraping nonexistent application."""
        with pytest.raises(Application.DoesNotExist):
            scrape_url_task(99999)


@pytest.mark.django_db
@pytest.mark.celery
class TestExtractQuestionsTask:
    """Test cases for extract_questions_task."""

    def test_extract_questions_task_success(self, test_application, mock_gemini_service):
        """Test extracting questions successfully."""
        scraped_content = {
            'url': test_application.url,
            'title': 'Job Title',
            'raw_text': 'Job description with questions...'
        }

        with patch('tracker.tasks.get_gemini_service', return_value=mock_gemini_service):
            result = extract_questions_task(test_application.id, scraped_content)

            assert result['status'] == 'success'
            assert result['application_id'] == test_application.id
            assert result['questions_extracted'] > 0

            # Verify questions were created
            assert Question.objects.filter(application=test_application).count() > 0

    def test_extract_questions_creates_correct_questions(
        self, test_application, mock_gemini_service
    ):
        """Test questions are created with correct data."""
        scraped_content = {
            'url': test_application.url,
            'title': 'Job Title',
            'raw_text': 'Content...'
        }

        with patch('tracker.tasks.get_gemini_service', return_value=mock_gemini_service):
            extract_questions_task(test_application.id, scraped_content)

            questions = Question.objects.filter(application=test_application)
            assert questions.count() == 2  # Mock returns 2 questions

            first_question = questions.first()
            assert first_question.is_extracted is True
            assert first_question.question_type in ['essay', 'experience']

    def test_extract_questions_task_no_questions_found(self, test_application):
        """Test when no questions are extracted."""
        mock_gemini = MagicMock()
        mock_gemini.extract_questions_from_content.return_value = []

        scraped_content = {
            'url': test_application.url,
            'title': 'Job Title',
            'raw_text': 'No questions here...'
        }

        with patch('tracker.tasks.get_gemini_service', return_value=mock_gemini):
            result = extract_questions_task(test_application.id, scraped_content)

            assert result['questions_extracted'] == 0
            assert Question.objects.filter(application=test_application).count() == 0

    def test_extract_questions_task_nonexistent_application(self):
        """Test extracting questions for nonexistent application."""
        scraped_content = {
            'url': 'https://example.com',
            'title': 'Title',
            'raw_text': 'Content'
        }

        with pytest.raises(Application.DoesNotExist):
            extract_questions_task(99999, scraped_content)


@pytest.mark.django_db
@pytest.mark.celery
class TestGenerateResponseTask:
    """Test cases for generate_response_task."""

    def test_generate_response_task_success(self, test_question, mock_gemini_service):
        """Test generating response successfully."""
        with patch('tracker.tasks.get_gemini_service', return_value=mock_gemini_service):
            with patch('tracker.tasks._get_user_extracted_info', return_value={}):
                result = generate_response_task(test_question.id)

                assert result['status'] == 'success'
                assert result['question_id'] == test_question.id

                # Verify response was created
                assert Response.objects.filter(question=test_question).exists()

    def test_generate_response_creates_response_object(self, test_question, mock_gemini_service):
        """Test response object is created correctly."""
        with patch('tracker.tasks.get_gemini_service', return_value=mock_gemini_service):
            with patch('tracker.tasks._get_user_extracted_info', return_value={}):
                generate_response_task(test_question.id)

                response = Response.objects.get(question=test_question)
                assert response.is_ai_generated is True
                assert response.generated_response != ''
                assert response.generation_prompt != ''
                assert response.generated_at is not None

    def test_generate_response_task_updates_existing_response(
        self, test_question, test_response, mock_gemini_service
    ):
        """Test generating response updates existing response."""
        original_response_text = test_response.generated_response

        with patch('tracker.tasks.get_gemini_service', return_value=mock_gemini_service):
            with patch('tracker.tasks._get_user_extracted_info', return_value={}):
                generate_response_task(test_question.id)

                test_response.refresh_from_db()
                # Response should be updated
                assert Response.objects.filter(question=test_question).count() == 1

    def test_generate_response_task_uses_user_info(self, test_question, mock_gemini_service):
        """Test response generation uses user information."""
        user_info = {
            'name': 'Test User',
            'education': [{'institution': 'Test University'}],
            'skills': ['Python', 'Django']
        }

        with patch('tracker.tasks.get_gemini_service', return_value=mock_gemini_service):
            with patch('tracker.tasks._get_user_extracted_info', return_value=user_info):
                generate_response_task(test_question.id)

                # Verify Gemini service was called with user info
                assert mock_gemini_service.generate_response.called
                call_args = mock_gemini_service.generate_response.call_args
                assert call_args[0][2] == user_info  # Third argument is user_info

    def test_generate_response_task_nonexistent_question(self, mock_gemini_service):
        """Test generating response for nonexistent question."""
        with pytest.raises(Question.DoesNotExist):
            generate_response_task(99999)

    def test_generate_response_task_gemini_failure(self, test_question):
        """Test handling Gemini API failure."""
        mock_gemini = MagicMock()
        mock_gemini.generate_response.return_value = {
            'response': '',
            'prompt': 'Test prompt'
        }

        with patch('tracker.tasks.get_gemini_service', return_value=mock_gemini):
            with patch('tracker.tasks._get_user_extracted_info', return_value={}):
                result = generate_response_task(test_question.id)

                # Task should complete but with empty response
                response = Response.objects.get(question=test_question)
                assert response.generated_response == ''


@pytest.mark.django_db
@pytest.mark.celery
class TestBatchGenerateResponsesTask:
    """Test cases for batch_generate_responses_task."""

    def test_batch_generate_creates_tasks_for_all_questions(
        self, test_application, mock_gemini_service
    ):
        """Test batch generation creates tasks for all questions."""
        # Create multiple questions
        Question.objects.create(
            application=test_application,
            question_text='Question 1?',
            question_type='short_answer',
            order=1
        )
        Question.objects.create(
            application=test_application,
            question_text='Question 2?',
            question_type='essay',
            order=2
        )

        from tracker.tasks import batch_generate_responses_task

        with patch('tracker.tasks.generate_response_task') as mock_task:
            with patch('tracker.tasks._get_user_extracted_info', return_value={}):
                batch_generate_responses_task(test_application.id)

                # Verify generate_response_task was called for each question
                assert mock_task.apply_async.call_count == 2

    def test_batch_generate_no_questions(self, test_application):
        """Test batch generation with no questions."""
        from tracker.tasks import batch_generate_responses_task

        # Application has no questions
        result = batch_generate_responses_task(test_application.id)

        assert result['responses_generated'] == 0
