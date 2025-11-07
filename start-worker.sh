#!/bin/bash
# Railway Celery worker start script

# Exit on error
set -e

# Wait for database to be ready
bash wait-for-db.sh

# Activate virtual environment
source /opt/venv/bin/activate

echo "Starting Celery worker..."
exec celery -A config worker --loglevel=info --concurrency=2 --max-tasks-per-child=1000