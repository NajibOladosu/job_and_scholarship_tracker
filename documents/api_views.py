"""
API Views for the documents app.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser

from .models import Document, ExtractedInformation
from .serializers import (
    DocumentListSerializer, DocumentDetailSerializer,
    DocumentUploadSerializer, ExtractedInformationSerializer
)


class DocumentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Document model.
    Handles document upload, viewing, and deletion.
    """
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        """Return documents for the current user only."""
        return Document.objects.filter(user=self.request.user).select_related('user').prefetch_related('extracted_info')

    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'list':
            return DocumentListSerializer
        elif self.action in ['create', 'upload']:
            return DocumentUploadSerializer
        return DocumentDetailSerializer

    @action(detail=False, methods=['post'])
    def upload(self, request):
        """Upload a new document."""
        serializer = DocumentUploadSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            document = serializer.save()
            # Trigger background processing task
            from .tasks import process_document
            process_document.delay(document.id)

            return Response(
                DocumentDetailSerializer(document, context={'request': request}).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'])
    def extracted_info(self, request, pk=None):
        """Get extracted information for a document."""
        document = self.get_object()
        try:
            extracted_info = document.extracted_info
            serializer = ExtractedInformationSerializer(extracted_info)
            return Response(serializer.data)
        except ExtractedInformation.DoesNotExist:
            return Response(
                {'message': 'Document has not been processed yet'},
                status=status.HTTP_404_NOT_FOUND
            )
