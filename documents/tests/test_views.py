"""
Tests for documents views.
"""
import pytest
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from documents.models import Document, ExtractedInformation


@pytest.mark.django_db
class TestDocumentUploadView:
    """Test cases for document upload view."""

    def test_upload_requires_login(self, client):
        """Test upload view requires authentication."""
        url = reverse('documents:upload')
        response = client.get(url)
        assert response.status_code == 302
        assert '/login' in response.url

    def test_upload_page_loads(self, authenticated_client):
        """Test upload page loads for authenticated user."""
        url = reverse('documents:upload')
        response = authenticated_client.get(url)
        assert response.status_code == 200

    def test_upload_document_success(self, authenticated_client, test_user):
        """Test uploading document successfully."""
        url = reverse('documents:upload')
        test_file = SimpleUploadedFile(
            "test_resume.pdf",
            b"Resume content",
            content_type="application/pdf"
        )
        data = {'document_type': 'resume', 'file': test_file}
        response = authenticated_client.post(url, data)
        assert response.status_code == 302

        # Verify document was created
        assert Document.objects.filter(user=test_user, document_type='resume').exists()


@pytest.mark.django_db
class TestDocumentListView:
    """Test cases for document list view."""

    def test_list_requires_login(self, client):
        """Test list view requires authentication."""
        url = reverse('documents:document_list')
        response = client.get(url)
        assert response.status_code == 302

    def test_list_shows_user_documents(self, authenticated_client, test_document):
        """Test list shows user's documents."""
        url = reverse('documents:document_list')
        response = authenticated_client.get(url)
        assert response.status_code == 200
        assert test_document.original_filename.encode() in response.content

    def test_list_doesnt_show_other_users_documents(
        self, authenticated_client, another_user, document_factory
    ):
        """Test list doesn't show other users' documents."""
        other_doc = document_factory(another_user, filename='other.pdf')
        url = reverse('documents:document_list')
        response = authenticated_client.get(url)
        assert other_doc.original_filename.encode() not in response.content


@pytest.mark.django_db
class TestDocumentDetailView:
    """Test cases for document detail view."""

    def test_detail_requires_login(self, client, test_document):
        """Test detail view requires authentication."""
        url = reverse('documents:document_detail', kwargs={'pk': test_document.pk})
        response = client.get(url)
        assert response.status_code == 302

    def test_detail_shows_document(self, authenticated_client, test_document):
        """Test detail view shows document."""
        url = reverse('documents:document_detail', kwargs={'pk': test_document.pk})
        response = authenticated_client.get(url)
        assert response.status_code == 200
        assert test_document.original_filename.encode() in response.content

    def test_detail_user_cannot_access_others_document(
        self, authenticated_client, another_user, document_factory
    ):
        """Test user cannot access another user's document."""
        other_doc = document_factory(another_user, filename='other.pdf')
        url = reverse('documents:document_detail', kwargs={'pk': other_doc.pk})
        response = authenticated_client.get(url)
        assert response.status_code == 404


@pytest.mark.django_db
class TestDocumentDeleteView:
    """Test cases for document delete view."""

    def test_delete_requires_login(self, client, test_document):
        """Test delete view requires authentication."""
        url = reverse('documents:document_delete', kwargs={'pk': test_document.pk})
        response = client.get(url)
        assert response.status_code == 302

    def test_delete_document_success(self, authenticated_client, test_document):
        """Test deleting document successfully."""
        doc_id = test_document.id
        url = reverse('documents:document_delete', kwargs={'pk': test_document.pk})
        response = authenticated_client.post(url)
        assert response.status_code == 302
        assert not Document.objects.filter(id=doc_id).exists()

    def test_delete_user_cannot_delete_others_document(
        self, authenticated_client, another_user, document_factory
    ):
        """Test user cannot delete another user's document."""
        other_doc = document_factory(another_user, filename='other.pdf')
        url = reverse('documents:document_delete', kwargs={'pk': other_doc.pk})
        response = authenticated_client.get(url)
        assert response.status_code == 404


@pytest.mark.django_db
class TestReprocessDocumentView:
    """Test cases for reprocess document view."""

    def test_reprocess_requires_login(self, client, test_document_processed):
        """Test reprocess view requires authentication."""
        url = reverse('documents:reprocess_document', kwargs={'pk': test_document_processed.pk})
        response = client.post(url)
        assert response.status_code == 302

    def test_reprocess_document_resets_status(
        self, authenticated_client, test_document_processed
    ):
        """Test reprocessing resets document status."""
        url = reverse('documents:reprocess_document', kwargs={'pk': test_document_processed.pk})
        authenticated_client.post(url)

        test_document_processed.refresh_from_db()
        assert test_document_processed.is_processed is False
        assert test_document_processed.processed_at is None
