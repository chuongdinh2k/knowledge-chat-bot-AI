"""Main FastAPI application."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.core.config import settings
from src.core.logging import setup_logging
from src.api.routers import health, ingest, query

# Setup logging
setup_logging()

# Create FastAPI app
app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    debug=settings.debug
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, prefix="/health", tags=["health"])
app.include_router(ingest.router, prefix="/api/v1/ingest", tags=["ingestion"])
app.include_router(query.router, prefix="/api/v1/query", tags=["query"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Knowledge Chat Bot API", "version": settings.api_version}

