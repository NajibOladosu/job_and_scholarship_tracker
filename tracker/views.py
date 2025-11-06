"""
Views for tracker app - application management, questions, and responses.
"""
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q, Count, Max
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from django.views.decorators.cache import cache_page
from django.core.cache import cache
from datetime import datetime
from .models import Application, Question, Response, ApplicationStatus, Note, Tag
from .forms import (
    ApplicationForm, QuickApplicationForm, QuestionForm, ResponseForm,
    ApplicationFilterForm, NoteForm, TagForm, EnhancedApplicationFilterForm
)
from .tasks import scrape_url_task, batch_generate_responses_task, generate_response_task
from .utils.analytics import calculate_summary_stats, generate_sankey_data, get_timeline_data
import json


@login_required
def dashboard_view(request):
    """
    Main dashboard showing user's applications.
    """
    # Get user's applications
    # Note: We don't annotate question_count here because Application model has a property with that name
    # The template will use the property instead
    applications = Application.objects.filter(user=request.user).order_by('-created_at')

    # Apply filters
    filter_form = ApplicationFilterForm(request.GET)
    if filter_form.is_valid():
        search = filter_form.cleaned_data.get('search')
        if search:
            applications = applications.filter(
                Q(title__icontains=search) |
                Q(company_or_institution__icontains=search) |
                Q(description__icontains=search)
            )

        app_type = filter_form.cleaned_data.get('application_type')
        if app_type:
            applications = applications.filter(application_type=app_type)

        status = filter_form.cleaned_data.get('status')
        if status:
            applications = applications.filter(status=status)

        priority = filter_form.cleaned_data.get('priority')
        if priority:
            applications = applications.filter(priority=priority)

    # Get statistics
    stats = {
        'total': applications.count(),
        'draft': applications.filter(status='draft').count(),
        'submitted': applications.filter(status='submitted').count(),
        'in_review': applications.filter(status='in_review').count(),
        'interview': applications.filter(status='interview').count(),
        'offer': applications.filter(status='offer').count(),
    }

    context = {
        'title': 'Dashboard',
        'applications': applications[:50],  # Limit for performance
        'filter_form': filter_form,
        'stats': stats,
    }
    return render(request, 'tracker/dashboard.html', context)


class ApplicationCreateView(LoginRequiredMixin, CreateView):
    """
    Create new application.
    """
    model = Application
    form_class = ApplicationForm
    template_name = 'tracker/application_form.html'

    def form_valid(self, form):
        form.instance.user = self.request.user
        response = super().form_valid(form)

        # If URL provided, trigger scraping task
        if form.instance.url:
            messages.info(
                self.request,
                'Application created! Processing URL to extract questions...'
            )
            scrape_url_task.delay(form.instance.id)
        else:
            messages.success(self.request, 'Application created successfully!')

        return response

    def get_success_url(self):
        return reverse('tracker:application_detail', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Create Application'
        return context


@login_required
def quick_application_create_view(request):
    """
    Quick application creation with just URL.
    """
    if request.method == 'POST':
        form = QuickApplicationForm(request.POST)
        if form.is_valid():
            application = form.save(commit=False)
            application.user = request.user
            application.title = 'Processing...'  # Placeholder
            application.company_or_institution = 'Processing...'  # Placeholder
            application.save()

            # Trigger scraping task
            messages.success(
                request,
                'Processing application URL! We\'ll extract the details and questions for you.'
            )
            scrape_url_task.delay(application.id)

            return redirect('tracker:application_detail', pk=application.pk)
    else:
        form = QuickApplicationForm()

    return render(request, 'tracker/quick_application_form.html', {
        'title': 'Add Application',
        'form': form
    })


class ApplicationDetailView(LoginRequiredMixin, DetailView):
    """
    View application details with questions and responses.
    """
    model = Application
    template_name = 'tracker/application_detail.html'
    context_object_name = 'application'

    def get_queryset(self):
        return Application.objects.filter(user=self.request.user).prefetch_related(
            'questions__response',
            'status_history'
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        application = self.object

        # Get questions with responses
        questions = application.questions.all().order_by('order', 'created_at')

        context.update({
            'title': application.title,
            'questions': questions,
            'status_history': application.status_history.all()[:10],
            'can_generate_responses': questions.exists(),
        })
        return context


class ApplicationUpdateView(LoginRequiredMixin, UpdateView):
    """
    Update application details.
    """
    model = Application
    form_class = ApplicationForm
    template_name = 'tracker/application_form.html'

    def get_queryset(self):
        return Application.objects.filter(user=self.request.user)

    def form_valid(self, form):
        # Track status changes
        if 'status' in form.changed_data:
            old_status = Application.objects.get(pk=self.object.pk).status
            new_status = form.cleaned_data['status']

            if old_status != new_status:
                ApplicationStatus.objects.create(
                    application=self.object,
                    status=new_status,
                    changed_by='user_update',
                    notes=f'Status changed from {old_status} to {new_status}'
                )

        messages.success(self.request, 'Application updated successfully!')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('tracker:application_detail', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Edit {self.object.title}'
        return context


class ApplicationDeleteView(LoginRequiredMixin, DeleteView):
    """
    Delete application.
    """
    model = Application
    template_name = 'tracker/application_confirm_delete.html'
    success_url = reverse_lazy('tracker:dashboard')

    def get_queryset(self):
        return Application.objects.filter(user=self.request.user)

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Application deleted successfully.')
        return super().delete(request, *args, **kwargs)


@login_required
def add_question_view(request, application_pk):
    """
    Manually add question to application.
    """
    application = get_object_or_404(Application, pk=application_pk, user=request.user)

    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.application = application
            question.is_extracted = False  # Manually added
            question.save()
            messages.success(request, 'Question added successfully!')
            return redirect('tracker:application_detail', pk=application.pk)
    else:
        # Set default order
        max_order = application.questions.aggregate(Max('order'))['order__max'] or 0
        form = QuestionForm(initial={'order': max_order + 1})

    return render(request, 'tracker/question_form.html', {
        'title': 'Add Question',
        'form': form,
        'application': application
    })


@login_required
def edit_response_view(request, question_pk):
    """
    Edit response to a question.
    """
    question = get_object_or_404(
        Question.objects.select_related('application'),
        pk=question_pk,
        application__user=request.user
    )

    # Get or create response
    response, created = Response.objects.get_or_create(question=question)

    if request.method == 'POST':
        form = ResponseForm(request.POST, instance=response)
        if form.is_valid():
            form.save()
            messages.success(request, 'Response saved successfully!')
            return redirect('tracker:application_detail', pk=question.application.pk)
    else:
        form = ResponseForm(instance=response)

    context = {
        'title': 'Edit Response',
        'form': form,
        'question': question,
        'response': response
    }
    return render(request, 'tracker/response_form.html', context)


@login_required
def generate_responses_view(request, application_pk):
    """
    Generate AI responses for all questions in application.
    Supports regeneration via 'regenerate' POST parameter.
    """
    application = get_object_or_404(Application, pk=application_pk, user=request.user)

    if request.method == 'POST':
        # Check if user has processed documents
        from documents.models import Document
        processed_docs = Document.objects.filter(user=request.user, is_processed=True).exists()

        if not processed_docs:
            messages.warning(
                request,
                'Please upload and process at least one document (resume, transcript, etc.) before generating responses.'
            )
            return redirect('documents:upload')

        # Check if regenerate flag is set
        regenerate = request.POST.get('regenerate', 'false').lower() == 'true'

        # Trigger batch generation task
        batch_generate_responses_task.delay(application.id, regenerate=regenerate)

        if regenerate:
            messages.success(
                request,
                'Regenerating ALL responses! This may take a few moments. Refresh the page to see updates.'
            )
        else:
            messages.success(
                request,
                'Generating responses for all questions! This may take a few moments. Refresh the page to see updates.'
            )
        return redirect('tracker:application_detail', pk=application.pk)

    return redirect('tracker:application_detail', pk=application.pk)


@login_required
def regenerate_response_view(request, question_pk):
    """
    Regenerate AI response for a single question.
    """
    question = get_object_or_404(
        Question,
        pk=question_pk,
        application__user=request.user
    )

    if request.method == 'POST':
        # Trigger generation task
        generate_response_task.delay(question.id)
        messages.success(request, 'Regenerating response! Refresh the page in a moment to see the new response.')
        return redirect('tracker:application_detail', pk=question.application.pk)

    return redirect('tracker:application_detail', pk=question.application.pk)


# ========== Note Views ==========

class NoteListView(LoginRequiredMixin, ListView):
    """
    List all notes with search and filter capabilities.
    """
    model = Note
    template_name = 'tracker/note_list.html'
    context_object_name = 'notes'
    paginate_by = 20

    def get_queryset(self):
        queryset = Note.objects.filter(user=self.request.user).select_related('application')

        # Search
        search = self.request.GET.get('search', '').strip()
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(plain_text__icontains=search)
            )

        # Filter by application
        application_id = self.request.GET.get('application')
        if application_id:
            queryset = queryset.filter(application_id=application_id)

        # Filter pinned
        show_pinned = self.request.GET.get('pinned')
        if show_pinned == 'true':
            queryset = queryset.filter(is_pinned=True)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'My Notes'
        context['search'] = self.request.GET.get('search', '')
        context['applications'] = Application.objects.filter(user=self.request.user).order_by('-created_at')
        return context


class NoteCreateView(LoginRequiredMixin, CreateView):
    """
    Create new note with rich text editor.
    """
    model = Note
    form_class = NoteForm
    template_name = 'tracker/note_editor.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, 'Note created successfully!')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('tracker:note_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Create Note'
        context['is_new'] = True
        return context


class NoteUpdateView(LoginRequiredMixin, UpdateView):
    """
    Update existing note.
    """
    model = Note
    form_class = NoteForm
    template_name = 'tracker/note_editor.html'

    def get_queryset(self):
        return Note.objects.filter(user=self.request.user)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, 'Note updated successfully!')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('tracker:note_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Edit: {self.object.title}'
        context['is_new'] = False
        return context


class NoteDeleteView(LoginRequiredMixin, DeleteView):
    """
    Delete note.
    """
    model = Note
    template_name = 'tracker/note_confirm_delete.html'
    success_url = reverse_lazy('tracker:note_list')

    def get_queryset(self):
        return Note.objects.filter(user=self.request.user)

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Note deleted successfully.')
        return super().delete(request, *args, **kwargs)


@login_required
@require_POST
def note_autosave_api(request):
    """
    API endpoint for auto-saving notes.
    Accepts JSON with note_id, title, and content.
    """
    try:
        data = json.loads(request.body)
        note_id = data.get('note_id')
        title = data.get('title', 'Untitled Note').strip()
        content = data.get('content', '')

        if not title:
            title = 'Untitled Note'

        if note_id:
            # Update existing note
            note = get_object_or_404(Note, pk=note_id, user=request.user)
            note.title = title
            note.content = content
            note.save()
            message = 'Note saved'
        else:
            # Create new note
            note = Note.objects.create(
                user=request.user,
                title=title,
                content=content
            )
            message = 'Note created'

        return JsonResponse({
            'success': True,
            'message': message,
            'note_id': note.id,
            'updated_at': note.updated_at.isoformat()
        })

    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'Invalid JSON'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)


@login_required
@require_POST
def note_toggle_pin_api(request, pk):
    """
    API endpoint to toggle note pin status.
    """
    try:
        note = get_object_or_404(Note, pk=pk, user=request.user)
        note.is_pinned = not note.is_pinned
        note.save()

        return JsonResponse({
            'success': True,
            'is_pinned': note.is_pinned
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)


# ========== Analytics Views ==========

@login_required
def analytics_dashboard_view(request):
    """
    Analytics dashboard with visualizations and statistics.

    Displays:
    - Summary statistics (total apps, status breakdown, conversion rates)
    - Sankey diagram for application flow
    - Timeline of upcoming deadlines and interviews
    """
    # Get time filter (default: 60 days)
    days_filter = int(request.GET.get('days', 60))
    if days_filter not in [7, 30, 60]:
        days_filter = 60

    # Calculate summary statistics (with caching)
    cache_key = f'analytics_stats_{request.user.id}_{days_filter}'
    stats = cache.get(cache_key)

    if stats is None:
        stats = calculate_summary_stats(request.user, days=days_filter)
        # Cache for 5 minutes
        cache.set(cache_key, stats, 300)

    context = {
        'title': 'Analytics Dashboard',
        'stats': stats,
        'days_filter': days_filter,
    }
    return render(request, 'tracker/analytics.html', context)


@login_required
def sankey_data_api(request):
    """
    API endpoint to get Sankey diagram data.

    Returns JSON data formatted for Plotly Sankey diagram:
    {
        'node': {
            'label': [...],
            'color': [...],
            'customdata': [...]
        },
        'link': {
            'source': [...],
            'target': [...],
            'value': [...],
            'color': [...]
        }
    }
    """
    # Cache Sankey data for 5 minutes
    cache_key = f'sankey_data_{request.user.id}'
    data = cache.get(cache_key)

    if data is None:
        data = generate_sankey_data(request.user)
        cache.set(cache_key, data, 300)

    return JsonResponse(data, safe=False)


@login_required
def timeline_data_api(request):
    """
    API endpoint to get timeline event data.

    Query parameters:
    - days: Number of days ahead to show (default: 30)

    Returns JSON array of timeline events:
    [
        {
            'id': 1,
            'title': 'Software Engineer',
            'company': 'Tech Corp',
            'date': '2024-01-15T09:00:00Z',
            'type': 'interview',
            'status': 'interview',
            'priority': 'high',
            'is_overdue': false,
            'is_today': false,
            'is_this_week': true,
            'days_until': 3
        },
        ...
    ]
    """
    days_ahead = int(request.GET.get('days', 30))

    # Limit to reasonable range
    if days_ahead < 7:
        days_ahead = 7
    elif days_ahead > 90:
        days_ahead = 90

    # Cache timeline data for 5 minutes
    cache_key = f'timeline_data_{request.user.id}_{days_ahead}'
    data = cache.get(cache_key)

    if data is None:
        data = get_timeline_data(request.user, days_ahead=days_ahead)
        cache.set(cache_key, data, 300)

    return JsonResponse(data, safe=False)
