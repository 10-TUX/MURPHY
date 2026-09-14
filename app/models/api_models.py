"""MURPHY API request and response models."""

from datetime import datetime

from pydantic import BaseModel, Field

from app.models.file_metadata import FileMetadata


# ─────────────────────────────────────────────
# Repository
# ─────────────────────────────────────────────


class RepositoryUploadResponse(BaseModel):
    """Response returned after a repository is loaded."""

    status: str
    source: str
    repository_path: str
    message: str
    session_id: str
    filename: str | None = None
    file_count: int | None = None
    files: list[FileMetadata] = Field(default_factory=list)


# ─────────────────────────────────────────────
# Query / RAG
# ─────────────────────────────────────────────


class QueryRequest(BaseModel):
    """Request containing a user's question."""

    question: str = Field(min_length=1)


class SourceReference(BaseModel):
    """Reference to a source used to answer a question."""

    source: str
    start_line: int | None = None
    end_line: int | None = None


class QueryResponse(BaseModel):
    """Response returned by the RAG query endpoint."""

    answer: str
    sources: list[SourceReference] = Field(default_factory=list)


# ─────────────────────────────────────────────
# Status
# ─────────────────────────────────────────────


class StatusResponse(BaseModel):
    """Current repository indexing status."""

    status: str
    message: str | None = None


# ─────────────────────────────────────────────
# Files
# ─────────────────────────────────────────────


class FilesResponse(BaseModel):
    """List of files indexed for the current repository."""

    files: list[FileMetadata] = Field(default_factory=list)


# ─────────────────────────────────────────────
# Conversation history
# ─────────────────────────────────────────────


class HistoryMessage(BaseModel):
    """Single message in a conversation."""

    role: str
    content: str
    timestamp: datetime | None = None


class HistoryResponse(BaseModel):
    """Conversation history for a session."""

    messages: list[HistoryMessage] = Field(default_factory=list)
