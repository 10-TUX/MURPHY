"""MURPHY - Query API."""

from fastapi import APIRouter, HTTPException

from app.models.api_models import QueryRequest, QueryResponse
from app.services.rag_service import RAGService
from app.services.session_service import session_service


router = APIRouter(
    prefix="/api",
    tags=["Query"],
)


def set_rag_service(
    session_id: str,
    rag_service: RAGService,
) -> None:
    """Attach a RAG service to a repository session."""
    session_service.set_rag_service(
        session_id,
        rag_service,
    )


@router.post("/query", response_model=QueryResponse)
async def query(
    request: QueryRequest,
    session_id: str,
) -> QueryResponse:
    """Answer a question using the MURPHY RAG service for a session."""

    session = session_service.get_session(session_id)

    if session is None:
        raise HTTPException(
            status_code=404,
            detail=f"Session not found.",
        )
    if session.rag_service is None:
        raise HTTPException(
            status_code=503,
            detail="RAG service is not initialized for this session.",
        )
    try:
        result = session.rag_service.invoke(request.question)

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
