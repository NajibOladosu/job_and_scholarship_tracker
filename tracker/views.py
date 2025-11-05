"""
Views for tracker app - application management, questions, and responses.
"""
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q, Count, Max
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.http import JsonResponse
from .models import Application, Question, Response, ApplicationStatus
from .forms import ApplicationForm, QuickApplicationForm, QuestionForm, ResponseForm, ApplicationFilterForm
from .tasks import scrape_url_task, batch_generate_responses_task, generate_response_task


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
