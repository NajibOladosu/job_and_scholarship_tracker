# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Job & Scholarship Tracker is a Django-based web application for tracking job and scholarship applications. The application helps users manage applications, deadlines, requirements, documents, follow-ups, and feedback.

## Technology Stack

- **Framework**: Django 4.2.19
- **Python**: Python 3.x (recommended 3.8+)
- **Database**: SQLite (default Django setup)

## Project Status

This is an early-stage project. The Django project structure has not yet been initialized. Before development can begin, you'll need to:

1. Create a virtual environment and activate it
2. Install dependencies from requirements.txt
3. Initialize the Django project structure
4. Create Django apps for the application logic

## Development Setup

```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Initialize Django project (when ready)
django-admin startproject config .

# Create Django app for tracking functionality (when ready)
python manage.py startapp tracker

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run development server
python manage.py runserver
```

## Common Django Commands

```bash
# Run development server
python manage.py runserver

# Create new migrations after model changes
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser for admin access
python manage.py createsuperuser

# Run Django shell
python manage.py shell

# Run tests
python manage.py test

# Run specific test
python manage.py test tracker.tests.test_models.ApplicationTestCase
```

## Planned Features

The application will support:
- Adding job and scholarship applications
- Viewing all applications and individual application details
- Deleting applications
- Reusing information from previous applications for new ones
- Resume and cover letter optimization
- Tracking application status, deadlines, requirements, documents, follow-ups, and feedback

## Architecture Notes

When the Django project is created, it should follow this structure:

- **Project configuration**: Standard Django settings, URLs, WSGI/ASGI configuration
- **Tracker app**: Main application logic for managing job and scholarship applications
  - Models will include fields for application type, status, deadlines, requirements, documents, etc.
  - Views will handle CRUD operations and additional features like copying applications
  - Admin interface should be configured for easy data management
- **Templates**: Django templates for the web interface
- **Static files**: CSS, JavaScript, and other static assets

## Database Considerations

The application will track complex application data including statuses, deadlines, requirements, documents, follow-ups, and feedback. The model design should accommodate:
- Different application types (jobs vs scholarships)
- Status tracking through the application lifecycle
- Document management and associations
- Temporal data (deadlines, follow-up dates)
- Text fields for feedback and notes
