# Job & Scholarship Tracker

> An intelligent Django-based platform that automates job and scholarship application management using AI-powered question extraction and response generation.

[![Django](https://img.shields.io/badge/Django-5.1.3-green.svg)](https://www.djangoproject.com/)
[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Celery](https://img.shields.io/badge/Celery-5.4.0-success.svg)](https://docs.celeryproject.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 🚀 Overview

Job & Scholarship Tracker is a production-ready web application that revolutionizes the way you manage applications. Simply paste an application URL, and our AI-powered system will:

- **Extract** all questions and requirements from the application page
- **Analyze** your uploaded documents (resume, transcripts, certificates)
- **Generate** tailored, professional responses based on your background
- **Track** your application status, deadlines, and progress

**No more copy-pasting. No more starting from scratch. Just smart, automated application management.**

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
- **Framework**: Django 5.1.3 (latest stable)
- **Task Queue**: Celery 5.4.0 + Redis
- **Database**: SQLite (development) / PostgreSQL (production)
- **AI Integration**: Google Gemini API (free tier)

### Document Processing
- **PDF**: pdfplumber 0.11.4
- **DOCX**: python-docx 1.1.2
- **OCR**: pytesseract 0.3.13 + Pillow 11.0.0
- **NLP**: spaCy 3.8.2

### Web Scraping
- **Static Pages**: BeautifulSoup4 4.12.3 + requests 2.32.3
- **Dynamic Pages**: Playwright 1.48.0 (supports JavaScript-rendered content)
- **Anti-Bot Protection**: fake-useragent 1.5.1

### Frontend
- **Template Engine**: Django Templates
- **CSS Framework**: Bootstrap 5 + Custom Minimalist Design
- **Forms**: django-crispy-forms 2.3 + crispy-bootstrap5

### Production
- **Web Server**: Gunicorn 23.0.0
- **Static Files**: WhiteNoise 6.8.2
- **Configuration**: python-decouple 3.8
- **API**: Django REST Framework 3.15.2

## 📦 Installation

### Prerequisites

- Python 3.8 or higher
- Redis (for Celery)
- Tesseract OCR (optional, for image processing)

### Step 1: Clone the Repository

```bash
git clone https://github.com/yourusername/job_and_scholarship_tracker.git
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
DJANGO_ENV=development
ALLOWED_HOSTS=localhost,127.0.0.1

# Google Gemini API
GEMINI_API_KEY=your-gemini-api-key-here

# Database (PostgreSQL for production)
DATABASE_URL=postgresql://user:password@localhost:5432/dbname

# Redis (for Celery)
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Email (for notifications)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
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

Run the test suite:

```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test accounts
python manage.py test tracker
python manage.py test documents

# Run specific test class
python manage.py test tracker.tests.test_models.ApplicationTestCase

# Run with coverage
coverage run --source='.' manage.py test
coverage report
```

## 📊 Admin Interface

Access the Django admin at: **http://localhost:8000/admin/**

Features:
- Manage users and profiles
- View and edit applications
- Monitor document processing
- Check notifications and reminders
- View system logs

## 🚀 Production Deployment

### Using Gunicorn + Nginx

1. **Set production environment:**
```bash
export DJANGO_ENV=production
```

2. **Collect static files:**
```bash
python manage.py collectstatic --noinput
```

3. **Run with Gunicorn:**
```bash
gunicorn config.wsgi:application --bind 0.0.0.0:8000
```

4. **Configure Nginx as reverse proxy**

5. **Run Celery worker and beat as system services**

See `IMPLEMENTATION_STATUS.md` for detailed deployment instructions.

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
- Open an issue on GitHub
- Check `IMPLEMENTATION_STATUS.md` for project progress
- Review `CLAUDE.md` for development guidelines

## 📈 Project Status

**Current Version**: 1.0.0-beta
**Completion**: ~75% (Backend: 85%, Frontend: 25%)
**Status**: Active Development

See `IMPLEMENTATION_STATUS.md` for detailed progress breakdown.

## 🎯 Roadmap

- [x] Core application tracking
- [x] AI-powered question extraction
- [x] AI-powered response generation
- [x] Document processing and extraction
- [x] Background task processing
- [ ] Complete frontend templates
- [ ] Advanced analytics dashboard
- [ ] Mobile application
- [ ] Browser extension for one-click import
- [ ] Resume builder integration
- [ ] Interview preparation features

---

**Built with ❤️ using Django, Celery, and Google Gemini AI**
