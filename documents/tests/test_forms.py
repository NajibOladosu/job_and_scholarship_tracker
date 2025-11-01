"""
Tests for documents forms.
"""
import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from documents.forms import DocumentUploadForm, DocumentFilterForm


@pytest.mark.django_db
class TestDocumentUploadForm:
    """Test cases for DocumentUploadForm."""

    def test_valid_upload_form(self):
        """Test form with valid data."""
        test_file = SimpleUploadedFile(
            "test_resume.pdf",
            b"Test content",
            content_type="application/pdf"
        )
        form_data = {'document_type': 'resume'}
        form = DocumentUploadForm(data=form_data, files={'file': test_file})
        assert form.is_valid()

    def test_upload_form_file_too_large(self):
        """Test form rejects files larger than 10MB."""
        # Create 11MB file
        large_content = b"x" * (11 * 1024 * 1024)
        test_file = SimpleUploadedFile(
            "large.pdf",
            large_content,
            content_type="application/pdf"
        )
        form_data = {'document_type': 'resume'}
        form = DocumentUploadForm(data=form_data, files={'file': test_file})
        assert not form.is_valid()
        assert 'file' in form.errors
        assert '10MB' in str(form.errors['file'])

    def test_upload_form_invalid_file_type(self):
        """Test form rejects invalid file types."""
        test_file = SimpleUploadedFile(
            "test.exe",
            b"Executable content",
            content_type="application/x-msdownload"
        )
        form_data = {'document_type': 'resume'}
        form = DocumentUploadForm(data=form_data, files={'file': test_file})
        assert not form.is_valid()
        assert 'file' in form.errors

    def test_upload_form_valid_file_types(self):
        """Test form accepts all valid file types."""
        valid_files = [
            ('test.pdf', 'application/pdf'),
            ('test.docx', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'),
            ('test.txt', 'text/plain'),
            ('test.png', 'image/png'),
            ('test.jpg', 'image/jpeg'),
        ]

        for filename, content_type in valid_files:
            test_file = SimpleUploadedFile(filename, b"Content", content_type=content_type)
            form_data = {'document_type': 'resume'}
            form = DocumentUploadForm(data=form_data, files={'file': test_file})
            assert form.is_valid(), f"Failed for {filename}"

    def test_upload_form_missing_file(self):
        """Test form requires file."""
        form_data = {'document_type': 'resume'}
        form = DocumentUploadForm(data=form_data)
        assert not form.is_valid()
        assert 'file' in form.errors


@pytest.mark.django_db
class TestDocumentFilterForm:
    """Test cases for DocumentFilterForm."""

    def test_valid_filter_form_empty(self):
        """Test form with no filters."""
        form = DocumentFilterForm(data={})
        assert form.is_valid()

    def test_filter_form_with_document_type(self):
        """Test form with document type filter."""
        form = DocumentFilterForm(data={'document_type': 'resume'})
        assert form.is_valid()
        assert form.cleaned_data['document_type'] == 'resume'

    def test_filter_form_with_processed_only(self):
        """Test form with processed only filter."""
        form = DocumentFilterForm(data={'processed_only': True})
        assert form.is_valid()
        assert form.cleaned_data['processed_only'] is True

    def test_filter_form_with_search(self):
        """Test form with search query."""
        form = DocumentFilterForm(data={'search': 'resume'})
        assert form.is_valid()
        assert form.cleaned_data['search'] == 'resume'

    def test_filter_form_all_fields_optional(self):
        """Test all filter form fields are optional."""
        form = DocumentFilterForm(data={})
        assert form.is_valid()
        for field in form.fields.values():
            assert field.required is False
