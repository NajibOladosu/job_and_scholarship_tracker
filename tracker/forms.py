"""
Forms for tracker app (applications, questions, responses).
"""
from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Application, Question, Response, Note, Tag, Interview, Interviewer, Referral


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


class NoteForm(forms.ModelForm):
    """
    Form for creating and editing rich text notes.
    """
    class Meta:
        model = Note
        fields = ['title', 'content', 'application', 'is_pinned']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Note title...',
                'id': 'note-title'
            }),
            'content': forms.HiddenInput(attrs={
                'id': 'note-content-input'
            }),
            'application': forms.Select(attrs={
                'class': 'form-select',
                'id': 'note-application'
            }),
            'is_pinned': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
                'id': 'note-pinned'
            }),
        }
        labels = {
            'application': _('Link to Application (optional)'),
            'is_pinned': _('Pin to top')
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['application'].required = False
        self.fields['content'].required = False

        # Filter applications by user
        if user:
            self.fields['application'].queryset = Application.objects.filter(user=user).order_by('-created_at')
            self.fields['application'].empty_label = 'No application'


class TagForm(forms.ModelForm):
    """
    Form for creating and editing tags.
    """
    class Meta:
        model = Tag
        fields = ['name', 'color']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Remote, High Salary, Dream Company',
                'maxlength': 50
            }),
            'color': forms.TextInput(attrs={
                'class': 'form-control',
                'type': 'color',
                'placeholder': '#6366f1'
            }),
        }
        help_texts = {
            'color': _('Choose a color to visually identify this tag')
        }


class EnhancedApplicationFilterForm(forms.Form):
    """
    Enhanced form for filtering applications with multi-select and date ranges.
    """
    search = forms.CharField(
        required=False,
        label=_('Search'),
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search by title, company, description...'
        })
    )

    # Multi-select filters
    statuses = forms.MultipleChoiceField(
        required=False,
        label=_('Status'),
        choices=Application.STATUS_CHOICES,
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'form-check-input'
        })
    )

    application_types = forms.MultipleChoiceField(
        required=False,
        label=_('Application Type'),
        choices=Application.APPLICATION_TYPE_CHOICES,
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'form-check-input'
        })
    )

    priorities = forms.MultipleChoiceField(
        required=False,
        label=_('Priority'),
        choices=Application.PRIORITY_CHOICES,
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'form-check-input'
        })
    )

    tags = forms.MultipleChoiceField(
        required=False,
        label=_('Tags'),
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'form-check-input'
        })
    )

    # Date range filters
    deadline_from = forms.DateField(
        required=False,
        label=_('Deadline From'),
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )

    deadline_to = forms.DateField(
        required=False,
        label=_('Deadline To'),
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )

    created_from = forms.DateField(
        required=False,
        label=_('Created From'),
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )

    created_to = forms.DateField(
        required=False,
        label=_('Created To'),
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )

    # Additional filters
    has_deadline = forms.NullBooleanField(
        required=False,
        label=_('Has Deadline'),
        widget=forms.Select(attrs={
            'class': 'form-select'
        }, choices=[
            ('', _('All')),
            ('true', _('Yes')),
            ('false', _('No'))
        ])
    )

    is_overdue = forms.BooleanField(
        required=False,
        label=_('Show Only Overdue'),
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)

        # Populate tag choices from user's tags
        if user:
            user_tags = Tag.objects.filter(user=user).order_by('name')
            self.fields['tags'].choices = [(tag.id, tag.name) for tag in user_tags]


class InterviewForm(forms.ModelForm):
    """
    Form for creating and editing interviews.
    """
    class Meta:
        model = Interview
        fields = [
            'interview_type', 'scheduled_date', 'duration_minutes',
            'location', 'meeting_link', 'notes', 'status'
        ]
        widgets = {
            'interview_type': forms.Select(attrs={'class': 'form-select'}),
            'scheduled_date': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'duration_minutes': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '60',
                'min': '15',
                'step': '15'
            }),
            'location': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Physical address or room number'
            }),
            'meeting_link': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://zoom.us/j/...'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Interview preparation notes, topics to cover, feedback...'
            }),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }
        help_texts = {
            'duration_minutes': _('Expected interview duration in minutes'),
            'meeting_link': _('Video call link (Zoom, Teams, Google Meet, etc.)'),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['location'].required = False
        self.fields['meeting_link'].required = False
        self.fields['notes'].required = False
        self.fields['duration_minutes'].initial = 60


class QuickInterviewForm(forms.ModelForm):
    """
    Quick form for scheduling interviews with minimal fields.
    """
    class Meta:
        model = Interview
        fields = ['interview_type', 'scheduled_date', 'meeting_link']
        widgets = {
            'interview_type': forms.Select(attrs={
                'class': 'form-select'
            }),
            'scheduled_date': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'meeting_link': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://zoom.us/j/...'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['meeting_link'].required = False


class InterviewerForm(forms.ModelForm):
    """
    Form for adding interviewers to an interview.
    """
    class Meta:
        model = Interviewer
        fields = ['name', 'title', 'email', 'phone', 'linkedin_url', 'notes']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Full name'
            }),
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Job title (e.g., Senior Engineer)'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'email@company.com'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+1-555-0123'
            }),
            'linkedin_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://linkedin.com/in/...'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Background, research notes...'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].required = False
        self.fields['phone'].required = False
        self.fields['linkedin_url'].required = False
        self.fields['notes'].required = False


# Inline formset for adding multiple interviewers
InterviewerInlineFormSet = forms.inlineformset_factory(
    Interview,
    Interviewer,
    form=InterviewerForm,
    extra=1,
    can_delete=True,
    min_num=0,
    validate_min=True,
)


class ReferralForm(forms.ModelForm):
    """
    Form for adding referrals to applications.
    """
    class Meta:
        model = Referral
        fields = [
            'name', 'relationship', 'company', 'email',
            'phone', 'referred_date', 'notes'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Referrer full name'
            }),
            'relationship': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Former colleague, Friend, Mentor'
            }),
            'company': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Company name'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'email@company.com'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+1-555-0123'
            }),
            'referred_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Additional details about the referral...'
            }),
        }
        help_texts = {
            'relationship': _('Your relationship to the referrer'),
            'referred_date': _('Date when the referral was made'),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['phone'].required = False
        self.fields['notes'].required = False
