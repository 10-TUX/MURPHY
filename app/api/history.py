"""MURPHY - History API."""

from fastapi import APIRouter, HTTPException

from app.models.api_models import HistoryMessage, HistoryResponse
from app.services.session_service import session_service


router = APIRouter(
    prefix="/api",
    tags=["History"],
)


@router.get("/history", response_model=HistoryResponse)
async def get_history(session_id: str) -> HistoryResponse:
    """Return conversation history for a repository session."""

    session = session_service.get_session(session_id)

    if session is None:
        raise HTTPException(
            status_code=404,
            detail="Session not found.",
        )

    if session.rag_service is None:
        return HistoryResponse(messages=[])

    messages = []

    for message in session.rag_service.chat_history:
        if message.type == "human":
            role = "user"
        elif message.type == "ai":
            role = "assistant"
        else:
            role = message.type

        messages.append(
            HistoryMessage(
                role=role,
                content=message.content,
            )
        )

    return HistoryResponse(messages=messages)
