# Railway Procfile - Updated for stable deployment
web: bash start.sh
worker: bash -c "source /opt/venv/bin/activate && bash wait-for-db.sh && celery -A config worker --loglevel=info --concurrency=2 --max-tasks-per-child=1000"
beat: bash -c "source /opt/venv/bin/activate && bash wait-for-db.sh && celery -A config beat --loglevel=info"
