"""
API Serializers for the notifications app.
"""
from rest_framework import serializers
from .models import Notification, Reminder


class NotificationSerializer(serializers.ModelSerializer):
    """Serializer for Notification model."""

    class Meta:
        model = Notification
        fields = [
            'id', 'user', 'notification_type', 'title',
            'message', 'link', 'is_read', 'created_at'
        ]
        read_only_fields = ['user', 'created_at']


class ReminderSerializer(serializers.ModelSerializer):
    """Serializer for Reminder model."""
    application_title = serializers.CharField(source='application.position_title', read_only=True)
    application_company = serializers.CharField(source='application.company_name', read_only=True)

    class Meta:
        model = Reminder
        fields = [
            'id', 'application', 'application_title', 'application_company',
            'reminder_type', 'reminder_date', 'reminder_time',
            'message', 'is_sent', 'sent_at', 'created_at'
        ]
        read_only_fields = ['is_sent', 'sent_at', 'created_at']
