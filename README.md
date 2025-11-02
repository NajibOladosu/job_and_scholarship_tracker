# Job & Scholarship Tracker

> An intelligent Django-based platform that automates job and scholarship application management using AI-powered question extraction and response generation.

[![Django](https://img.shields.io/badge/Django-5.2.7-green.svg)](https://www.djangoproject.com/)
[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![Celery](https://img.shields.io/badge/Celery-5.5.3-success.svg)](https://docs.celeryproject.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Railway](https://img.shields.io/badge/Deploy-Railway-blueviolet.svg)](https://railway.app)

## 🚀 Overview

Job & Scholarship Tracker is a production-ready web application that revolutionizes the way you manage applications. Simply paste an application URL, and our AI-powered system will:

- **Extract** all questions and requirements from the application page
- **Analyze** your uploaded documents (resume, transcripts, certificates)
- **Generate** tailored, professional responses based on your background
- **Track** your application status, deadlines, and progress

**No more copy-pasting. No more starting from scratch. Just smart, automated application management.**

## 🚀 Quick Start

```bash
# Clone the repository
git clone https://github.com/NajibOladosu/job_and_scholarship_tracker.git
cd job_and_scholarship_tracker

# Set up and run (detailed instructions below)
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Add your GEMINI_API_KEY to .env
python manage.py migrate
python manage.py runserver

# In separate terminals, run:
celery -A config worker -l info
celery -A config beat -l info
```

See [QUICKSTART.md](QUICKSTART.md) for detailed setup instructions.

## ✨ Key Features

### 🤖 AI-Powered Intelligence
- **Automatic Question Extraction**: Paste any job or scholarship URL, and AI extracts all application questions
- **Smart Response Generation**: AI creates personalized answers using information from your documents
- **Document Analysis**: Automatically extracts education, experience, skills, and certifications from resumes and transcripts
- **Context-Aware Responses**: Responses are tailored to each question type and your unique background

### 📋 Application Management
- **Quick URL Entry**: Add applications with just a URL - AI handles the rest
- **Full CRUD Operations**: Create, view, edit, and delete applications
- **Status Tracking**: Track applications through multiple stages (Draft, Submitted, In Review, Interview, Offer, Rejected)
- **Priority Management**: Organize applications by priority (High, Medium, Low)
- **Deadline Monitoring**: Never miss a deadline with built-in tracking

### 📄 Document Processing
- **Multi-Format Support**: PDF, DOCX, images (with OCR), and text files
- **Intelligent Extraction**: AI parses your documents to extract structured information
- **Reusable Data**: Extracted information is used across all your applications
- **Version Control**: Keep track of document updates and changes

### 📊 Dashboard & Analytics
- **Centralized Dashboard**: View all applications at a glance
- **Advanced Filtering**: Filter by type, status, priority, and search
- **Status Statistics**: See your application pipeline at a glance
- **Timeline View**: Track application history and status changes

### 🔔 Notifications & Reminders
- **Deadline Reminders**: Automatic reminders for upcoming deadlines
- **Status Updates**: Get notified when application statuses change
- **In-App Notifications**: Never miss important updates

## 🛠️ Technology Stack

### Backend
- **Framework**: Django 5.2.7 (latest stable)
- **Task Queue**: Celery 5.5.3 + Redis 7.0.1
- **Database**: SQLite (development) / PostgreSQL (production)
- **AI Integration**: Google Gemini API

### Document Processing
- **PDF**: pdfplumber 0.11.7
- **DOCX**: python-docx 1.2.0
- **OCR**: pytesseract 0.3.14 + Pillow 12.0.0
- **NLP**: spaCy 3.8.7

### Web Scraping
- **Static Pages**: BeautifulSoup4 4.14.2 + requests 2.32.5
- **Dynamic Pages**: Playwright 1.55.0 (supports JavaScript-rendered content)
- **Anti-Bot Protection**: fake-useragent 2.0.1

### Frontend
- **Template Engine**: Django Templates
- **CSS Framework**: Bootstrap 5 + Custom Minimalist Design
- **Forms**: django-crispy-forms 2.3.1 + crispy-bootstrap5 2024.10
- **Icons**: Bootstrap Icons

### Production & Deployment
- **Web Server**: Gunicorn 23.0.0
- **Static Files**: WhiteNoise 6.8.2
- **Configuration**: python-decouple 3.8
- **API**: Django REST Framework 3.16.1
- **Deployment**: Railway (recommended) / Render / DigitalOcean
- **CI/CD**: Automatic deployments from GitHub

## 📦 Installation

### Prerequisites

- Python 3.8 or higher
- Redis (for Celery)
- Tesseract OCR (optional, for image processing)

### Step 1: Clone the Repository

```bash
git clone https://github.com/NajibOladosu/job_and_scholarship_tracker.git
cd job_and_scholarship_tracker
```

### Step 2: Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Edit `.env` and add your configuration:

```env
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=True
DJANGO_SETTINGS_MODULE=config.settings.development
ALLOWED_HOSTS=localhost,127.0.0.1

# Google Gemini API
# Get your key from: https://makersuite.google.com/app/apikey
GEMINI_API_KEY=your-gemini-api-key-here

# Database (PostgreSQL for production)
DB_NAME=job_tracker_db
DB_USER=postgres
DB_PASSWORD=your-db-password
DB_HOST=localhost
DB_PORT=5432

# Redis (for Celery)
REDIS_URL=redis://localhost:6379/0

# Email (for notifications)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-gmail-app-password
```

### Step 5: Run Database Migrations

```bash
python manage.py migrate
```

### Step 6: Create Superuser

```bash
python manage.py createsuperuser
```

### Step 7: Install Tesseract OCR (Optional)

For image document processing (certificates, scanned transcripts):

**Ubuntu/Debian:**
```bash
sudo apt-get install tesseract-ocr
```

**macOS:**
```bash
brew install tesseract
```

**Windows:**
Download from: https://github.com/UB-Mannheim/tesseract/wiki

## 🚀 Running the Application

### Development Mode

You'll need **three terminal windows**:

**Terminal 1 - Django Development Server:**
```bash
source venv/bin/activate
python manage.py runserver
```

**Terminal 2 - Celery Worker:**
```bash
source venv/bin/activate
celery -A config worker -l info
```

**Terminal 3 - Celery Beat (Scheduler):**
```bash
source venv/bin/activate
celery -A config beat -l info
```

Access the application at: **http://localhost:8000**

## 📖 Usage

### 1. Upload Your Documents

1. Navigate to **Documents** → **Upload**
2. Upload your resume, transcripts, certificates, or other documents
3. The system automatically processes and extracts your information
4. Extracted data includes: education, experience, skills, certifications

### 2. Add an Application

**Quick Method (Recommended):**
1. Click **"Quick Add"** or **"Add Application"**
2. Paste the job/scholarship application URL
3. Select application type (Job or Scholarship)
4. Click **"Create"**
5. AI automatically extracts:
   - Application title
   - Company/Institution name
   - Description
   - All application questions

**Manual Method:**
1. Click **"New Application"**
2. Fill in details manually
3. Add questions manually if needed

### 3. Generate Responses

1. Open an application
2. Click **"Generate All Responses"**
3. AI creates personalized answers for each question using your document data
4. Review and edit responses as needed
5. Copy responses to use in the actual application

### 4. Track Your Applications

- Update status as you progress (Submitted → In Review → Interview → Offer)
- Set deadlines and get automatic reminders
- Add notes and track communication
- View application history and timeline

## 🏗️ Project Structure

```
job_and_scholarship_tracker/
├── config/                     # Django project configuration
│   ├── settings/              # Modular settings (base, dev, prod)
│   ├── celery.py              # Celery configuration
│   └── urls.py                # Main URL routing
├── apps/
│   ├── accounts/              # User authentication & profiles
│   ├── tracker/               # Application tracking (core app)
│   ├── documents/             # Document management & processing
│   ├── notifications/         # Notifications & reminders
│   └── core/                  # Shared utilities
├── services/                  # Business logic services
│   ├── gemini_service.py     # Google Gemini AI integration
│   ├── scraper_service.py    # Web scraping
│   └── document_parser.py    # Document parsing
├── templates/                 # HTML templates
├── static/                    # CSS, JavaScript, images
├── media/                     # User uploaded files
└── requirements.txt           # Python dependencies
```

## 🔧 Configuration

### Settings Files

The project uses modular settings:

- **`base.py`**: Common settings for all environments
- **`development.py`**: Development-specific settings (SQLite, DEBUG=True)
- **`production.py`**: Production settings (PostgreSQL, DEBUG=False, security)

Switch between environments using the `DJANGO_ENV` environment variable.

## 🧪 Testing

The project includes a comprehensive test suite using pytest:

```bash
# Run all tests with pytest (recommended)
pytest

# Run tests with coverage
pytest --cov=. --cov-report=html

# Run specific app tests
pytest accounts/tests/
pytest tracker/tests/
pytest documents/tests/

# Run specific test file
pytest tracker/tests/test_models.py

# Run with verbose output
pytest -v

# Alternative: Django's test runner
python manage.py test

# Run specific app tests
python manage.py test accounts
python manage.py test tracker
```

Test configuration is in `pytest.ini` and `.coveragerc`.

## 📊 Admin Interface

Access the Django admin at: **http://localhost:8000/admin/**

Features:
- Manage users and profiles
- View and edit applications
- Monitor document processing
- Check notifications and reminders
- View system logs

## 🚀 Production Deployment

### Railway (Recommended - Easiest) ⭐

**Quick Deploy to Railway:**

1. **Sign up at [Railway](https://railway.app)**
2. **Click "Deploy from GitHub repo"**
3. **Select this repository**
4. **Add PostgreSQL and Redis databases** (one-click)
5. **Set environment variables** (see `railway.env.example`)
6. **Deploy!** 🎉

**Automatic deployments:** Every push to your branch auto-deploys!

**Complete Railway guide:** See `RAILWAY_DEPLOYMENT.md` for step-by-step instructions.

**What you get:**
- ✅ Automatic HTTPS
- ✅ PostgreSQL database
- ✅ Redis for Celery
- ✅ Auto-scaling
- ✅ Free tier available ($5/month credit)

### Alternative: Traditional Deployment (VPS/Server)

1. **Set production environment:**
```bash
export DJANGO_SETTINGS_MODULE=config.settings.production
```

2. **Collect static files:**
```bash
python manage.py collectstatic --noinput
```

3. **Run with Gunicorn:**
```bash
gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 3
```

4. **Configure Nginx as reverse proxy**

5. **Run Celery worker and beat as systemd services**

See `DEPLOYMENT.md` for detailed manual deployment instructions.

## 🔐 Security

- Email-based authentication (no username)
- Password hashing with PBKDF2
- CSRF protection enabled
- Encrypted sensitive data (API keys, tokens)
- File upload validation
- SQL injection protection via Django ORM
- HTTPS enforcement in production

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **Google Gemini**: AI-powered question extraction and response generation
- **Django Community**: Excellent framework and ecosystem
- **Celery**: Robust task queue system
- **Bootstrap**: Beautiful UI components

## 📞 Support

For issues, questions, or suggestions:
- Open an issue on [GitHub](https://github.com/NajibOladosu/job_and_scholarship_tracker/issues)
- Check `IMPLEMENTATION_STATUS.md` for project progress
- Review `CLAUDE.md` for development guidelines
- See deployment guides: `RAILWAY_DEPLOYMENT.md` or `DEPLOYMENT.md`

## 📈 Project Status

**Current Version**: 1.0.0
**Completion**: ~95% Complete 🎉
- **Backend**: 100% ✅
- **Frontend**: 100% ✅
- **Testing**: 80% ✅
- **Deployment**: 100% ✅

**Status**: Production Ready

See `IMPLEMENTATION_STATUS.md` for detailed progress breakdown.

## 🎯 Roadmap

### Completed ✅
- [x] Core application tracking system
- [x] AI-powered question extraction from URLs
- [x] AI-powered response generation
- [x] Document processing and extraction (PDF, DOCX, images with OCR)
- [x] Background task processing with Celery
- [x] Complete frontend templates (minimalist design)
- [x] User authentication and profiles
- [x] Notifications and reminders system
- [x] Admin interfaces for all models
- [x] Railway deployment configuration
- [x] Comprehensive testing suite

### Planned 🚀
- [ ] Advanced analytics dashboard with charts
- [ ] Email notification integration
- [ ] Mobile-responsive enhancements
- [ ] Browser extension for one-click import
- [ ] Resume builder integration
- [ ] Interview preparation features
- [ ] Application insights and recommendations
- [ ] Cover letter generator

---

**Built with ❤️ using Django, Celery, and Google Gemini AI**
