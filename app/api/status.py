"""MURPHY - Status API."""

from fastapi import APIRouter, HTTPException

from app.models.api_models import StatusResponse
from app.services.session_service import session_service


router = APIRouter(
    prefix="/api",
    tags=["Status"],
)


@router.get("/status", response_model=StatusResponse)
async def get_status(session_id: str | None = None) -> StatusResponse:
    """Return the current MURPHY service status."""
    if session_id is not None:
        session = session_service.get_session(session_id)
        if session is None:
            raise HTTPException(
                status_code=404,
                detail=f"Session not found.",
            )
        if session.rag_service is None:
            return StatusResponse(
                status="not_ready",
                message="RAG service is not initialized for this session.",
            )
        return StatusResponse(
            status="ready",
            message="MURPHY RAG service is ready.",
        )

    has_ready_session = any(
        s.rag_service is not None for s in session_service.list_sessions()
    )
    if not has_ready_session:
        return StatusResponse(
            status="not_ready",
            message="RAG service is not initialized.",
        )

    return StatusResponse(
        status="ready",
        message="MURPHY RAG service is ready.",
    )
