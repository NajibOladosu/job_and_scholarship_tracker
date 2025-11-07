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

    Also serves static assets (JS, CSS, images) from frontend/dist
    to bypass Django's /static/ prefix mismatch with Vite's base URL.
    """
    from django.http import FileResponse, Http404
    import mimetypes

    # Get the requested path
    path = request.path.lstrip('/')

    # If path is empty, serve index.html
    if not path or path == '/':
        index_path = os.path.join(settings.BASE_DIR, 'frontend', 'dist', 'index.html')
        if os.path.exists(index_path):
            with open(index_path, 'r', encoding='utf-8') as f:
                return HttpResponse(f.read(), content_type='text/html')

    # Try to serve files from frontend/dist (for Vite assets like /assets/*.js)
    file_path = os.path.join(settings.BASE_DIR, 'frontend', 'dist', path)
    if os.path.exists(file_path) and os.path.isfile(file_path):
        # Guess the content type
        content_type, _ = mimetypes.guess_type(file_path)
        return FileResponse(open(file_path, 'rb'), content_type=content_type or 'application/octet-stream')

    # For all other routes (React Router paths), serve index.html
    index_path = os.path.join(settings.BASE_DIR, 'frontend', 'dist', 'index.html')
    if os.path.exists(index_path):
        with open(index_path, 'r', encoding='utf-8') as f:
            return HttpResponse(f.read(), content_type='text/html')

    # If frontend is not built, show helpful error
    return HttpResponse(
        '<h1>Frontend Not Built</h1>'
        '<p>The React frontend has not been built yet.</p>'
        '<p>Run: <code>cd frontend && npm install && npm run build</code></p>',
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
