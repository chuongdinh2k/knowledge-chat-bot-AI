.PHONY: install run test lint format clean docker-build docker-run

install:
	uv pip install -r requirements.txt

# Alternative: install from pyproject.toml
# install:
# 	uv pip install -e .

run:
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

docker-build:
	docker build -t knowledge-chat-bot -f infra/docker/Dockerfile .

docker-run:
	docker run -p 8000:8000 knowledge-chat-bot