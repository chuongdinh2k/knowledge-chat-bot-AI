"""Query request models."""
from pydantic import BaseModel
from typing import Optional, List, Dict, Any


class QueryRequest(BaseModel):
    """Request model for querying."""
    query: str
    top_k: Optional[int] = 5
    filters: Optional[Dict[str, Any]] = None


class QueryResponse(BaseModel):
    """Response model for querying."""
    answer: str
    sources: List[Dict[str, Any]]
    metadata: Optional[Dict[str, Any]] = None

