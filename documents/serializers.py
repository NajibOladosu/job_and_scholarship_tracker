"""
API Serializers for the documents app.
"""
from rest_framework import serializers
from .models import Document, ExtractedInformation


class ExtractedInformationSerializer(serializers.ModelSerializer):
    """Serializer for ExtractedInformation model."""

    class Meta:
        model = ExtractedInformation
        fields = [
            'id', 'document', 'full_text', 'skills', 'education',
            'experience', 'certifications', 'languages',
            'extracted_at'
        ]
        read_only_fields = ['extracted_at']


class DocumentListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for document list views."""
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = Document
        fields = [
            'id', 'document_type', 'original_filename',
            'file_size', 'is_processed', 'uploaded_at',
            'processed_at', 'file_url'
        ]
        read_only_fields = ['uploaded_at', 'processed_at']

    def get_file_url(self, obj):
        request = self.context.get('request')
        if obj.file and request:
            return request.build_absolute_uri(obj.file.url)
        return None


class DocumentDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for single document views."""
    extracted_info = ExtractedInformationSerializer(read_only=True)
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = Document
        fields = [
            'id', 'user', 'document_type', 'file', 'original_filename',
            'uploaded_at', 'file_size', 'is_processed', 'processed_at',
            'extracted_info', 'file_url'
        ]
        read_only_fields = ['user', 'uploaded_at', 'processed_at', 'is_processed']

    def get_file_url(self, obj):
        request = self.context.get('request')
        if obj.file and request:
            return request.build_absolute_uri(obj.file.url)
        return None


class DocumentUploadSerializer(serializers.ModelSerializer):
    """Serializer for uploading documents."""

    class Meta:
        model = Document
        fields = ['document_type', 'file', 'original_filename']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        # Save file size
        if 'file' in validated_data:
            validated_data['file_size'] = validated_data['file'].size
        return super().create(validated_data)

    def validate_file(self, value):
        """Validate file size and type."""
        # Max file size: 10MB
        max_size = 10 * 1024 * 1024
        if value.size > max_size:
            raise serializers.ValidationError("File size cannot exceed 10MB.")

        # Allowed file types
        allowed_extensions = ['.pdf', '.doc', '.docx', '.jpg', '.jpeg', '.png']
        ext = value.name.lower().split('.')[-1] if '.' in value.name else ''
        if f'.{ext}' not in allowed_extensions:
            raise serializers.ValidationError(
                f"File type not supported. Allowed types: {', '.join(allowed_extensions)}"
            )

        return value
