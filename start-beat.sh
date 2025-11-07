#!/bin/bash
# Railway Celery beat start script

# Exit on error
set -e

echo "=== Celery Beat Startup ==="

# Wait for database to be ready
bash wait-for-db.sh

# Try to find and activate virtual environment
VENV_ACTIVATED=false

# Option 1: Try /opt/venv (created by nixpacks)
if [ -d "/opt/venv" ] && [ -f "/opt/venv/bin/activate" ]; then
    echo "Found venv at /opt/venv"
    source /opt/venv/bin/activate
    VENV_ACTIVATED=true
# Option 2: Try local venv
elif [ -d "venv" ] && [ -f "venv/bin/activate" ]; then
    echo "Found local venv"
    source venv/bin/activate
    VENV_ACTIVATED=true
# Option 3: Create new venv if neither exists
else
    echo "No venv found. Creating new venv..."
    python3 -m venv /tmp/beat_venv
    source /tmp/beat_venv/bin/activate
    echo "Installing requirements..."
    pip install --no-cache-dir -r requirements.txt
    VENV_ACTIVATED=true
fi

# Verify Python and Celery are available
echo "Python path: $(which python)"
echo "Python version: $(python --version)"

# Check if celery module is available
if python -c "import celery" 2>/dev/null; then
    echo "Celery module found"
else
    echo "ERROR: Celery module not found. Installing requirements..."
    pip install --no-cache-dir -r requirements.txt
fi

echo "Starting Celery beat..."
# Use python -m celery to ensure we use the right Python environment
exec python -m celery -A config beat --loglevel=info
