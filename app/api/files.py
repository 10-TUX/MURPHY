"""MURPHY - Files API."""

from fastapi import APIRouter, HTTPException

from app.models.api_models import FilesResponse
from app.services.repository_service import collect_file_metadata
from app.services.session_service import session_service


router = APIRouter(
    prefix="/api",
    tags=["Files"],
)


@router.get("/files", response_model=FilesResponse)
async def get_files(session_id: str) -> FilesResponse:
    """Return files belonging to a repository session."""

    session = session_service.get_session(session_id)

    if session is None:
        raise HTTPException(
            status_code=404,
            detail="Session not found.",
        )

    files = collect_file_metadata(session.repository_path)

    return FilesResponse(
        files=files,
    )
