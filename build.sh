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

# Ensure the dist directory exists and has content
if [ ! -f "frontend/dist/index.html" ]; then
    echo "ERROR: Frontend build failed - index.html not found!"
    exit 1
fi

echo "Frontend build successful. Contents of frontend/dist:"
ls -la frontend/dist/

echo "Collecting static files..."
python manage.py collectstatic --noinput --settings=config.settings.production

echo "Build complete!"
