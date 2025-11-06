# Railway Procfile - Updated for stable deployment
web: bash start.sh
worker: bash -c "bash wait-for-db.sh && /opt/venv/bin/celery -A config worker --loglevel=info --concurrency=2 --max-tasks-per-child=1000"
beat: bash -c "bash wait-for-db.sh && /opt/venv/bin/celery -A config beat --loglevel=info"
