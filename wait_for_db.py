#!/usr/bin/env python
"""
Wait for database to be ready before starting services.
Handles DNS resolution delays in Railway deployment.
"""
import os
import sys
import time
import django
from django.core.management import execute_from_command_line

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')
django.setup()

from django.db import connections
from django.db.utils import OperationalError

MAX_RETRIES = 60
RETRY_INTERVAL = 3

print("Waiting for database to be ready...")
print(f"Max wait time: {MAX_RETRIES * RETRY_INTERVAL} seconds")

for attempt in range(1, MAX_RETRIES + 1):
    try:
        # Try to connect to the database
        conn = connections['default']
        conn.ensure_connection()

        # If we get here, connection was successful
        print(f"✓ Database connection successful on attempt {attempt}")

        # Verify migrations are up to date
        try:
            from django.core.management import call_command
            from io import StringIO

            out = StringIO()
            call_command('migrate', '--check', stdout=out, stderr=out)
            print("✓ All migrations are up to date")
            print("Database is ready! Starting service...")
            sys.exit(0)

        except SystemExit as e:
            if e.code == 0:
                print("✓ All migrations are up to date")
                print("Database is ready! Starting service...")
                sys.exit(0)
            else:
                print(f"⚠ Migrations check returned exit code {e.code}")
                print("Database is ready! Starting service...")
                sys.exit(0)

    except OperationalError as e:
        error_msg = str(e)

        if attempt >= MAX_RETRIES:
            print(f"\n✗ ERROR: Database not ready after {MAX_RETRIES} attempts ({MAX_RETRIES * RETRY_INTERVAL} seconds)")
            print(f"Last error: {error_msg}")
            sys.exit(1)

        # Provide helpful feedback based on error type
        if "could not translate host name" in error_msg:
            print(f"[{attempt}/{MAX_RETRIES}] Waiting for DNS resolution... (Railway internal DNS can take 30-60s on startup)")
        elif "Connection refused" in error_msg:
            print(f"[{attempt}/{MAX_RETRIES}] Database container is starting...")
        elif "does not exist" in error_msg:
            print(f"[{attempt}/{MAX_RETRIES}] Waiting for database initialization...")
        else:
            print(f"[{attempt}/{MAX_RETRIES}] Database not ready: {error_msg[:100]}")

        time.sleep(RETRY_INTERVAL)

    except Exception as e:
        print(f"Unexpected error: {e}")
        if attempt >= MAX_RETRIES:
            sys.exit(1)
        time.sleep(RETRY_INTERVAL)
