"""
Core views for the application.
"""
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.conf import settings
import os


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


def react_app_view(request):
    """
    Serve the React app's index.html for all non-API routes.
    This allows React Router to handle client-side routing.
    """
    # Try to find index.html in the frontend/dist directory
    index_path = os.path.join(settings.BASE_DIR, 'frontend', 'dist', 'index.html')

    if os.path.exists(index_path):
        with open(index_path, 'r', encoding='utf-8') as f:
            return HttpResponse(f.read(), content_type='text/html')
    else:
        # Fallback: Try to render it as a template
        try:
            return render(request, 'index.html')
        except Exception as e:
            # If all else fails, return a helpful error message
            return HttpResponse(
                f'<h1>Frontend Not Built</h1>'
                f'<p>The React frontend has not been built yet.</p>'
                f'<p>Run: <code>cd frontend && npm install && npm run build</code></p>'
                f'<p>Error: {str(e)}</p>',
                status=500
            )


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
