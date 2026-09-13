"""MURPHY - Status API."""

from fastapi import APIRouter

from app.api import query
from app.models.api_models import StatusResponse


router = APIRouter(
    prefix="/api",
    tags=["Status"],
)


@router.get("/status", response_model=StatusResponse)
async def get_status() -> StatusResponse:
    """Return the current MURPHY service status."""

    if query._rag_service is None:
        return StatusResponse(
            status="not_ready",
            message="RAG service is not initialized.",
        )

    return StatusResponse(
        status="ready",
        message="MURPHY RAG service is ready.",
    )
