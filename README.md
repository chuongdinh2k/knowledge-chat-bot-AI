# Knowledge Chat Bot

A RAG (Retrieval Augmented Generation) based knowledge chat bot API built with FastAPI.

## Project Structure

```
project-root/
├── src/                    # Source code
│   ├── api/               # API routes and models
│   ├── core/              # Core configuration and utilities
│   ├── services/          # Business logic services
│   ├── vectorstore/       # Vector database client
│   ├── embeddings/        # Embedding generation
│   ├── loaders/           # Document loaders
│   ├── llm/               # LLM integration
│   └── utils/             # Utility functions
├── infra/                 # Infrastructure as code
│   ├── terraform/         # Terraform configurations
│   └── docker/            # Docker files
├── tests/                 # Test files
└── scripts/               # Utility scripts
```

## Getting Started

### Prerequisites

- Python 3.11+
- pip

### Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file (optional):
   ```
   DATABASE_URL=postgresql://user:password@localhost/dbname
   OPENAI_API_KEY=your_api_key
   DEBUG=False
   ```

### Running Locally

```bash
uvicorn src.app:app --reload
```

The API will be available at `http://localhost:8000`

### API Endpoints

- `GET /` - Root endpoint
- `GET /health/` - Health check
- `GET /health/ready` - Readiness check
- `POST /api/v1/ingest/` - Ingest a document
- `POST /api/v1/query/` - Query the knowledge base

### API Documentation

Once running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Development

This is a base implementation with placeholder logic. The following components need to be implemented:

- Database connection and pgvector integration
- LLM client integration (OpenAI)
- Embedding generation
- Document loaders (PDF, Markdown, Text)
- Vector search and retrieval
- RAG pipeline

## License

MIT

