# Quick Start Guide - Job & Scholarship Tracker

Get the application running in 5 minutes!

## Prerequisites

- Python 3.8+
- Git
- Redis (for background tasks)

## Installation Steps

### 1. Clone and Setup

```bash
# Clone the repository
git clone https://github.com/YourUsername/job_and_scholarship_tracker.git
cd job_and_scholarship_tracker

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Install System Dependencies

```bash
# For document OCR (optional but recommended)
# Ubuntu/Debian:
sudo apt-get install tesseract-ocr

# macOS:
brew install tesseract

# For web scraping
playwright install chromium
```

### 3. Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env and add your Gemini API key
# Get it from: https://makersuite.google.com/app/apikey
nano .env  # or use your preferred editor
```

**Required in .env:**
```env
GEMINI_API_KEY=your-api-key-here
```

### 4. Setup Database

```bash
# Run migrations
python manage.py migrate

# Create superuser (admin account)
python manage.py createsuperuser
```

### 5. Install and Start Redis

```bash
# Ubuntu/Debian:
sudo apt-get install redis-server
sudo systemctl start redis-server

# macOS:
brew install redis
brew services start redis

# Windows:
# Download from https://redis.io/download or use Docker
```

### 6. Run the Application

Open **3 terminal windows**:

**Terminal 1 - Django Server:**
```bash
source venv/bin/activate
python manage.py runserver
```

**Terminal 2 - Celery Worker:**
```bash
source venv/bin/activate
celery -A config worker -l info
```

**Terminal 3 - Celery Beat (scheduler):**
```bash
source venv/bin/activate
celery -A config beat -l info
```

### 7. Access the Application

Open your browser and go to:
- **Application**: http://localhost:8000
- **Admin Panel**: http://localhost:8000/admin

Login with the superuser credentials you created in step 4.

---

## First Steps

### 1. Create Your Profile
- Click "Sign Up" or login with superuser
- Complete your profile information

### 2. Upload Your Documents
- Go to "Documents" → "Upload"
- Upload your resume, transcripts, certificates
- Wait for AI processing (background task)

### 3. Add Your First Application
- Go to "Applications" → "New Application"
- Enter the job/scholarship URL
- Or use "Quick Add" with just the URL
- AI will extract questions automatically

### 4. Generate Responses
- Open the application detail page
- Click "Generate AI Responses"
- Review and edit responses as needed

---

## Common Issues & Solutions

### Issue: ModuleNotFoundError
```bash
# Solution: Make sure virtual environment is activated
source venv/bin/activate
pip install -r requirements.txt
```

### Issue: Redis connection error
```bash
# Solution: Make sure Redis is running
redis-cli ping  # Should return PONG

# Start Redis if not running
sudo systemctl start redis-server  # Linux
brew services start redis  # macOS
```

### Issue: Celery tasks not executing
```bash
# Solution: Make sure Celery worker is running
celery -A config worker -l info

# Check Redis connection
redis-cli ping
```

### Issue: Static files not loading
```bash
# Solution: Collect static files
python manage.py collectstatic
```

### Issue: Document processing fails
```bash
# Solution: Install Tesseract OCR
sudo apt-get install tesseract-ocr  # Ubuntu
brew install tesseract  # macOS
```

---

## Development vs Production

This quick start guide is for **development**. For production deployment:
- See [DEPLOYMENT.md](DEPLOYMENT.md) for complete instructions
- Use PostgreSQL instead of SQLite
- Configure proper security settings
- Use Gunicorn + Nginx
- Enable HTTPS/SSL

---

## Features to Try

1. **Application Tracking**
   - Add job and scholarship applications
   - Track status changes
   - Monitor deadlines

2. **AI Question Extraction**
   - Paste job application URLs
   - AI extracts all questions
   - Manual question addition available

3. **AI Response Generation**
   - Uses your uploaded documents
   - Generates tailored responses
   - Edit and customize responses

4. **Document Management**
   - Upload resumes, transcripts, certificates
   - AI extracts key information
   - Reuse information across applications

5. **Reminders & Notifications**
   - Set deadline reminders
   - Get status change notifications
   - Track application progress

---

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Check [DEPLOYMENT.md](DEPLOYMENT.md) for production deployment
- Review [CLAUDE.md](CLAUDE.md) for project architecture
- See [IMPLEMENTATION_STATUS.md](IMPLEMENTATION_STATUS.md) for feature completion

---

## Getting Help

If you encounter issues:
1. Check this guide's troubleshooting section
2. Review application logs
3. Check Django/Celery documentation
4. Open an issue on GitHub

**Happy Tracking! 🎯**
