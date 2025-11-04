"""
Views for notifications app - manage notifications and reminders.
"""
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.utils import timezone
from .models import Notification, Reminder
from .forms import ReminderForm, NotificationFilterForm, ReminderFilterForm


@login_required
def notification_list_view(request):
    """
    List all user's notifications with filtering and date grouping.
    """
    from datetime import datetime, timedelta

    # Get user's notifications
    notifications = Notification.objects.filter(user=request.user).select_related('user')

    # Get filter type from query params
    filter_type = request.GET.get('filter', 'all')

    # Apply filters
    if filter_type == 'unread':
        notifications = notifications.filter(is_read=False)
    elif filter_type == 'read':
        notifications = notifications.filter(is_read=True)

    # Get counts
    unread_count = Notification.objects.filter(user=request.user, is_read=False).count()
    total_count = Notification.objects.filter(user=request.user).count()
    read_count = total_count - unread_count

    # Group notifications by date
    now = timezone.now()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    yesterday_start = today_start - timedelta(days=1)
    week_start = today_start - timedelta(days=7)

    # Get notifications for each group
    today_notifications = notifications.filter(created_at__gte=today_start).order_by('-created_at')
    yesterday_notifications = notifications.filter(
        created_at__gte=yesterday_start,
        created_at__lt=today_start
    ).order_by('-created_at')
    this_week_notifications = notifications.filter(
        created_at__gte=week_start,
        created_at__lt=yesterday_start
    ).order_by('-created_at')
    older_notifications = notifications.filter(created_at__lt=week_start).order_by('-created_at')[:50]

    context = {
        'title': 'Notifications',
        'notifications': notifications,
        'today_notifications': today_notifications,
        'yesterday_notifications': yesterday_notifications,
        'this_week_notifications': this_week_notifications,
        'older_notifications': older_notifications,
        'filter_type': filter_type,
        'unread_count': unread_count,
        'total_count': total_count,
        'read_count': read_count,
    }
    return render(request, 'notifications/notification_list.html', context)


@login_required
def notification_mark_read_view(request, pk):
    """
    Mark a notification as read (AJAX-friendly).
    """
    notification = get_object_or_404(Notification, pk=pk, user=request.user)

    if request.method == 'POST':
        notification.mark_as_read()

        # Return JSON for AJAX requests
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': 'Notification marked as read.',
                'read_at': notification.read_at.isoformat() if notification.read_at else None,
            })

        messages.success(request, 'Notification marked as read.')
        return redirect('notifications:list')

    return redirect('notifications:list')


@login_required
def notification_mark_all_read_view(request):
    """
    Mark all user's notifications as read.
    """
    if request.method == 'POST':
        # Get all unread notifications
        unread_notifications = Notification.objects.filter(
            user=request.user,
            is_read=False
        )

        # Mark all as read
        count = 0
        for notification in unread_notifications:
            notification.mark_as_read()
            count += 1

        # Return JSON for AJAX requests
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': f'{count} notification(s) marked as read.',
                'count': count,
            })

        messages.success(request, f'{count} notification(s) marked as read.')
        return redirect('notifications:list')

    return redirect('notifications:list')


@login_required
def reminder_list_view(request):
    """
    List all user's reminders with filtering.
    """
    # Get user's reminders
    reminders = Reminder.objects.filter(user=request.user).select_related(
        'user', 'application'
    )

    # Apply filters
    filter_form = ReminderFilterForm(request.GET)
    if filter_form.is_valid():
        reminder_type = filter_form.cleaned_data.get('reminder_type')
        if reminder_type:
            reminders = reminders.filter(reminder_type=reminder_type)

        status = filter_form.cleaned_data.get('status')
        if status == 'pending':
            reminders = reminders.filter(is_sent=False, scheduled_for__gt=timezone.now())
        elif status == 'sent':
            reminders = reminders.filter(is_sent=True)
        elif status == 'overdue':
            reminders = reminders.filter(is_sent=False, scheduled_for__lte=timezone.now())

    # Separate upcoming and past reminders
    now = timezone.now()
    upcoming_reminders = reminders.filter(
        is_sent=False,
        scheduled_for__gt=now
    ).order_by('scheduled_for')

    overdue_reminders = reminders.filter(
        is_sent=False,
        scheduled_for__lte=now
    ).order_by('-scheduled_for')

    sent_reminders = reminders.filter(is_sent=True).order_by('-sent_at')

    context = {
        'title': 'Reminders',
        'upcoming_reminders': upcoming_reminders[:50],
        'overdue_reminders': overdue_reminders[:20],
        'sent_reminders': sent_reminders[:30],
        'filter_form': filter_form,
        'upcoming_count': upcoming_reminders.count(),
        'overdue_count': overdue_reminders.count(),
        'sent_count': sent_reminders.count(),
    }
    return render(request, 'notifications/reminders.html', context)


@login_required
def reminder_create_view(request):
    """
    Create a new reminder.
    """
    if request.method == 'POST':
        form = ReminderForm(user=request.user, data=request.POST)
        if form.is_valid():
            reminder = form.save(commit=False)
            reminder.user = request.user
            reminder.save()
            messages.success(request, 'Reminder created successfully!')
            return redirect('notifications:reminders')
    else:
        form = ReminderForm(user=request.user)

    context = {
        'title': 'Create Reminder',
        'form': form,
    }
    return render(request, 'notifications/reminder_form.html', context)


@login_required
def reminder_edit_view(request, pk):
    """
    Edit an existing reminder.
    """
    reminder = get_object_or_404(Reminder, pk=pk, user=request.user)

    if request.method == 'POST':
        form = ReminderForm(user=request.user, data=request.POST, instance=reminder)
        if form.is_valid():
            form.save()
            messages.success(request, 'Reminder updated successfully!')
            return redirect('notifications:reminders')
    else:
        form = ReminderForm(user=request.user, instance=reminder)

    context = {
        'title': 'Edit Reminder',
        'form': form,
        'reminder': reminder,
    }
    return render(request, 'notifications/reminder_form.html', context)


@login_required
def reminder_delete_view(request, pk):
    """
    Delete a reminder.
    """
    reminder = get_object_or_404(Reminder, pk=pk, user=request.user)

    if request.method == 'POST':
        reminder.delete()

        # Return JSON for AJAX requests
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': 'Reminder deleted successfully.',
            })

        messages.success(request, 'Reminder deleted successfully.')
        return redirect('notifications:reminders')

    # For GET requests, show confirmation page
    context = {
        'title': 'Delete Reminder',
        'reminder': reminder,
    }
    return render(request, 'notifications/reminder_confirm_delete.html', context)
