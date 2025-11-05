#!/bin/bash
# Railway start script - collects static files, runs migrations, then starts web server

# Exit on error
set -e

echo "Collecting static files..."
python manage.py collectstatic --noinput --settings=config.settings.production

echo "Running database migrations..."
python manage.py migrate --settings=config.settings.production --noinput

echo "Starting web server..."
exec gunicorn config.wsgi:application --bind 0.0.0.0:$PORT --workers 3 --timeout 120
