"""
Analytics utilities for generating dashboard statistics and visualizations.

Provides functions for calculating summary stats, generating Sankey diagram data,
and preparing timeline events for the analytics dashboard.
"""
from django.utils import timezone
from django.db.models import Count, Q
from datetime import timedelta
from collections import defaultdict
from typing import Dict, List, Any, Optional


def calculate_summary_stats(user, days: int = 60) -> Dict[str, Any]:
    """
    Calculate summary statistics for a user's applications.

    Args:
        user: User instance
        days: Number of days to look back for time-based stats (default: 60)

    Returns:
        Dictionary containing summary statistics with the following structure:
        {
            'total_applications': int,
            'recent_applications': int,  # Last N days
            'status_breakdown': {
                'draft': int,
                'submitted': int,
                'in_review': int,
                'interview': int,
                'offer': int,
                'rejected': int,
                'withdrawn': int,
            },
            'type_breakdown': {
                'job': int,
                'scholarship': int,
            },
            'priority_breakdown': {
                'high': int,
                'medium': int,
                'low': int,
            },
            'interview_stats': {
                'total_interviews': int,
                'upcoming_interviews': int,
            },
            'deadline_stats': {
                'overdue': int,
                'due_this_week': int,
                'due_this_month': int,
            },
            'conversion_rate': float,  # Offers / Total Submitted
            'response_rate': float,  # (Offers + Rejections) / Total Submitted
        }
    """
    from tracker.models import Application

    # Get user's applications
    applications = Application.objects.filter(user=user)

    # Calculate date thresholds
    now = timezone.now()
    cutoff_date = now - timedelta(days=days)
    one_week = now + timedelta(days=7)
    one_month = now + timedelta(days=30)

    # Total and recent applications
    total_applications = applications.count()
    recent_applications = applications.filter(created_at__gte=cutoff_date).count()

    # Status breakdown
    status_breakdown = {
        'draft': applications.filter(status='draft').count(),
        'submitted': applications.filter(status='submitted').count(),
        'in_review': applications.filter(status='in_review').count(),
        'interview': applications.filter(status='interview').count(),
        'offer': applications.filter(status='offer').count(),
        'rejected': applications.filter(status='rejected').count(),
        'withdrawn': applications.filter(status='withdrawn').count(),
    }

    # Type breakdown
    type_breakdown = {
        'job': applications.filter(application_type='job').count(),
        'scholarship': applications.filter(application_type='scholarship').count(),
    }

    # Priority breakdown
    priority_breakdown = {
        'high': applications.filter(priority='high').count(),
        'medium': applications.filter(priority='medium').count(),
        'low': applications.filter(priority='low').count(),
    }

    # Interview stats (applications in interview status)
    total_interviews = status_breakdown['interview']
    # Upcoming interviews (applications with deadlines in the future and interview status)
    upcoming_interviews = applications.filter(
        status='interview',
        deadline__gte=now,
        deadline__lte=one_week
    ).count()

    # Deadline stats
    overdue = applications.filter(
        deadline__lt=now,
        status__in=['draft', 'submitted', 'in_review']
    ).count()

    due_this_week = applications.filter(
        deadline__gte=now,
        deadline__lte=one_week,
        status__in=['draft', 'submitted', 'in_review', 'interview']
    ).count()

    due_this_month = applications.filter(
        deadline__gte=now,
        deadline__lte=one_month,
        status__in=['draft', 'submitted', 'in_review', 'interview']
    ).count()

    # Conversion and response rates
    submitted_count = applications.filter(
        status__in=['submitted', 'in_review', 'interview', 'offer', 'rejected']
    ).count()

    offers_count = status_breakdown['offer']
    rejections_count = status_breakdown['rejected']

    conversion_rate = (offers_count / submitted_count * 100) if submitted_count > 0 else 0
    response_rate = ((offers_count + rejections_count) / submitted_count * 100) if submitted_count > 0 else 0

    return {
        'total_applications': total_applications,
        'recent_applications': recent_applications,
        'days_filter': days,
        'status_breakdown': status_breakdown,
        'type_breakdown': type_breakdown,
        'priority_breakdown': priority_breakdown,
        'interview_stats': {
            'total_interviews': total_interviews,
            'upcoming_interviews': upcoming_interviews,
        },
        'deadline_stats': {
            'overdue': overdue,
            'due_this_week': due_this_week,
            'due_this_month': due_this_month,
        },
        'conversion_rate': round(conversion_rate, 1),
        'response_rate': round(response_rate, 1),
    }


def generate_sankey_data(user) -> Dict[str, Any]:
    """
    Generate Sankey diagram data for application flow visualization.

    The Sankey diagram shows how applications flow through different stages:
    - Initial state (Draft/Submitted)
    - Review stages (In Review, Interview)
    - Final outcomes (Offer, Rejected, Withdrawn)

    Args:
        user: User instance

    Returns:
        Dictionary containing Plotly Sankey diagram configuration:
        {
            'node': {
                'label': List[str],  # Node labels
                'color': List[str],  # Node colors
                'customdata': List[int],  # Node counts for hover
            },
            'link': {
                'source': List[int],  # Source node indices
                'target': List[int],  # Target node indices
                'value': List[int],  # Flow values (counts)
                'color': List[str],  # Link colors
            },
            'total_count': int,  # Total applications
        }
    """
    from tracker.models import Application, ApplicationStatus

    # Define node structure (order matters for indices)
    # Nodes: Draft, Submitted, In Review, Interview, Offer, Rejected, Withdrawn, No Update
    nodes = {
        'draft': 0,
        'submitted': 1,
        'in_review': 2,
        'interview': 3,
        'offer': 4,
        'rejected': 5,
        'withdrawn': 6,
    }

    node_labels = [
        'Draft',
        'Submitted',
        'In Review',
        'Interview',
        'Offer',
        'Rejected',
        'Withdrawn',
    ]

    node_colors = [
        'rgba(156, 163, 175, 0.8)',  # Draft - gray
        'rgba(59, 130, 246, 0.8)',   # Submitted - blue
        'rgba(245, 158, 11, 0.8)',   # In Review - amber
        'rgba(139, 92, 246, 0.8)',   # Interview - purple
        'rgba(16, 185, 129, 0.8)',   # Offer - green
        'rgba(239, 68, 68, 0.8)',    # Rejected - red
        'rgba(75, 85, 99, 0.8)',     # Withdrawn - dark gray
    ]

    # Count applications in each status
    applications = Application.objects.filter(user=user)
    status_counts = applications.values('status').annotate(count=Count('id'))

    status_count_dict = {item['status']: item['count'] for item in status_counts}

    # Calculate node sizes (for hover display)
    node_customdata = [
        status_count_dict.get('draft', 0),
        status_count_dict.get('submitted', 0),
        status_count_dict.get('in_review', 0),
        status_count_dict.get('interview', 0),
        status_count_dict.get('offer', 0),
        status_count_dict.get('rejected', 0),
        status_count_dict.get('withdrawn', 0),
    ]

    # Build flow links by analyzing status history
    # Track transitions between statuses
    link_data = defaultdict(int)

    # Get all status history records ordered by date
    from tracker.models import ApplicationStatus as StatusHistory

    # For each application, trace its status journey
    for app in applications:
        status_changes = StatusHistory.objects.filter(
            application=app
        ).order_by('created_at').values_list('status', flat=True)

        if status_changes:
            # Convert to list to iterate
            changes_list = list(status_changes)

            # If there's history, create flows from previous to current
            for i in range(len(changes_list) - 1):
                source_status = changes_list[i]
                target_status = changes_list[i + 1]

                if source_status in nodes and target_status in nodes:
                    link_key = (nodes[source_status], nodes[target_status])
                    link_data[link_key] += 1

            # Add flow from last status in history to current status if different
            last_history_status = changes_list[-1]
            current_status = app.status

            if last_history_status != current_status and current_status in nodes:
                link_key = (nodes[last_history_status], nodes[current_status])
                link_data[link_key] += 1
        else:
            # No status history - application is in its initial status
            # For visualization, we'll show these as standalone nodes
            pass

    # If no status history, create default flows based on typical progression
    if not link_data:
        # Create simple flows: Draft -> Submitted, Submitted -> In Review, etc.
        # Based on current status counts
        draft_count = status_count_dict.get('draft', 0)
        submitted_count = status_count_dict.get('submitted', 0)
        in_review_count = status_count_dict.get('in_review', 0)
        interview_count = status_count_dict.get('interview', 0)
        offer_count = status_count_dict.get('offer', 0)
        rejected_count = status_count_dict.get('rejected', 0)
        withdrawn_count = status_count_dict.get('withdrawn', 0)

        # Estimate flows (this is a simplification when no history exists)
        if submitted_count > 0:
            link_data[(nodes['draft'], nodes['submitted'])] = max(1, submitted_count // 2)

        if in_review_count > 0:
            link_data[(nodes['submitted'], nodes['in_review'])] = max(1, in_review_count)

        if interview_count > 0:
            link_data[(nodes['in_review'], nodes['interview'])] = max(1, interview_count)

        if offer_count > 0:
            link_data[(nodes['interview'], nodes['offer'])] = max(1, offer_count // 2)
            link_data[(nodes['in_review'], nodes['offer'])] = max(1, offer_count - offer_count // 2)

        if rejected_count > 0:
            link_data[(nodes['interview'], nodes['rejected'])] = max(1, rejected_count // 3)
            link_data[(nodes['in_review'], nodes['rejected'])] = max(1, rejected_count // 3)
            link_data[(nodes['submitted'], nodes['rejected'])] = max(1, rejected_count - 2 * (rejected_count // 3))

        if withdrawn_count > 0:
            link_data[(nodes['draft'], nodes['withdrawn'])] = max(1, withdrawn_count)

    # Convert link_data to Plotly format
    link_sources = []
    link_targets = []
    link_values = []
    link_colors = []

    for (source, target), value in link_data.items():
        link_sources.append(source)
        link_targets.append(target)
        link_values.append(value)

        # Color links based on target status
        # Use semi-transparent version of target node color
        link_colors.append(node_colors[target].replace('0.8)', '0.4)'))

    total_count = applications.count()

    return {
        'node': {
            'label': node_labels,
            'color': node_colors,
            'customdata': node_customdata,
            'hovertemplate': '%{label}<br>%{customdata} applications<extra></extra>',
        },
        'link': {
            'source': link_sources,
            'target': link_targets,
            'value': link_values,
            'color': link_colors,
            'hovertemplate': '%{value} applications<br>%{source.label} → %{target.label}<extra></extra>',
        },
        'total_count': total_count,
    }


def get_timeline_data(user, days_ahead: int = 30) -> List[Dict[str, Any]]:
    """
    Get timeline events for upcoming interviews and deadlines.

    Args:
        user: User instance
        days_ahead: Number of days to look ahead (default: 30)

    Returns:
        List of timeline events, each containing:
        {
            'id': int,  # Application ID
            'title': str,  # Application title
            'company': str,  # Company/institution name
            'date': str,  # ISO format datetime
            'type': str,  # 'interview', 'deadline', 'overdue'
            'status': str,  # Application status
            'priority': str,  # Application priority
            'is_overdue': bool,
            'is_today': bool,
            'is_this_week': bool,
            'days_until': int,  # Days until event (negative if past)
        }
    """
    from tracker.models import Application

    now = timezone.now()
    future_date = now + timedelta(days=days_ahead)

    # Get applications with deadlines in the next N days or overdue
    applications = Application.objects.filter(
        user=user,
        deadline__isnull=False
    ).filter(
        Q(deadline__lte=future_date) | Q(deadline__lt=now)
    ).order_by('deadline')

    events = []

    for app in applications:
        deadline = app.deadline
        days_until = (deadline - now).days

        # Determine event type
        if deadline < now:
            event_type = 'overdue'
        elif app.status == 'interview':
            event_type = 'interview'
        else:
            event_type = 'deadline'

        # Check date flags
        is_overdue = deadline < now
        is_today = deadline.date() == now.date()
        is_this_week = 0 <= days_until <= 7

        events.append({
            'id': app.id,
            'title': app.title,
            'company': app.company_or_institution,
            'date': deadline.isoformat(),
            'date_display': deadline.strftime('%B %d, %Y at %I:%M %p'),
            'type': event_type,
            'status': app.status,
            'status_display': app.get_status_display(),
            'priority': app.priority,
            'priority_display': app.get_priority_display(),
            'is_overdue': is_overdue,
            'is_today': is_today,
            'is_this_week': is_this_week,
            'days_until': days_until,
        })

    return events
