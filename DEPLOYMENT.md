# Deployment Guide - Job & Scholarship Tracker

This guide provides step-by-step instructions for deploying the Job & Scholarship Tracker application to production.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Environment Setup](#environment-setup)
3. [Database Configuration](#database-configuration)
4. [Application Deployment](#application-deployment)
5. [Celery & Redis Setup](#celery--redis-setup)
6. [Static Files](#static-files)
7. [Production Checklist](#production-checklist)
8. [Monitoring & Maintenance](#monitoring--maintenance)

---

## Prerequisites

### System Requirements
- Python 3.8 or higher
- PostgreSQL 12+ (for production)
- Redis 6+ (for Celery)
- Git
- Linux/Ubuntu server (recommended)

### Services & APIs
- **Google Gemini API Key** - Get from [Google AI Studio](https://makersuite.google.com/app/apikey)
- **Domain name** (optional but recommended)
- **SSL certificate** (recommended - use Let's Encrypt)

---

## Environment Setup

### 1. Clone Repository

```bash
git clone https://github.com/YourUsername/job_and_scholarship_tracker.git
cd job_and_scholarship_tracker
```

### 2. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Install Additional Production Dependencies

```bash
# Install Tesseract OCR (required for document processing)
sudo apt-get update
sudo apt-get install tesseract-ocr

# Install Playwright browsers (for web scraping)
playwright install chromium
```

---

## Database Configuration

### 1. Install PostgreSQL

```bash
sudo apt-get install postgresql postgresql-contrib
```

### 2. Create Database and User

```bash
sudo -u postgres psql

# In PostgreSQL shell:
CREATE DATABASE job_tracker_db;
CREATE USER job_tracker_user WITH PASSWORD 'your_secure_password';
ALTER ROLE job_tracker_user SET client_encoding TO 'utf8';
ALTER ROLE job_tracker_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE job_tracker_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE job_tracker_db TO job_tracker_user;
\q
```

---

## Application Deployment

### 1. Create Environment File

Create `.env` file in project root:

```bash
# Django Settings
DJANGO_SETTINGS_MODULE=config.settings.production
SECRET_KEY=your-very-secure-secret-key-here-min-50-chars
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Database
DB_NAME=job_tracker_db
DB_USER=job_tracker_user
DB_PASSWORD=your_secure_password
DB_HOST=localhost
DB_PORT=5432

# Redis (Celery)
REDIS_URL=redis://localhost:6379/0

# Email (for password reset, notifications)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Google Gemini API
GEMINI_API_KEY=your-gemini-api-key-here

# Security
CSRF_COOKIE_SECURE=True
SESSION_COOKIE_SECURE=True
SECURE_SSL_REDIRECT=True
```

**Important**: Generate a secure SECRET_KEY:
```python
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 2. Run Migrations

```bash
python manage.py migrate --settings=config.settings.production
```

### 3. Create Superuser

```bash
python manage.py createsuperuser --settings=config.settings.production
```

### 4. Collect Static Files

```bash
python manage.py collectstatic --noinput --settings=config.settings.production
```

### 5. Test the Application

```bash
python manage.py runserver --settings=config.settings.production
```

---

## Celery & Redis Setup

### 1. Install Redis

```bash
sudo apt-get install redis-server
sudo systemctl enable redis-server
sudo systemctl start redis-server
```

### 2. Test Redis Connection

```bash
redis-cli ping
# Should return: PONG
```

### 3. Create Celery Systemd Service

Create `/etc/systemd/system/celery.service`:

```ini
[Unit]
Description=Celery Service
After=network.target

[Service]
Type=forking
User=www-data
Group=www-data
WorkingDirectory=/path/to/job_and_scholarship_tracker
Environment="PATH=/path/to/venv/bin"
ExecStart=/path/to/venv/bin/celery -A config worker --detach --loglevel=info --logfile=/var/log/celery/worker.log
ExecStop=/path/to/venv/bin/celery -A config control shutdown
Restart=always

[Install]
WantedBy=multi-user.target
```

### 4. Create Celery Beat Systemd Service

Create `/etc/systemd/system/celerybeat.service`:

```ini
[Unit]
Description=Celery Beat Service
After=network.target

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/path/to/job_and_scholarship_tracker
Environment="PATH=/path/to/venv/bin"
ExecStart=/path/to/venv/bin/celery -A config beat --loglevel=info --logfile=/var/log/celery/beat.log
Restart=always

[Install]
WantedBy=multi-user.target
```

### 5. Create Log Directory

```bash
sudo mkdir -p /var/log/celery
sudo chown www-data:www-data /var/log/celery
```

### 6. Start Celery Services

```bash
sudo systemctl daemon-reload
sudo systemctl enable celery celerybeat
sudo systemctl start celery celerybeat
sudo systemctl status celery celerybeat
```

---

## Static Files

### Using WhiteNoise (Already Configured)

WhiteNoise is already configured in `config/settings/production.py` and will serve static files efficiently.

### Optional: Use CDN or S3

For large-scale deployments, consider:
- AWS S3 + CloudFront
- Google Cloud Storage
- Cloudinary

Update `STATIC_URL` and storage backend in production settings.

---

## Web Server Setup

### Option 1: Gunicorn + Nginx (Recommended)

#### 1. Install Gunicorn

```bash
pip install gunicorn
```

#### 2. Create Gunicorn Systemd Service

Create `/etc/systemd/system/gunicorn.service`:

```ini
[Unit]
Description=Gunicorn daemon for Job & Scholarship Tracker
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/path/to/job_and_scholarship_tracker
Environment="PATH=/path/to/venv/bin"
ExecStart=/path/to/venv/bin/gunicorn \
    --workers 3 \
    --bind unix:/run/gunicorn.sock \
    --timeout 120 \
    --access-logfile /var/log/gunicorn/access.log \
    --error-logfile /var/log/gunicorn/error.log \
    config.wsgi:application

[Install]
WantedBy=multi-user.target
```

#### 3. Create Log Directory

```bash
sudo mkdir -p /var/log/gunicorn
sudo chown www-data:www-data /var/log/gunicorn
```

#### 4. Start Gunicorn

```bash
sudo systemctl daemon-reload
sudo systemctl enable gunicorn
sudo systemctl start gunicorn
sudo systemctl status gunicorn
```

#### 5. Install and Configure Nginx

```bash
sudo apt-get install nginx
```

Create `/etc/nginx/sites-available/job_tracker`:

```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    client_max_body_size 10M;

    location = /favicon.ico { access_log off; log_not_found off; }

    location /static/ {
        alias /path/to/job_and_scholarship_tracker/staticfiles/;
    }

    location /media/ {
        alias /path/to/job_and_scholarship_tracker/media/;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/run/gunicorn.sock;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header Host $host;
        proxy_redirect off;
    }
}
```

#### 6. Enable Site and Restart Nginx

```bash
sudo ln -s /etc/nginx/sites-available/job_tracker /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

#### 7. Setup SSL with Let's Encrypt

```bash
sudo apt-get install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

---

## Production Checklist

### Security
- [ ] Set `DEBUG=False` in production
- [ ] Use strong `SECRET_KEY` (min 50 characters)
- [ ] Set `ALLOWED_HOSTS` correctly
- [ ] Enable HTTPS/SSL
- [ ] Set `CSRF_COOKIE_SECURE=True`
- [ ] Set `SESSION_COOKIE_SECURE=True`
- [ ] Configure firewall (UFW)
- [ ] Keep Gemini API key secure

### Database
- [ ] Use PostgreSQL (not SQLite)
- [ ] Set strong database password
- [ ] Configure database backups
- [ ] Enable connection pooling if needed

### Files & Media
- [ ] Configure media file storage
- [ ] Set up media file backups
- [ ] Limit file upload sizes (10MB configured)
- [ ] Verify file type restrictions

### Services
- [ ] Celery worker running
- [ ] Celery beat running
- [ ] Redis running
- [ ] Gunicorn running
- [ ] Nginx running

### Monitoring
- [ ] Set up error logging
- [ ] Configure application monitoring (Sentry, New Relic, etc.)
- [ ] Set up uptime monitoring
- [ ] Configure backup alerts

### Testing
- [ ] Test user registration and login
- [ ] Test application creation and tracking
- [ ] Test document upload and processing
- [ ] Test AI question extraction
- [ ] Test AI response generation
- [ ] Test reminder notifications
- [ ] Test all CRUD operations
- [ ] Test mobile responsiveness

---

## Monitoring & Maintenance

### Application Logs

```bash
# Django logs
tail -f /var/log/job_tracker/django.log

# Gunicorn logs
tail -f /var/log/gunicorn/error.log

# Celery logs
tail -f /var/log/celery/worker.log
tail -f /var/log/celery/beat.log

# Nginx logs
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log
```

### Database Backup

```bash
# Create backup script: /usr/local/bin/backup_db.sh
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/var/backups/postgresql"
mkdir -p $BACKUP_DIR

pg_dump -U job_tracker_user job_tracker_db > $BACKUP_DIR/backup_$DATE.sql
gzip $BACKUP_DIR/backup_$DATE.sql

# Keep only last 7 days
find $BACKUP_DIR -type f -mtime +7 -delete
```

Schedule with cron:
```bash
sudo crontab -e
# Add: 0 2 * * * /usr/local/bin/backup_db.sh
```

### Media Files Backup

```bash
# Backup media files
rsync -av /path/to/media/ /backup/location/media/
```

### System Updates

```bash
# Update system packages
sudo apt-get update && sudo apt-get upgrade

# Update Python packages (carefully!)
pip list --outdated
pip install --upgrade package-name

# Restart services after updates
sudo systemctl restart gunicorn celery celerybeat
```

### Performance Monitoring

Consider using:
- **Sentry** - Error tracking
- **New Relic** - Application performance monitoring
- **Prometheus + Grafana** - Metrics and dashboards
- **UptimeRobot** - Uptime monitoring

---

## Troubleshooting

### Common Issues

**Issue**: Static files not loading
```bash
# Solution:
python manage.py collectstatic --clear --noinput
sudo systemctl restart nginx
```

**Issue**: Celery tasks not executing
```bash
# Check Celery status
sudo systemctl status celery

# Check Redis connection
redis-cli ping

# Restart Celery
sudo systemctl restart celery celerybeat
```

**Issue**: Database connection errors
```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Check database credentials in .env
# Verify database exists
sudo -u postgres psql -l
```

**Issue**: Permission denied errors
```bash
# Fix ownership
sudo chown -R www-data:www-data /path/to/project
sudo chmod -R 755 /path/to/project
```

---

## Additional Resources

- [Django Deployment Checklist](https://docs.djangoproject.com/en/stable/howto/deployment/checklist/)
- [Celery Production Guide](https://docs.celeryproject.org/en/stable/userguide/deployment.html)
- [Gunicorn Documentation](https://docs.gunicorn.org/)
- [Nginx Documentation](https://nginx.org/en/docs/)

---

## Support

For issues or questions:
1. Check application logs
2. Review Django documentation
3. Check GitHub issues
4. Consult the README.md file

**Happy Deploying! 🚀**
