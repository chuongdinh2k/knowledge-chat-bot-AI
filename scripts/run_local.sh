#!/bin/bash
set -e

echo "Starting Knowledge Chat Bot API locally..."

# Activate virtual environment if it exists (check .venv first, then venv)
if [ -d ".venv" ]; then
    source .venv/bin/activate
    echo "Activated .venv"
elif [ -d "venv" ]; then
    source venv/bin/activate
    echo "Activated venv"
else
    echo "Warning: No virtual environment found. Using system Python."
fi

# Load environment variables from .env if it exists
if [ -f ".env" ]; then
    export $(cat .env | grep -v '^#' | xargs)
    echo "Loaded .env file"
fi

# Run the application
uv run uvicorn src.app:app --reload --host 0.0.0.0 --port 8000
