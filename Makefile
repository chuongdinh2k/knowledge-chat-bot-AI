.PHONY: install run test lint format clean docker-build docker-run

api-install:
	uv pip install -r requirements.txt

# Alternative: install from pyproject.toml
# install:
# 	uv pip install -e .

api-run:
	uv run uvicorn src.app:app --reload --host 0.0.0.0 --port 8000

test:
	uv run pytest tests/

lint:
	# Add linting command here
	@echo "Linting not configured yet"

format:
	# Add formatting command here
	@echo "Formatting not configured yet"

clean:
	find . -type d -name __pycache__ -exec rm -r {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete

# api-build:
# 	docker build -t knowledge-chat-bot -f infra/docker/Dockerfile .

# api-run:
# 	docker run -p 8000:8000 knowledge-chat-bot

build-services:
	docker compose build

run-services:
	docker compose up -d

stop-services:
	docker compose down

logs-services:
	docker compose logs -f
	