"""
Views for documents app - document upload, listing, and management.
"""
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, DeleteView
from .models import Document, ExtractedInformation
from .forms import DocumentUploadForm, DocumentFilterForm
from .tasks import process_document_task


@login_required
def document_upload_view(request):
    """
    Upload new document and trigger processing.
    """
    if request.method == 'POST':
        form = DocumentUploadForm(request.POST, request.FILES)
        if form.is_valid():
            document = form.save(commit=False)
            document.user = request.user
            document.save()

            # Trigger background processing
            process_document_task.delay(document.id)

            messages.success(
                request,
                f'{document.get_document_type_display()} uploaded successfully! Processing in background...'
            )
            return redirect('documents:document_list')
    else:
        form = DocumentUploadForm()

    context = {
        'title': 'Upload Document',
        'form': form,
    }
    return render(request, 'documents/upload.html', context)


class DocumentListView(LoginRequiredMixin, ListView):
    """
    List all user's documents with filtering.
    """
    model = Document
    template_name = 'documents/list.html'
    context_object_name = 'documents'
    paginate_by = 20

    def get_queryset(self):
        """
        Get user's documents with optional filtering.
        """
        queryset = Document.objects.filter(user=self.request.user).prefetch_related('extracted_info')

        # Apply filters
        filter_form = DocumentFilterForm(self.request.GET)
        if filter_form.is_valid():
            search = filter_form.cleaned_data.get('search')
            if search:
                queryset = queryset.filter(original_filename__icontains=search)

            document_type = filter_form.cleaned_data.get('document_type')
            if document_type:
                queryset = queryset.filter(document_type=document_type)

            processed_only = filter_form.cleaned_data.get('processed_only')
            if processed_only:
                queryset = queryset.filter(is_processed=True)

        return queryset.order_by('-uploaded_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'My Documents'
        context['filter_form'] = DocumentFilterForm(self.request.GET)

        # Get statistics
        user_documents = Document.objects.filter(user=self.request.user)
        context['stats'] = {
            'total': user_documents.count(),
            'processed': user_documents.filter(is_processed=True).count(),
            'pending': user_documents.filter(is_processed=False).count(),
            'resumes': user_documents.filter(document_type='resume').count(),
            'transcripts': user_documents.filter(document_type='transcript').count(),
        }

        return context


class DocumentDetailView(LoginRequiredMixin, DetailView):
    """
    View document details and extracted information.
    """
    model = Document
    template_name = 'documents/detail.html'
    context_object_name = 'document'

    def get_queryset(self):
        """
        Ensure user can only view their own documents.
        """
        return Document.objects.filter(user=self.request.user).prefetch_related('extracted_info')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = self.object.original_filename

        # Get extracted information organized by type
        extracted_info = {}
        for info in self.object.extracted_info.all():
            extracted_info[info.data_type] = {
                'content': info.content,
                'confidence': info.confidence_percentage,
            }

        context['extracted_info'] = extracted_info
        return context


class DocumentDeleteView(LoginRequiredMixin, DeleteView):
    """
    Delete a document.
    """
    model = Document
    template_name = 'documents/confirm_delete.html'
    success_url = reverse_lazy('documents:document_list')

    def get_queryset(self):
        """
        Ensure user can only delete their own documents.
        """
        return Document.objects.filter(user=self.request.user)

    def delete(self, request, *args, **kwargs):
        """
        Delete document and show success message.
        """
        document = self.get_object()
        messages.success(request, f'{document.original_filename} deleted successfully.')
        return super().delete(request, *args, **kwargs)


@login_required
def reprocess_document_view(request, pk):
    """
    Trigger reprocessing of a document.
    """
    document = get_object_or_404(Document, pk=pk, user=request.user)

    if request.method == 'POST':
        # Reset processing status
        document.is_processed = False
        document.processed_at = None
        document.save()

        # Delete existing extracted information
        document.extracted_info.all().delete()

        # Trigger reprocessing
        process_document_task.delay(document.id)

        messages.success(request, f'Reprocessing {document.original_filename}...')
        return redirect('documents:document_detail', pk=document.pk)

    return redirect('documents:document_detail', pk=document.pk)
