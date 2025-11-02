#!/bin/bash
# Wait for database to be ready before starting

set -e

echo "Waiting for database to be ready..."

MAX_RETRIES=30
RETRY_INTERVAL=2
counter=0

until python manage.py migrate --check --settings=config.settings.production 2>/dev/null; do
  counter=$((counter + 1))
  if [ $counter -gt $MAX_RETRIES ]; then
    echo "Database is not ready after $MAX_RETRIES attempts. Exiting..."
    exit 1
  fi
  echo "Database not ready yet (attempt $counter/$MAX_RETRIES). Waiting ${RETRY_INTERVAL}s..."
  sleep $RETRY_INTERVAL
done

echo "Database is ready!"
