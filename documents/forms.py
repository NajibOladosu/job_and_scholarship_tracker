"""
Forms for documents app.
"""
from django import forms
from .models import Document


class DocumentUploadForm(forms.ModelForm):
    """
    Form for uploading documents.
    """
    class Meta:
        model = Document
        fields = ['document_type', 'file']
        widgets = {
            'document_type': forms.Select(attrs={
                'class': 'form-select',
                'required': True,
            }),
            'file': forms.FileInput(attrs={
                'class': 'form-control',
                'required': True,
                'accept': '.pdf,.doc,.docx,.txt,.png,.jpg,.jpeg',
            }),
        }
        help_texts = {
            'document_type': 'Select the type of document you\'re uploading',
            'file': 'Supported formats: PDF, DOCX, TXT, PNG, JPG (max 10MB)',
        }

    def clean_file(self):
        """
        Validate uploaded file.
        """
        file = self.cleaned_data.get('file')

        if file:
            # Check file size (max 10MB)
            max_size = 10 * 1024 * 1024  # 10MB in bytes
            if file.size > max_size:
                raise forms.ValidationError(
                    f'File size must not exceed 10MB. Your file is {round(file.size / (1024 * 1024), 2)}MB.'
                )

            # Check file extension
            allowed_extensions = ['.pdf', '.doc', '.docx', '.txt', '.png', '.jpg', '.jpeg']
            file_name = file.name.lower()
            if not any(file_name.endswith(ext) for ext in allowed_extensions):
                raise forms.ValidationError(
                    f'Unsupported file type. Allowed types: {", ".join(allowed_extensions)}'
                )

        return file


class DocumentFilterForm(forms.Form):
    """
    Form for filtering documents in list view.
    """
    document_type = forms.ChoiceField(
        choices=[('', 'All Types')] + list(Document.DOCUMENT_TYPE_CHOICES),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    processed_only = forms.BooleanField(
        required=False,
        label='Processed only',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search by filename...',
        })
    )
