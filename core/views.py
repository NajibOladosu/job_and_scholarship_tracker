"""
Core views for the application.
"""
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required


def home_view(request):
    """
    Landing page view.
    If user is authenticated, redirect to dashboard.
    Otherwise, show landing page.
    """
    if request.user.is_authenticated:
        return redirect('tracker:dashboard')

    return render(request, 'home.html', {
        'title': 'Job & Scholarship Tracker'
    })


def handler404(request, exception):
    """
    Custom 404 error handler.
    """
    return render(request, 'errors/404.html', status=404)


def handler500(request):
    """
    Custom 500 error handler.
    """
    return render(request, 'errors/500.html', status=500)
