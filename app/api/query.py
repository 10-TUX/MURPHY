"""MURPHY - Query API."""

from fastapi import APIRouter, HTTPException

from app.models.api_models import QueryRequest, QueryResponse
from app.services.rag_service import RAGService


router = APIRouter(
    prefix="/api",
    tags=["Query"],
)


# Temporary application-level RAG service.
# Session-specific RAG state will be introduced in Step 8.
_rag_service: RAGService | None = None


def set_rag_service(rag_service: RAGService) -> None:
    """Set the RAG service used by the query endpoint."""
    global _rag_service
    _rag_service = rag_service


@router.post("/query", response_model=QueryResponse)
async def query(request: QueryRequest) -> QueryResponse:
    """Answer a question using the MURPHY RAG pipeline."""

    if _rag_service is None:
        raise HTTPException(
            status_code=503,
            detail="RAG service is not initialized.",
        )

    try:
        result = _rag_service.invoke(request.question)

        sources = []

        for document in result.documents:
            metadata = document.metadata

            sources.append(
                {
                    "source": metadata.get("source", "unknown"),
                    "start_line": metadata.get("start_line"),
                    "end_line": metadata.get("end_line"),
                }
            )

        return QueryResponse(
            answer=result.answer,
            sources=sources,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc
