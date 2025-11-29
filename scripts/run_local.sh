#!/bin/bash
set -e

echo "Starting Knowledge Chat Bot API locally..."

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Run the application
uvicorn src.app:app --reload --host 0.0.0.0 --port 8000

