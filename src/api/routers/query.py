"""Query router."""
from fastapi import APIRouter, Depends, HTTPException
from src.api.models.query_request import QueryRequest, QueryResponse
from src.services.rag_service import RAGService

router = APIRouter()


def get_rag_service() -> RAGService:
    """Dependency for RAG service."""
    return RAGService()


@router.post("/", response_model=QueryResponse)
async def query(
    request: QueryRequest,
    rag_service: RAGService = Depends(get_rag_service)
):
    """Query the knowledge base."""
    try:
        result = await rag_service.query(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

