"""
Tests for tracker forms.
"""
import pytest
from django.utils import timezone
from datetime import timedelta
from tracker.forms import (
    ApplicationForm, QuickApplicationForm, QuestionForm,
    ResponseForm, ApplicationFilterForm
)
from tracker.models import Application, Question, Response


@pytest.mark.django_db
class TestApplicationForm:
    """Test cases for ApplicationForm."""

    def test_valid_application_form(self):
        """Test form with valid data."""
        form_data = {
            'application_type': 'job',
            'title': 'Software Engineer',
            'company_or_institution': 'Test Company',
            'url': 'https://example.com/job',
            'description': 'Test description',
            'deadline': (timezone.now() + timedelta(days=7)).strftime('%Y-%m-%dT%H:%M'),
            'status': 'draft',
            'priority': 'high',
            'notes': 'Test notes'
        }
        form = ApplicationForm(data=form_data)
        assert form.is_valid()

    def test_application_form_optional_fields(self):
        """Test form with only required fields."""
        form_data = {
            'application_type': 'job',
            'title': 'Software Engineer',
            'company_or_institution': 'Test Company',
            'status': 'draft',
            'priority': 'medium'
        }
        form = ApplicationForm(data=form_data)
        assert form.is_valid()

    def test_application_form_missing_required_fields(self):
        """Test form with missing required fields."""
        form_data = {
            'application_type': 'job'
        }
        form = ApplicationForm(data=form_data)
        assert not form.is_valid()
        assert 'title' in form.errors
        assert 'company_or_institution' in form.errors

    def test_application_form_invalid_url(self):
        """Test form with invalid URL."""
        form_data = {
            'application_type': 'job',
            'title': 'Software Engineer',
            'company_or_institution': 'Test Company',
            'url': 'not-a-valid-url',
            'status': 'draft',
            'priority': 'medium'
        }
        form = ApplicationForm(data=form_data)
        assert not form.is_valid()
        assert 'url' in form.errors

    def test_application_form_all_application_types(self):
        """Test form accepts all valid application types."""
        for app_type, label in Application.APPLICATION_TYPE_CHOICES:
            form_data = {
                'application_type': app_type,
                'title': 'Test',
                'company_or_institution': 'Test',
                'status': 'draft',
                'priority': 'medium'
            }
            form = ApplicationForm(data=form_data)
            assert form.is_valid()

    def test_application_form_all_statuses(self):
        """Test form accepts all valid statuses."""
        for status, label in Application.STATUS_CHOICES:
            form_data = {
                'application_type': 'job',
                'title': 'Test',
                'company_or_institution': 'Test',
                'status': status,
                'priority': 'medium'
            }
            form = ApplicationForm(data=form_data)
            assert form.is_valid()

    def test_application_form_all_priorities(self):
        """Test form accepts all valid priorities."""
        for priority, label in Application.PRIORITY_CHOICES:
            form_data = {
                'application_type': 'job',
                'title': 'Test',
                'company_or_institution': 'Test',
                'status': 'draft',
                'priority': priority
            }
            form = ApplicationForm(data=form_data)
            assert form.is_valid()


@pytest.mark.django_db
class TestQuickApplicationForm:
    """Test cases for QuickApplicationForm."""

    def test_valid_quick_application_form(self):
        """Test form with valid data."""
        form_data = {
            'application_type': 'job',
            'url': 'https://example.com/job'
        }
        form = QuickApplicationForm(data=form_data)
        assert form.is_valid()

    def test_quick_application_form_missing_url(self):
        """Test form with missing URL."""
        form_data = {
            'application_type': 'job'
        }
        form = QuickApplicationForm(data=form_data)
        assert not form.is_valid()
        assert 'url' in form.errors

    def test_quick_application_form_invalid_url(self):
        """Test form with invalid URL."""
        form_data = {
            'application_type': 'job',
            'url': 'invalid-url'
        }
        form = QuickApplicationForm(data=form_data)
        assert not form.is_valid()
        assert 'url' in form.errors

    def test_quick_application_form_scholarship_type(self):
        """Test form with scholarship type."""
        form_data = {
            'application_type': 'scholarship',
            'url': 'https://example.com/scholarship'
        }
        form = QuickApplicationForm(data=form_data)
        assert form.is_valid()


@pytest.mark.django_db
class TestQuestionForm:
    """Test cases for QuestionForm."""

    def test_valid_question_form(self):
        """Test form with valid data."""
        form_data = {
            'question_text': 'Why do you want this position?',
            'question_type': 'essay',
            'is_required': True,
            'order': 1
        }
        form = QuestionForm(data=form_data)
        assert form.is_valid()

    def test_question_form_all_question_types(self):
        """Test form accepts all valid question types."""
        for q_type, label in Question.QUESTION_TYPE_CHOICES:
            form_data = {
                'question_text': 'Test question?',
                'question_type': q_type,
                'is_required': False,
                'order': 1
            }
            form = QuestionForm(data=form_data)
            assert form.is_valid()

    def test_question_form_missing_required_fields(self):
        """Test form with missing required fields."""
        form_data = {}
        form = QuestionForm(data=form_data)
        assert not form.is_valid()
        assert 'question_text' in form.errors
        assert 'question_type' in form.errors

    def test_question_form_optional_is_required(self):
        """Test is_required field is optional."""
        form_data = {
            'question_text': 'Test question?',
            'question_type': 'short_answer',
            'order': 1
        }
        form = QuestionForm(data=form_data)
        assert form.is_valid()


@pytest.mark.django_db
class TestResponseForm:
    """Test cases for ResponseForm."""

    def test_valid_response_form(self, test_response):
        """Test form with valid data."""
        form_data = {
            'edited_response': 'This is my edited response.'
        }
        form = ResponseForm(data=form_data, instance=test_response)
        assert form.is_valid()

    def test_response_form_empty_response(self, test_response):
        """Test form with empty response."""
        form_data = {
            'edited_response': ''
        }
        form = ResponseForm(data=form_data, instance=test_response)
        # Empty response should be valid (allows clearing)
        assert form.is_valid()

    def test_response_form_long_response(self, test_response):
        """Test form with long response."""
        form_data = {
            'edited_response': 'A' * 5000  # Very long response
        }
        form = ResponseForm(data=form_data, instance=test_response)
        assert form.is_valid()

    def test_response_form_save_updates_response(self, test_response):
        """Test form save updates response."""
        form_data = {
            'edited_response': 'Updated response text'
        }
        form = ResponseForm(data=form_data, instance=test_response)
        assert form.is_valid()
        updated_response = form.save()
        assert updated_response.edited_response == 'Updated response text'


@pytest.mark.django_db
class TestApplicationFilterForm:
    """Test cases for ApplicationFilterForm."""

    def test_valid_filter_form_empty(self):
        """Test form with no filters."""
        form_data = {}
        form = ApplicationFilterForm(data=form_data)
        assert form.is_valid()

    def test_filter_form_with_search(self):
        """Test form with search query."""
        form_data = {
            'search': 'software engineer'
        }
        form = ApplicationFilterForm(data=form_data)
        assert form.is_valid()
        assert form.cleaned_data['search'] == 'software engineer'

    def test_filter_form_with_application_type(self):
        """Test form with application type filter."""
        form_data = {
            'application_type': 'job'
        }
        form = ApplicationFilterForm(data=form_data)
        assert form.is_valid()
        assert form.cleaned_data['application_type'] == 'job'

    def test_filter_form_with_status(self):
        """Test form with status filter."""
        form_data = {
            'status': 'submitted'
        }
        form = ApplicationFilterForm(data=form_data)
        assert form.is_valid()
        assert form.cleaned_data['status'] == 'submitted'

    def test_filter_form_with_priority(self):
        """Test form with priority filter."""
        form_data = {
            'priority': 'high'
        }
        form = ApplicationFilterForm(data=form_data)
        assert form.is_valid()
        assert form.cleaned_data['priority'] == 'high'

    def test_filter_form_with_all_filters(self):
        """Test form with all filters."""
        form_data = {
            'search': 'engineer',
            'application_type': 'job',
            'status': 'draft',
            'priority': 'high'
        }
        form = ApplicationFilterForm(data=form_data)
        assert form.is_valid()
        assert form.cleaned_data['search'] == 'engineer'
        assert form.cleaned_data['application_type'] == 'job'
        assert form.cleaned_data['status'] == 'draft'
        assert form.cleaned_data['priority'] == 'high'

    def test_filter_form_all_fields_optional(self):
        """Test all filter form fields are optional."""
        form = ApplicationFilterForm(data={})
        assert form.is_valid()
        for field in form.fields.values():
            assert field.required is False
