"""
Settings module initialization.
Automatically loads the appropriate settings based on the DJANGO_SETTINGS_MODULE environment variable.
"""

import os

# Determine which settings to use
# Default to development if not specified
env = os.environ.get('DJANGO_ENV', 'development')

if env == 'production':
    from .production import *
elif env == 'development':
    from .development import *
else:
    from .development import *
