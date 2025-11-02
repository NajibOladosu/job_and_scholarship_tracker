#!/bin/bash
# Wait for database to be ready before starting
# This script wraps the Python-based database readiness check

set -e

# Use Python-based check for better error handling and DNS resolution support
python wait_for_db.py
