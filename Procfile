web: bash start.sh
worker: bash wait-for-db.sh && celery -A config worker --loglevel=info --concurrency=2 --max-tasks-per-child=1000
beat: bash wait-for-db.sh && celery -A config beat --loglevel=info
