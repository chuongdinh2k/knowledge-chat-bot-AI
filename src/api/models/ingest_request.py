"""Ingestion request models."""
from pydantic import BaseModel
from typing import Optional, Dict, Any


class IngestRequest(BaseModel):
    """Request model for document ingestion."""
    content: str
    metadata: Optional[Dict[str, Any]] = None
    document_id: Optional[str] = None


class IngestResponse(BaseModel):
    """Response model for document ingestion."""
    document_id: str
    status: str
    message: str
    task_id: Optional[str] = None
    api_version: Optional[str] = "v1"  # Add version to response