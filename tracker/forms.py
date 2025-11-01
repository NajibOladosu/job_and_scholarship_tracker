"""
Forms for tracker app (applications, questions, responses).
"""
from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Application, Question, Response


class ApplicationForm(forms.ModelForm):
    """
    Form for creating and editing applications.
    """
    class Meta:
        model = Application
        fields = [
            'application_type', 'title', 'company_or_institution',
            'url', 'description', 'deadline', 'status', 'priority', 'notes'
        ]
        widgets = {
            'application_type': forms.Select(attrs={'class': 'form-select'}),
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Senior Software Engineer'}),
            'company_or_institution': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Google, Harvard University'}),
            'url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://...'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Job or scholarship description (optional if providing URL)'}),
            'deadline': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'priority': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Any additional notes...'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make some fields optional
        self.fields['description'].required = False
        self.fields['deadline'].required = False
        self.fields['notes'].required = False
        self.fields['url'].required = False


class QuickApplicationForm(forms.ModelForm):
    """
    Quick form for creating applications with just URL.
    AI will extract the rest.
    """
    class Meta:
        model = Application
        fields = ['application_type', 'url']
        widgets = {
            'application_type': forms.Select(attrs={'class': 'form-select'}),
            'url': forms.URLInput(attrs={
                'class': 'form-control form-control-lg',
                'placeholder': 'Paste application URL here...',
                'autofocus': True
            }),
        }


class QuestionForm(forms.ModelForm):
    """
    Form for manually adding/editing questions.
    """
    class Meta:
        model = Question
        fields = ['question_text', 'question_type', 'is_required', 'order']
        widgets = {
            'question_text': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Enter the application question...'
            }),
            'question_type': forms.Select(attrs={'class': 'form-select'}),
            'is_required': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'order': forms.NumberInput(attrs={'class': 'form-control'}),
        }


class ResponseForm(forms.ModelForm):
    """
    Form for editing AI-generated or custom responses.
    """
    class Meta:
        model = Response
        fields = ['edited_response']
        widgets = {
            'edited_response': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 8,
                'placeholder': 'Edit your response here...'
            }),
        }
        labels = {
            'edited_response': _('Your Response')
        }


class ApplicationFilterForm(forms.Form):
    """
    Form for filtering applications in dashboard.
    """
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search applications...'
        })
    )
    application_type = forms.ChoiceField(
        required=False,
        choices=[('', 'All Types')] + list(Application.APPLICATION_TYPE_CHOICES),
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    status = forms.ChoiceField(
        required=False,
        choices=[('', 'All Statuses')] + list(Application.STATUS_CHOICES),
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    priority = forms.ChoiceField(
        required=False,
        choices=[('', 'All Priorities')] + list(Application.PRIORITY_CHOICES),
        widget=forms.Select(attrs={'class': 'form-select'})
    )
