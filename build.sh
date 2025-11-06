#!/bin/bash
# Railway build script

# Exit on error
set -e

echo "Installing Python dependencies..."
pip install -r requirements.txt

echo "Building React frontend..."
cd frontend
npm install
npm run build
cd ..

echo "Collecting static files..."
python manage.py collectstatic --noinput --settings=config.settings.production

echo "Build complete!"
