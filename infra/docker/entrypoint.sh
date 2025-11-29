#!/bin/bash
set -e

# Run database migrations if needed
# python scripts/migrate_pgvector.py

# Start the application
exec uvicorn src.app:app --host 0.0.0.0 --port 8000

