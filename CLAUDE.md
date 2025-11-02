# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Job & Scholarship Tracker is a production-ready Django web application that automates job and scholarship application management using AI-powered question extraction and response generation. Users paste application URLs, and the system extracts questions, processes uploaded documents (resumes, transcripts), and generates personalized responses using Google Gemini AI.

## Technology Stack

- **Framework**: Django 5.2.7 with Django REST Framework 3.16.1
- **Python**: 3.11+ (see runtime.txt)
- **Database**: SQLite (development) / PostgreSQL (production)
- **Task Queue**: Celery 5.5.3 with Redis 7.0.1
- **AI Integration**: Google Gemini API (google-generativeai 0.8.5)
- **Web Scraping**: Playwright 1.55.0, BeautifulSoup4 4.14.2
- **Document Processing**: pdfplumber 0.11.7, python-docx 1.2.0, pytesseract 0.3.13
- **NLP**: spaCy 3.8.7
- **Testing**: pytest with pytest-django
- **Deployment**: Railway (Gunicorn 23.0.0, WhiteNoise 6.11.0)

## Project Status

**Production-ready** (~95% complete). Core functionality implemented and deployed to Railway.

## Project Structure

```
job_and_scholarship_tracker/
├── config/                     # Django project configuration
│   ├── settings/              # Modular settings (base.py, development.py, production.py)
│   ├── celery.py              # Celery configuration for background tasks
│   ├── urls.py                # Root URL routing
│   ├── wsgi.py                # WSGI config for production
│   └── asgi.py                # ASGI config for async support
├── accounts/                   # User authentication & profiles
│   ├── models.py              # Custom User model
│   ├── views.py               # Login, logout, registration
│   ├── forms.py               # User forms
│   └── tasks.py               # Celery tasks for user-related operations
├── tracker/                    # Core application tracking (main app)
│   ├── models.py              # Application, Question, Response models
│   ├── views.py               # CRUD views for applications
│   ├── forms.py               # Application forms
│   ├── tasks.py               # Celery tasks for AI processing
│   └── admin.py               # Django admin configuration
├── documents/                  # Document management & processing
│   ├── models.py              # Document model
│   ├── views.py               # Document upload/view
│   ├── tasks.py               # Background document processing
│   └── admin.py               # Admin interface for documents
├── notifications/              # Notifications & reminders
│   ├── models.py              # Notification model
│   ├── views.py               # Notification display
│   ├── tasks.py               # Scheduled notification tasks
│   └── admin.py               # Notification management
├── core/                       # Shared utilities and base classes
│   ├── models.py              # Abstract base models
│   └── tasks.py               # Shared Celery tasks
├── services/                   # Business logic services (not Django apps)
│   ├── gemini_service.py      # Google Gemini AI integration
│   ├── scraper_service.py     # Web scraping for URL extraction
│   └── document_parser.py     # Document text extraction
├── templates/                  # HTML templates (Django template engine)
│   ├── base.html              # Base template with Bootstrap 5
│   ├── home.html              # Landing page
│   ├── accounts/              # Authentication templates
│   ├── tracker/               # Application management templates
│   ├── documents/             # Document templates
│   └── notifications/         # Notification templates
├── static/                     # Static files (CSS, JS, images)
├── media/                      # User-uploaded files (documents)
├── manage.py                   # Django management script
├── requirements.txt            # Python dependencies
├── pytest.ini                  # pytest configuration
├── conftest.py                 # pytest fixtures and configuration
├── Procfile                    # Railway deployment processes
├── railway.json                # Railway configuration
├── build.sh                    # Railway build script
└── start.sh                    # Railway startup script
```

## Development Setup

### Initial Setup

```bash
# Clone and navigate to project
git clone https://github.com/NajibOladosu/job_and_scholarship_tracker.git
cd job_and_scholarship_tracker

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY and other settings

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Optional: Install Tesseract OCR for image document processing
# Ubuntu/Debian: sudo apt-get install tesseract-ocr
# macOS: brew install tesseract
```

### Running the Application (Development)

Three terminal windows are required:

```bash
# Terminal 1: Django development server
python manage.py runserver

# Terminal 2: Celery worker (processes background tasks)
celery -A config worker -l info

# Terminal 3: Celery Beat (scheduler for periodic tasks)
celery -A config beat -l info
```

Access at: http://localhost:8000

## Common Commands

### Django Management

```bash
# Run development server
python manage.py runserver

# Create migrations after model changes
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser for admin access
python manage.py createsuperuser

# Django shell
python manage.py shell

# Collect static files (production)
python manage.py collectstatic --noinput
```

### Testing

```bash
# Run all tests with pytest (recommended)
pytest

# Run with coverage report
pytest --cov=. --cov-report=html

# Run specific app tests
pytest accounts/tests/
pytest tracker/tests/
pytest documents/tests/

# Run specific test file
pytest tracker/tests/test_models.py

# Run specific test
pytest tracker/tests/test_models.py::TestApplication::test_application_creation

# Alternative: Django's test runner
python manage.py test

# Run specific app
python manage.py test tracker
```

Test configuration is in `pytest.ini` with markers for categorizing tests (unit, integration, slow, api, celery, external, permissions).

### Celery Commands

```bash
# Start worker
celery -A config worker -l info

# Start beat scheduler
celery -A config beat -l info

# View active tasks
celery -A config inspect active

# Purge all tasks
celery -A config purge
```

### Database

```bash
# Create a new migration
python manage.py makemigrations app_name

# View migration SQL
python manage.py sqlmigrate app_name migration_number

# Show all migrations and their status
python manage.py showmigrations

# Reset database (development only)
rm db.sqlite3
python manage.py migrate
```

## Architecture Overview

### Settings Configuration

The project uses **modular settings** in `config/settings/`:

- **`base.py`**: Common settings for all environments (installed apps, middleware, templates)
- **`development.py`**: Development settings (DEBUG=True, SQLite, console email backend)
- **`production.py`**: Production settings (DEBUG=False, PostgreSQL, security hardening, WhiteNoise)

Switch environments using `DJANGO_SETTINGS_MODULE`:
- Development: `config.settings.development` (default in manage.py)
- Production: `config.settings.production` (set via environment variable)

### Django Apps

1. **accounts**: User authentication with email-based login (no username)
2. **tracker**: Core app for managing applications, questions, and AI-generated responses
3. **documents**: Document upload, storage, and AI-powered text extraction
4. **notifications**: In-app notifications and deadline reminders
5. **core**: Shared utilities, abstract models, and common tasks

### Services Layer

Located in `services/` (not Django apps):

- **`gemini_service.py`**: Google Gemini AI integration
  - Question extraction from URLs
  - Response generation based on user documents
  - Content analysis and summarization

- **`scraper_service.py`**: Web scraping
  - Playwright for JavaScript-rendered pages
  - BeautifulSoup for static pages
  - Automatic fallback between methods

- **`document_parser.py`**: Document text extraction
  - PDF parsing with pdfplumber
  - DOCX parsing with python-docx
  - OCR with pytesseract for images
  - Text extraction and cleaning

### Background Task Processing

**Celery** handles asynchronous operations:

- **Question extraction** from pasted URLs (can take 10-30 seconds)
- **Response generation** using AI (processes multiple questions)
- **Document parsing** (PDF/DOCX/image processing)
- **Deadline reminders** (periodic tasks via Celery Beat)
- **Status change notifications**

Tasks are defined in `tasks.py` files within each app. Celery configuration is in `config/celery.py`.

### Database Models

Key models (see DATABASE_MODELS.md for full schema):

- **`Application`**: Job/scholarship applications with status tracking, deadlines, priorities
- **`Question`**: Questions extracted from application URLs or added manually
- **`Response`**: AI-generated or user-edited responses to questions
- **`Document`**: Uploaded documents with extracted text and metadata
- **`Notification`**: In-app notifications for deadlines and status changes

### Template Structure

Templates use Django template engine with Bootstrap 5:

- **`base.html`**: Base template with navbar, messages, and common structure
- **`home.html`**: Landing page with quick stats and recent applications
- App-specific templates in `templates/{app_name}/`
- Reusable components in `templates/components/`

### AI Integration

**Google Gemini** is used for:
1. **URL scraping**: Extract application content from pasted URLs
2. **Question extraction**: Parse content to identify application questions
3. **Document analysis**: Extract structured data from resumes, transcripts
4. **Response generation**: Create tailored answers based on user background

AI calls are wrapped in Celery tasks to avoid blocking the web interface.

## Deployment

### Railway (Recommended)

The project is configured for Railway deployment:

- **Procfile**: Defines web, worker, and beat processes
- **build.sh**: Installs system dependencies and Python packages
- **start.sh**: Runs migrations and starts Gunicorn
- **railway.json**: Railway-specific configuration
- **railway.env.example**: Required environment variables

Deployment process:
1. Push to GitHub branch
2. Railway auto-deploys from the branch
3. Runs migrations automatically via start.sh
4. Three processes run: web (Django), worker (Celery), beat (scheduler)

See RAILWAY_DEPLOYMENT.md for detailed setup instructions.

### Environment Variables (Production)

Required in production:
- `SECRET_KEY`: Django secret key
- `DJANGO_SETTINGS_MODULE=config.settings.production`
- `DATABASE_URL`: PostgreSQL connection string
- `REDIS_URL`: Redis connection string
- `GEMINI_API_KEY`: Google Gemini API key
- `ALLOWED_HOSTS`: Comma-separated list of allowed hosts

## Key Features Implementation

### 1. Quick URL Entry
- User pastes job/scholarship URL → Celery task extracts questions using Gemini
- Scraper service handles both static (BeautifulSoup) and dynamic (Playwright) pages
- Questions automatically created and linked to application

### 2. Document Processing
- Upload PDF/DOCX/images → Background task extracts text
- spaCy NLP extracts structured data (education, experience, skills)
- Extracted data stored for reuse across applications

### 3. AI Response Generation
- Click "Generate Responses" → Celery task processes each question
- Gemini analyzes question + user documents → generates tailored response
- Responses saved and editable before copying to actual application

### 4. Notifications
- Celery Beat runs periodic tasks to check deadlines
- Creates in-app notifications for upcoming deadlines
- Tracks read/unread status

## Testing Strategy

The project uses **pytest** with Django integration:

- Test files: `{app}/tests/test_*.py`
- Fixtures in `conftest.py` (users, applications, documents)
- Markers: `@pytest.mark.unit`, `@pytest.mark.integration`, `@pytest.mark.celery`
- Coverage target: 80%+
- Mock external services (Gemini API, Playwright) in tests

## Common Development Tasks

### Adding a New Model Field

```bash
# 1. Edit models.py
# 2. Create migration
python manage.py makemigrations app_name

# 3. Review migration file
cat app_name/migrations/XXXX_migration_name.py

# 4. Apply migration
python manage.py migrate

# 5. Update admin.py, forms.py, templates as needed
# 6. Write tests
pytest app_name/tests/test_models.py
```

### Adding a New Celery Task

```python
# In app/tasks.py
from celery import shared_task

@shared_task(bind=True, max_retries=3)
def my_task(self, arg1, arg2):
    try:
        # Task logic
        pass
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60)
```

Test locally with worker running: `celery -A config worker -l info`

### Debugging Celery Tasks

```bash
# View active tasks
celery -A config inspect active

# View scheduled tasks
celery -A config inspect scheduled

# View worker stats
celery -A config inspect stats

# Purge all pending tasks
celery -A config purge
```

### Working with the Services Layer

Services in `services/` are standalone Python modules (not Django apps):

```python
# Example: Using gemini_service
from services.gemini_service import GeminiService

service = GeminiService()
questions = service.extract_questions(url_content)
response = service.generate_response(question_text, user_context)
```

Services are typically called from Celery tasks, not directly from views.

## Security Notes

- Email-based authentication (custom User model in accounts)
- CSRF protection enabled
- SQL injection protection via Django ORM
- File upload validation (size, type)
- Environment-based secrets (never commit .env)
- Production: HTTPS enforcement, secure cookies, HSTS

## Important Files

- **`DATABASE_MODELS.md`**: Complete database schema documentation
- **`IMPLEMENTATION_STATUS.md`**: Project completion status and roadmap
- **`RAILWAY_DEPLOYMENT.md`**: Detailed Railway deployment guide
- **`QUICKSTART.md`**: Quick setup instructions
- **`README.md`**: User-facing documentation
- **`.env.example`**: Template for environment variables

## Tips for Claude Code

1. **Always run migrations** after model changes
2. **Restart Celery worker** after modifying tasks
3. **Use pytest** for testing (configured in pytest.ini)
4. **Mock external APIs** (Gemini, Playwright) in tests
5. **Check settings environment**: development vs production in config/settings/
6. **Services vs Apps**: Business logic in services/, Django apps for models/views/templates
7. **Background tasks**: Long-running operations must use Celery (URL scraping, AI calls)
8. **Templates**: Use base.html as parent, Bootstrap 5 classes available
9. **Admin interface**: Register new models in admin.py for easy data management
10. **Environment variables**: Use python-decouple's `config()` function, never hardcode secrets
