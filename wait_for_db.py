#!/usr/bin/env python
"""
Wait for database to be ready before starting services.
Handles DNS resolution delays in Railway deployment.
"""
import os
import sys
import time
import socket
import psycopg2
from urllib.parse import urlparse

MAX_RETRIES = 60
RETRY_INTERVAL = 3

print("=" * 60)
print("DATABASE READINESS CHECK")
print("=" * 60)
print(f"Max wait time: {MAX_RETRIES * RETRY_INTERVAL} seconds ({MAX_RETRIES} attempts)")
print()

# Get DATABASE_URL from environment
DATABASE_URL = os.environ.get('DATABASE_URL')
if not DATABASE_URL:
    print("ERROR: DATABASE_URL environment variable not set!")
    sys.exit(1)

# Parse DATABASE_URL
parsed = urlparse(DATABASE_URL)
host = parsed.hostname
port = parsed.port or 5432
database = parsed.path.lstrip('/')
user = parsed.username
password = parsed.password

print(f"Database host: {host}")
print(f"Database port: {port}")
print(f"Database name: {database}")
print()

for attempt in range(1, MAX_RETRIES + 1):
    try:
        # Step 1: Test DNS resolution
        print(f"[{attempt}/{MAX_RETRIES}] Attempting DNS resolution for '{host}'...")
        ip_address = socket.gethostbyname(host)
        print(f"  ✓ DNS resolved to: {ip_address}")

        # Step 2: Test database connection
        print(f"[{attempt}/{MAX_RETRIES}] Attempting database connection...")
        conn = psycopg2.connect(
            host=host,
            port=port,
            database=database,
            user=user,
            password=password,
            connect_timeout=10
        )

        # Test the connection
        cursor = conn.cursor()
        cursor.execute('SELECT 1')
        cursor.close()
        conn.close()

        print(f"  ✓ Database connection successful!")
        print()
        print("=" * 60)
        print("DATABASE IS READY! Starting service...")
        print("=" * 60)
        sys.exit(0)

    except socket.gaierror as e:
        # DNS resolution failed
        print(f"  ✗ DNS resolution failed: {e}")
        print(f"  Note: Railway internal DNS can take 30-60 seconds on first startup")

        if attempt >= MAX_RETRIES:
            print()
            print("=" * 60)
            print(f"ERROR: DNS not resolved after {MAX_RETRIES} attempts")
            print("=" * 60)
            sys.exit(1)

    except psycopg2.OperationalError as e:
        error_msg = str(e)
        print(f"  ✗ Database connection failed: {error_msg[:100]}")

        if "Connection refused" in error_msg:
            print(f"  Note: Database container is starting up...")
        elif "does not exist" in error_msg:
            print(f"  Note: Waiting for database initialization...")

        if attempt >= MAX_RETRIES:
            print()
            print("=" * 60)
            print(f"ERROR: Database not ready after {MAX_RETRIES} attempts")
            print(f"Last error: {error_msg}")
            print("=" * 60)
            sys.exit(1)

    except Exception as e:
        print(f"  ✗ Unexpected error: {type(e).__name__}: {e}")

        if attempt >= MAX_RETRIES:
            print()
            print("=" * 60)
            print(f"ERROR: Failed after {MAX_RETRIES} attempts")
            print("=" * 60)
            sys.exit(1)

    # Wait before next attempt
    if attempt < MAX_RETRIES:
        print(f"  Waiting {RETRY_INTERVAL} seconds before retry...")
        print()
        time.sleep(RETRY_INTERVAL)
