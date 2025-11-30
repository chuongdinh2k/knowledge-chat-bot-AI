"""Query router."""
from fastapi import APIRouter, Depends, HTTPException
from src.api.models.query_request import QueryRequest, QueryResponse
from src.services.rag_service import RAGService
from src.core.config import settings


router = APIRouter(
    prefix="/api/v1/query",
    tags=["query", "v1"]
)

def get_rag_service() -> RAGService:
    """Dependency for RAG service."""
    return RAGService()

# API Version constant
API_VERSION = "v1"

@router.post("/", response_model=QueryResponse)
async def query(
    request: QueryRequest,
    rag_service: RAGService = Depends(get_rag_service)
):
    """Query the knowledge base.
    
    **API Version:** v1
    """
    try:
        result = await rag_service.query(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/version")
async def get_version():
    """
    Get the API version information for query endpoints.
    
    **API Version:** v1
    """
    return {
        "api_version": settings.api_version,
        "endpoint_version": API_VERSION,
        "endpoints": {
            "query": "/api/v1/query/",
            "version": "/api/v1/query/version"
        }
    }

