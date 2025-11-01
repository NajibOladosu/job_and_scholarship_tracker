"""
Forms for notifications app (reminders and notification filters).
"""
from django import forms
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from .models import Reminder, Notification


class ReminderForm(forms.ModelForm):
    """
    Form for creating and editing reminders.
    """
    class Meta:
        model = Reminder
        fields = ['application', 'reminder_type', 'message', 'scheduled_for']
        widgets = {
            'application': forms.Select(attrs={'class': 'form-select'}),
            'reminder_type': forms.Select(attrs={'class': 'form-select'}),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Enter reminder message...'
            }),
            'scheduled_for': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
        }

    def __init__(self, user=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter applications to only show user's applications
        if user:
            self.fields['application'].queryset = user.applications.all()

        # Set help texts
        self.fields['scheduled_for'].help_text = _('When you want to be reminded')
        self.fields['message'].help_text = _('What you want to be reminded about')

    def clean_scheduled_for(self):
        """
        Validate that scheduled_for is in the future.
        """
        scheduled_for = self.cleaned_data.get('scheduled_for')
        if scheduled_for and scheduled_for < timezone.now():
            raise forms.ValidationError(
                _('Reminder time must be in the future.')
            )
        return scheduled_for


class NotificationFilterForm(forms.Form):
    """
    Form for filtering notifications.
    """
    notification_type = forms.ChoiceField(
        required=False,
        choices=[('', 'All Types')] + list(Notification.NOTIFICATION_TYPE_CHOICES),
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    unread_only = forms.BooleanField(
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label=_('Show unread only')
    )


class ReminderFilterForm(forms.Form):
    """
    Form for filtering reminders.
    """
    reminder_type = forms.ChoiceField(
        required=False,
        choices=[('', 'All Types')] + list(Reminder.REMINDER_TYPE_CHOICES),
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    status = forms.ChoiceField(
        required=False,
        choices=[
            ('', 'All Reminders'),
            ('pending', 'Pending'),
            ('sent', 'Sent'),
            ('overdue', 'Overdue'),
        ],
        widget=forms.Select(attrs={'class': 'form-select'}),
        label=_('Status')
    )
