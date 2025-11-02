"""
Production settings for Job & Scholarship Tracker project.
These settings are used in production deployment.
"""

from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

# ALLOWED_HOSTS should be set via environment variable in production
# Example: ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com


# Database
# Use PostgreSQL in production (configured via DATABASE_URL from Railway)
DATABASE_URL = config('DATABASE_URL', default=None)
if DATABASE_URL:
    import dj_database_url
    DATABASES = {
        'default': dj_database_url.parse(DATABASE_URL)
    }
else:
    # Fallback for manual configuration (without DATABASE_URL)
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': config('DB_NAME', default='postgres'),
            'USER': config('DB_USER', default='postgres'),
            'PASSWORD': config('DB_PASSWORD', default=''),
            'HOST': config('DB_HOST', default='localhost'),
            'PORT': config('DB_PORT', default='5432'),
        }
    }


# Email Configuration - Use SMTP in production
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'


# Security Settings
# Railway uses a reverse proxy, so we need to trust the X-Forwarded-Proto header
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
X_FRAME_OPTIONS = 'DENY'


# Logging Configuration
import os

# Create logs directory if it doesn't exist
LOGS_DIR = BASE_DIR / 'logs'
os.makedirs(LOGS_DIR, exist_ok=True)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'WARNING',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'WARNING',
            'propagate': False,
        },
        'tracker': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}


# Celery - Use Redis broker in production
CELERY_TASK_ALWAYS_EAGER = False

# Railway provides REDIS_URL automatically when you add Redis service
REDIS_URL = config('REDIS_URL', default=None)
if REDIS_URL:
    CELERY_BROKER_URL = REDIS_URL
    CELERY_RESULT_BACKEND = REDIS_URL

# Celery worker configuration for Railway deployment
# CRITICAL: Limit concurrency to prevent OOM crashes on Railway
CELERYD_CONCURRENCY = 2  # Maximum 2 worker processes
CELERY_WORKER_CONCURRENCY = 2  # Alternative setting name
CELERY_WORKER_PREFETCH_MULTIPLIER = 1
CELERY_WORKER_MAX_TASKS_PER_CHILD = 1000  # Recycle worker after 1000 tasks to prevent memory leaks
CELERY_TASK_ACKS_LATE = True  # Tasks are acknowledged after completion, not before
CELERY_TASK_REJECT_ON_WORKER_LOST = True  # Re-queue tasks if worker dies
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True  # Retry broker connection on startup

# Task time limits (prevent runaway tasks)
CELERY_TASK_SOFT_TIME_LIMIT = 300  # 5 minutes soft limit
CELERY_TASK_TIME_LIMIT = 600  # 10 minutes hard limit

# Result backend settings
CELERY_RESULT_EXPIRES = 3600  # Results expire after 1 hour
CELERY_RESULT_BACKEND_MAX_RETRIES = 10


# Static files - Ensure WhiteNoise is properly configured
# Already set in base.py, but verify STATIC_ROOT is correct
# STATIC_ROOT should be collected using: python manage.py collectstatic
