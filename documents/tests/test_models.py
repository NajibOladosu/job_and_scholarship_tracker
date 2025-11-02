"""
Tests for documents models.
"""
import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from documents.models import Document, ExtractedInformation


@pytest.mark.django_db
class TestDocumentModel:
    """Test cases for Document model."""

    def test_create_document(self, test_user):
        """Test creating a document."""
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
            file_size=len(file_content)
        )

        assert document.user == test_user
        assert document.document_type == 'resume'
        assert document.original_filename == 'test_resume.pdf'
        assert document.file_size == len(file_content)
        assert document.is_processed is False

    def test_document_str_representation(self, test_document):
        """Test document string representation."""
        expected = f"{test_document.get_document_type_display()} - {test_document.original_filename}"
        assert str(test_document) == expected

    def test_document_save_sets_original_filename(self, test_user):
        """Test save method sets original_filename automatically."""
        file_content = b"Test content"
        test_file = SimpleUploadedFile(
            "auto_name.pdf",
            file_content,
            content_type="application/pdf"
        )

        document = Document.objects.create(
            user=test_user,
            document_type='resume',
            file=test_file
        )

        assert document.original_filename == 'auto_name.pdf'

    def test_document_save_sets_file_size(self, test_user):
        """Test save method sets file_size automatically."""
        file_content = b"Test content with some length"
        test_file = SimpleUploadedFile(
            "test.pdf",
            file_content,
            content_type="application/pdf"
        )

        document = Document.objects.create(
            user=test_user,
            document_type='resume',
            file=test_file
        )

        assert document.file_size == len(file_content)

    def test_document_file_size_mb_property(self, test_user):
        """Test file_size_mb property."""
        file_content = b"x" * (2 * 1024 * 1024)  # 2MB
        test_file = SimpleUploadedFile(
            "large.pdf",
            file_content,
            content_type="application/pdf"
        )

        document = Document.objects.create(
            user=test_user,
            document_type='resume',
            file=test_file
        )

        assert document.file_size_mb == 2.0

    def test_document_file_size_mb_zero_when_no_size(self, test_user):
        """Test file_size_mb returns 0 when file_size is None."""
        test_file = SimpleUploadedFile(
            "test.pdf",
            b"content",
            content_type="application/pdf"
        )

        document = Document.objects.create(
            user=test_user,
            document_type='resume',
            file=test_file,
            file_size=None
        )

        assert document.file_size_mb == 0

    def test_document_ordering(self, test_user, document_factory):
        """Test documents are ordered by uploaded_at descending."""
        doc1 = document_factory(test_user, filename='first.pdf')
        doc2 = document_factory(test_user, filename='second.pdf')

        documents = list(Document.objects.all())
        assert documents[0] == doc2  # Most recent first
        assert documents[1] == doc1

    def test_document_cascade_delete_extracted_info(self, test_document_processed, test_extracted_info):
        """Test extracted info is deleted when document is deleted."""
        info_id = test_extracted_info.id
        test_document_processed.delete()
        assert not ExtractedInformation.objects.filter(id=info_id).exists()

    def test_user_document_path_function(self, test_user):
        """Test user_document_path generates correct path."""
        from documents.models import user_document_path

        test_file = SimpleUploadedFile("test.pdf", b"content")
        document = Document(user=test_user, file=test_file)

        path = user_document_path(document, "myresume.pdf")
        assert path == f'documents/user_{test_user.id}/myresume.pdf'


@pytest.mark.django_db
class TestExtractedInformationModel:
    """Test cases for ExtractedInformation model."""

    def test_create_extracted_information(self, test_document_processed):
        """Test creating extracted information."""
        info = ExtractedInformation.objects.create(
            document=test_document_processed,
            data_type='education',
            content={'degree': 'BS', 'institution': 'Test University'},
            confidence_score=0.95
        )

        assert info.document == test_document_processed
        assert info.data_type == 'education'
        assert info.content == {'degree': 'BS', 'institution': 'Test University'}
        assert info.confidence_score == 0.95

    def test_extracted_info_str_representation(self, test_extracted_info):
        """Test extracted information string representation."""
        result = str(test_extracted_info)
        assert test_extracted_info.get_data_type_display() in result
        assert test_extracted_info.document.original_filename in result

    def test_extracted_info_confidence_percentage_property(self, test_document_processed):
        """Test confidence_percentage property."""
        info = ExtractedInformation.objects.create(
            document=test_document_processed,
            data_type='skills',
            content={'skills': ['Python']},
            confidence_score=0.856
        )

        assert info.confidence_percentage == 85.6

    def test_extracted_info_ordering(self, test_document_processed):
        """Test extracted info is ordered by extracted_at descending."""
        info1 = ExtractedInformation.objects.create(
            document=test_document_processed,
            data_type='skills',
            content={'skills': ['Python']}
        )
        info2 = ExtractedInformation.objects.create(
            document=test_document_processed,
            data_type='education',
            content={'degree': 'BS'}
        )

        infos = list(ExtractedInformation.objects.all())
        assert infos[0] == info2  # Most recent first
        assert infos[1] == info1

    def test_extracted_info_json_content(self, test_document_processed):
        """Test JSON content can store complex data."""
        complex_content = {
            'education': [
                {'institution': 'University A', 'degree': 'BS', 'year': 2020},
                {'institution': 'University B', 'degree': 'MS', 'year': 2022}
            ],
            'gpa': 3.8,
            'honors': ['Dean\'s List', 'Cum Laude']
        }

        info = ExtractedInformation.objects.create(
            document=test_document_processed,
            data_type='education',
            content=complex_content,
            confidence_score=0.9
        )

        # Retrieve and verify
        info.refresh_from_db()
        assert info.content == complex_content
        assert len(info.content['education']) == 2
        assert info.content['gpa'] == 3.8

    def test_extracted_info_all_data_types(self, test_document_processed):
        """Test all data type choices are valid."""
        for data_type, label in ExtractedInformation.DATA_TYPE_CHOICES:
            info = ExtractedInformation.objects.create(
                document=test_document_processed,
                data_type=data_type,
                content={'test': 'data'}
            )
            assert info.data_type == data_type
            assert info.get_data_type_display() == label
            info.delete()  # Clean up for next iteration
