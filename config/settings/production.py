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
# Use PostgreSQL in production (configured via environment variables)
# During build phase (collectstatic), database isn't needed, so we provide defaults
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME', default=''),
        'USER': config('DB_USER', default=''),
        'PASSWORD': config('DB_PASSWORD', default=''),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default='5432'),
    }
}

# Check if DATABASE_URL is provided (Railway provides this)
DATABASE_URL = config('DATABASE_URL', default=None)
if DATABASE_URL:
    import dj_database_url
    DATABASES['default'] = dj_database_url.parse(DATABASE_URL)


# Email Configuration - Use SMTP in production
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'


# Security Settings
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
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'django.log',
            'maxBytes': 1024 * 1024 * 15,  # 15MB
            'backupCount': 10,
            'formatter': 'verbose',
        },
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'WARNING',
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'WARNING',
            'propagate': False,
        },
        'tracker': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}


# Celery - Use Redis broker in production
CELERY_TASK_ALWAYS_EAGER = False


# Static files - Ensure WhiteNoise is properly configured
# Already set in base.py, but verify STATIC_ROOT is correct
# STATIC_ROOT should be collected using: python manage.py collectstatic
