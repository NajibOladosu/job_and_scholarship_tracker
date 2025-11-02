#!/bin/bash
# Railway build script

# Exit on error
set -e

echo "Collecting static files..."
python manage.py collectstatic --noinput --settings=config.settings.production

echo "Build complete!"
