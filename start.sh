#!/bin/bash
# Railway start script - runs migrations then starts the web server

# Exit on error
set -e

echo "Running database migrations..."
python manage.py migrate --settings=config.settings.production --noinput

echo "Starting web server..."
exec gunicorn config.wsgi:application --bind 0.0.0.0:$PORT --workers 3 --timeout 120
