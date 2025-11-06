#!/bin/bash
# Railway Celery beat start script

# Exit on error
set -e

# Wait for database to be ready
bash wait-for-db.sh

# Activate virtual environment
source /opt/venv/bin/activate

echo "Starting Celery beat..."
exec celery -A config beat --loglevel=info
