# Docker Setup Guide

This guide explains how to run the Knowledge Chat Bot with Docker, including Redis, PostgreSQL, and Celery workers for processing Excel and CSV files.

## Prerequisites

- Docker and Docker Compose installed
- `.env` file configured (copy from `.env.example`)

## Services

The `docker-compose.yml` includes the following services:

1. **PostgreSQL** (with pgvector extension) - Database for storing vectors and metadata
2. **Redis** - Message broker and result backend for Celery
3. **API** - FastAPI application
4. **Celery Worker** - Background worker for processing documents
5. **Celery Beat** - Task scheduler (optional, for periodic tasks)

## Quick Start

1. **Create environment file:**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

2. **Start all services:**
   ```bash
   docker-compose up -d
   ```

3. **View logs:**
   ```bash
   # All services
   docker-compose logs -f
   
   # Specific service
   docker-compose logs -f celery-worker
   docker-compose logs -f api
   ```

4. **Stop services:**
   ```bash
   docker-compose down
   ```

5. **Stop and remove volumes:**
   ```bash
   docker-compose down -v
   ```

## API Endpoints

Once running, the API will be available at `http://localhost:8000`:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **Health Check**: `http://localhost:8000/health/`

## Uploading Files

### Using curl:

```bash
curl -X POST "http://localhost:8000/api/v1/ingest/file" \
  -H "accept: application/json" \
  -F "file=@/path/to/your/file.xlsx" \
  -F "document_id=optional-doc-id"
```

### Using Python:

```python
import requests

url = "http://localhost:8000/api/v1/ingest/file"
files = {"file": open("data.xlsx", "rb")}
data = {"document_id": "my-document-123"}

response = requests.post(url, files=files, data=data)
print(response.json())
```

## Checking Task Status

You can check the status of a Celery task using the task ID returned in the response:

```python
from celery.result import AsyncResult
from src.celery_app import celery_app

task_id = "your-task-id-here"
result = AsyncResult(task_id, app=celery_app)
print(f"Status: {result.status}")
print(f"Result: {result.result}")
```

## Supported File Types

- **Excel**: `.xlsx`, `.xls`
- **CSV**: `.csv`

## Troubleshooting

### Check service status:
```bash
docker-compose ps
```

### Restart a specific service:
```bash
docker-compose restart celery-worker
```

### Access service shell:
```bash
docker-compose exec api bash
docker-compose exec celery-worker bash
```

### View Redis data:
```bash
docker-compose exec redis redis-cli
```

### View PostgreSQL:
```bash
docker-compose exec postgres psql -U postgres -d knowledge_chat
```

## Development

For development, you can mount your source code:

```yaml
volumes:
  - ./src:/app/src
```

This allows hot-reloading during development (restart containers to see changes).

## Production Considerations

- Use environment variables for sensitive data
- Configure proper database backups
- Set up monitoring for Celery workers
- Use a reverse proxy (nginx) in front of the API
- Configure proper resource limits in docker-compose.yml

