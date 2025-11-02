web: bash start.sh
worker: bash wait-for-db.sh && celery -A config worker --loglevel=info
beat: bash wait-for-db.sh && celery -A config beat --loglevel=info
