"""MURPHY — Session Management Service."""

from dataclasses import dataclass
from pathlib import Path
from tempfile import TemporaryDirectory


@dataclass
class RepositorySession:
    """Stores state for an active MURPHY repository session."""

    session_id: str
    repository_path: Path
    source: str


class SessionService:
    """Manage active repository sessions."""

    def __init__(self) -> None:
        self._sessions: dict[str, RepositorySession] = {}
        self._workspaces: dict[str, TemporaryDirectory] = {}

    def create_session(
        self,
        session_id: str,
        repository_path: Path,
        source: str,
        workspace: TemporaryDirectory | None = None,
    ) -> RepositorySession:
        """Create and store a repository session."""
        if session_id in self._sessions:
            raise ValueError(f"Session already exists: {session_id}")

        session = RepositorySession(
            session_id=session_id,
            repository_path=repository_path,
            source=source,
        )

        self._sessions[session_id] = session

        if workspace is not None:
            self._workspaces[session_id] = workspace

        return session

    def get_session(self, session_id: str) -> RepositorySession | None:
        """Return an active session, if it exists."""

        return self._sessions.get(session_id)

    def remove_session(self, session_id: str) -> None:
        """Remove a session and clean up its workspace."""

        self._sessions.pop(session_id, None)

        workspace = self._workspaces.pop(session_id, None)

        if workspace is not None:
            workspace.cleanup()

    def has_session(self, session_id: str) -> bool:
        """Return whether a session exists."""
        return session_id in self._sessions

    def clear(self) -> None:
        """Remove all sessions and clean up their workspaces."""
        for session_id in list(self._sessions):
            self.remove_session(session_id)
