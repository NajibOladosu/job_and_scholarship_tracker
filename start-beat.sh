#!/bin/bash
# Railway Celery beat start script

# Exit on error
set -e

# Wait for database to be ready
bash wait-for-db.sh

# Activate virtual environment if it exists
if [ -d "/opt/venv" ]; then
    source /opt/venv/bin/activate
    echo "Using virtualenv at /opt/venv"
elif [ -d "venv" ]; then
    source venv/bin/activate
    echo "Using local virtualenv"
fi

echo "Starting Celery beat..."
echo "Python path: $(which python)"
echo "Celery path: $(which celery || echo 'celery not in PATH')"

# Use python -m celery to ensure we use the right Python environment
exec python -m celery -A config beat --loglevel=info
