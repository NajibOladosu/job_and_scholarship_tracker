"""
Tests for documents tasks.
"""
import pytest
from unittest.mock import patch, MagicMock
from documents.tasks import process_document_task, extract_information_task
from documents.models import Document, ExtractedInformation


@pytest.mark.django_db
@pytest.mark.celery
class TestProcessDocumentTask:
    """Test cases for process_document_task."""

    def test_process_document_task_success(self, test_document, mock_document_parser):
        """Test processing document successfully."""
        with patch('documents.tasks.get_document_parser', return_value=mock_document_parser):
            with patch('documents.tasks.extract_information_task') as mock_extract:
                result = process_document_task(test_document.id)

                assert result['status'] == 'success'
                # Verify extract_information_task was called
                assert mock_extract.apply_async.called

    def test_process_document_task_parser_failure(self, test_document):
        """Test handling parser failure."""
        mock_parser = MagicMock()
        mock_parser.parse_document.return_value = {
            'success': False,
            'text': '',
            'error': 'Parse error'
        }

        with patch('documents.tasks.get_document_parser', return_value=mock_parser):
            with pytest.raises(ValueError):
                process_document_task(test_document.id)

    def test_process_document_task_nonexistent_document(self):
        """Test processing nonexistent document."""
        with pytest.raises(Document.DoesNotExist):
            process_document_task(99999)


@pytest.mark.django_db
@pytest.mark.celery
class TestExtractInformationTask:
    """Test cases for extract_information_task."""

    def test_extract_information_task_success(self, test_document, mock_gemini_service):
        """Test extracting information successfully."""
        text_content = "Resume text content..."

        with patch('documents.tasks.get_gemini_service', return_value=mock_gemini_service):
            result = extract_information_task(test_document.id, text_content)

            assert result['status'] == 'success'
            # Verify extracted information was created
            assert ExtractedInformation.objects.filter(document=test_document).count() > 0

    def test_extract_information_creates_correct_entries(
        self, test_document, mock_gemini_service
    ):
        """Test extracted information entries are created correctly."""
        text_content = "Resume text..."

        with patch('documents.tasks.get_gemini_service', return_value=mock_gemini_service):
            extract_information_task(test_document.id, text_content)

            # Check that various data types were extracted
            info_types = ExtractedInformation.objects.filter(
                document=test_document
            ).values_list('data_type', flat=True)

            assert 'skills' in info_types or 'education' in info_types

    def test_extract_information_marks_document_processed(
        self, test_document, mock_gemini_service
    ):
        """Test document is marked as processed."""
        text_content = "Resume text..."

        with patch('documents.tasks.get_gemini_service', return_value=mock_gemini_service):
            extract_information_task(test_document.id, text_content)

            test_document.refresh_from_db()
            assert test_document.is_processed is True
            assert test_document.processed_at is not None

    def test_extract_information_task_nonexistent_document(self, mock_gemini_service):
        """Test extracting information for nonexistent document."""
        with pytest.raises(Document.DoesNotExist):
            extract_information_task(99999, "Text content")
