"""
Tests for tracker models.
"""
import pytest
from django.utils import timezone
from datetime import timedelta
from tracker.models import Application, Question, Response, ApplicationStatus


@pytest.mark.django_db
class TestApplicationModel:
    """Test cases for Application model."""

    def test_create_application(self, test_user):
        """Test creating an application."""
        application = Application.objects.create(
            user=test_user,
            application_type='job',
            title='Software Engineer',
            company_or_institution='Test Company',
            url='https://example.com/job',
            description='Test description',
            deadline=timezone.now() + timedelta(days=7),
            status='draft',
            priority='high'
        )
        assert application.user == test_user
        assert application.application_type == 'job'
        assert application.title == 'Software Engineer'
        assert application.status == 'draft'
        assert application.priority == 'high'

    def test_application_str_representation(self, test_application):
        """Test application string representation."""
        expected = f"{test_application.title} at {test_application.company_or_institution}"
        assert str(test_application) == expected

    def test_application_is_overdue_property(self, test_user):
        """Test is_overdue property for overdue application."""
        # Create overdue application
        app = Application.objects.create(
            user=test_user,
            application_type='job',
            title='Overdue Job',
            company_or_institution='Test Corp',
            deadline=timezone.now() - timedelta(days=1),
            status='draft'
        )
        assert app.is_overdue is True

    def test_application_not_overdue_property(self, test_user):
        """Test is_overdue property for non-overdue application."""
        app = Application.objects.create(
            user=test_user,
            application_type='job',
            title='Future Job',
            company_or_institution='Test Corp',
            deadline=timezone.now() + timedelta(days=7),
            status='draft'
        )
        assert app.is_overdue is False

    def test_application_is_overdue_submitted_status(self, test_user):
        """Test is_overdue returns False for submitted applications."""
        app = Application.objects.create(
            user=test_user,
            application_type='job',
            title='Submitted Job',
            company_or_institution='Test Corp',
            deadline=timezone.now() - timedelta(days=1),
            status='submitted'
        )
        assert app.is_overdue is False

    def test_application_days_until_deadline(self, test_user):
        """Test days_until_deadline property."""
        deadline = timezone.now() + timedelta(days=5)
        app = Application.objects.create(
            user=test_user,
            application_type='job',
            title='Test Job',
            company_or_institution='Test Corp',
            deadline=deadline
        )
        assert app.days_until_deadline >= 4  # Allow for time elapsed during test

    def test_application_days_until_deadline_none(self, test_user):
        """Test days_until_deadline returns None when no deadline."""
        app = Application.objects.create(
            user=test_user,
            application_type='job',
            title='Test Job',
            company_or_institution='Test Corp'
        )
        assert app.days_until_deadline is None

    def test_application_ordering(self, test_user):
        """Test applications are ordered by created_at descending."""
        app1 = Application.objects.create(
            user=test_user,
            application_type='job',
            title='First',
            company_or_institution='Company A'
        )
        app2 = Application.objects.create(
            user=test_user,
            application_type='job',
            title='Second',
            company_or_institution='Company B'
        )
        apps = list(Application.objects.all())
        assert apps[0] == app2  # Most recent first
        assert apps[1] == app1

    def test_application_cascade_delete_questions(self, test_application, test_question):
        """Test questions are deleted when application is deleted."""
        question_id = test_question.id
        test_application.delete()
        assert not Question.objects.filter(id=question_id).exists()


@pytest.mark.django_db
class TestQuestionModel:
    """Test cases for Question model."""

    def test_create_question(self, test_application):
        """Test creating a question."""
        question = Question.objects.create(
            application=test_application,
            question_text='Why do you want this position?',
            question_type='essay',
            is_required=True,
            is_extracted=False,
            order=1
        )
        assert question.application == test_application
        assert question.question_text == 'Why do you want this position?'
        assert question.question_type == 'essay'
        assert question.is_required is True
        assert question.is_extracted is False
        assert question.order == 1

    def test_question_str_representation(self, test_question):
        """Test question string representation."""
        result = str(test_question)
        assert result.startswith(f"Q{test_question.order}:")
        assert test_question.question_text[:50] in result

    def test_question_ordering(self, test_application):
        """Test questions are ordered by order then created_at."""
        q2 = Question.objects.create(
            application=test_application,
            question_text='Question 2',
            question_type='short_answer',
            order=2
        )
        q1 = Question.objects.create(
            application=test_application,
            question_text='Question 1',
            question_type='short_answer',
            order=1
        )
        questions = list(Question.objects.all())
        assert questions[0] == q1  # Lower order first
        assert questions[1] == q2

    def test_question_cascade_delete_response(self, test_question, test_response):
        """Test response is deleted when question is deleted."""
        response_id = test_response.id
        test_question.delete()
        assert not Response.objects.filter(id=response_id).exists()


@pytest.mark.django_db
class TestResponseModel:
    """Test cases for Response model."""

    def test_create_response(self, test_question):
        """Test creating a response."""
        response = Response.objects.create(
            question=test_question,
            generated_response='Generated answer',
            is_ai_generated=True,
            generation_prompt='Test prompt',
            generated_at=timezone.now()
        )
        assert response.question == test_question
        assert response.generated_response == 'Generated answer'
        assert response.is_ai_generated is True
        assert response.version == 1

    def test_response_str_representation(self, test_response):
        """Test response string representation."""
        result = str(test_response)
        assert 'Response to:' in result
        assert test_response.question.question_text[:30] in result

    def test_response_final_response_edited(self, test_question):
        """Test final_response property returns edited response."""
        response = Response.objects.create(
            question=test_question,
            generated_response='Generated',
            edited_response='Edited version'
        )
        assert response.final_response == 'Edited version'

    def test_response_final_response_generated(self, test_question):
        """Test final_response property returns generated response when no edit."""
        response = Response.objects.create(
            question=test_question,
            generated_response='Generated response'
        )
        assert response.final_response == 'Generated response'

    def test_response_save_updates_version(self, test_response):
        """Test saving with edited_response updates version."""
        original_version = test_response.version
        test_response.edited_response = 'Updated response'
        test_response.save()
        assert test_response.version == original_version + 1
        assert test_response.last_edited_at is not None

    def test_response_one_to_one_relationship(self, test_question):
        """Test one-to-one relationship between Question and Response."""
        response1 = Response.objects.create(question=test_question)
        # Attempting to create another response for same question should fail
        with pytest.raises(Exception):  # IntegrityError
            Response.objects.create(question=test_question)


@pytest.mark.django_db
class TestApplicationStatusModel:
    """Test cases for ApplicationStatus model."""

    def test_create_application_status(self, test_application):
        """Test creating an application status."""
        status = ApplicationStatus.objects.create(
            application=test_application,
            status='submitted',
            changed_by='user_update',
            notes='Submitted application'
        )
        assert status.application == test_application
        assert status.status == 'submitted'
        assert status.changed_by == 'user_update'
        assert status.notes == 'Submitted application'

    def test_application_status_str_representation(self, test_application):
        """Test application status string representation."""
        status = ApplicationStatus.objects.create(
            application=test_application,
            status='in_review',
            changed_by='manual'
        )
        result = str(status)
        assert test_application.title in result
        assert 'In Review' in result

    def test_application_status_ordering(self, test_application):
        """Test statuses are ordered by created_at descending."""
        status1 = ApplicationStatus.objects.create(
            application=test_application,
            status='draft',
            changed_by='manual'
        )
        status2 = ApplicationStatus.objects.create(
            application=test_application,
            status='submitted',
            changed_by='user_update'
        )
        statuses = list(ApplicationStatus.objects.all())
        assert statuses[0] == status2  # Most recent first
        assert statuses[1] == status1

    def test_application_status_cascade_delete(self, test_application):
        """Test status history is deleted when application is deleted."""
        status = ApplicationStatus.objects.create(
            application=test_application,
            status='submitted'
        )
        status_id = status.id
        test_application.delete()
        assert not ApplicationStatus.objects.filter(id=status_id).exists()
