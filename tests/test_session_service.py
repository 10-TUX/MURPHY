from pathlib import Path
from tempfile import TemporaryDirectory

import pytest

from app.services.session_service import SessionService


def test_create_and_get_session(tmp_path):
    """A created session should be retrievable."""

    service = SessionService()

    session = service.create_session(
        session_id="test-session",
        repository_path=tmp_path,
        source="local_path",
    )

    assert session.session_id == "test-session"
    assert session.repository_path == tmp_path
    assert session.source == "local_path"

    retrieved = service.get_session("test-session")

    assert retrieved == session
    assert service.has_session("test-session") is True


def test_get_missing_session_returns_none():
    """Unknown sessions should return None."""

    service = SessionService()

    assert service.get_session("missing") is None
    assert service.has_session("missing") is False


def test_duplicate_session_is_rejected(tmp_path):
    """A session ID cannot be reused."""

    service = SessionService()

    service.create_session(
        session_id="duplicate",
        repository_path=tmp_path,
        source="local_path",
    )

    with pytest.raises(ValueError, match="Session already exists"):
        service.create_session(
            session_id="duplicate",
            repository_path=tmp_path,
            source="local_path",
        )


def test_remove_session(tmp_path):
    """Removing a session should make it unavailable."""

    service = SessionService()

    service.create_session(
        session_id="remove-me",
        repository_path=tmp_path,
        source="local_path",
    )

    service.remove_session("remove-me")

    assert service.get_session("remove-me") is None
    assert service.has_session("remove-me") is False


def test_remove_session_cleans_workspace(tmp_path):
    """Removing a session should clean up its temporary workspace."""

    service = SessionService()

    workspace = TemporaryDirectory(prefix="murphy_test_")
    workspace_path = Path(workspace.name)

    assert workspace_path.exists()

    service.create_session(
        session_id="zip-session",
        repository_path=workspace_path,
        source="zip_file",
        workspace=workspace,
    )

    service.remove_session("zip-session")

    assert not workspace_path.exists()


def test_clear_removes_all_sessions(tmp_path):
    """Clear should remove all active sessions."""

    service = SessionService()

    service.create_session(
        session_id="one",
        repository_path=tmp_path,
        source="local_path",
    )

    service.create_session(
        session_id="two",
        repository_path=tmp_path,
        source="local_path",
    )

    service.clear()

    assert service.get_session("one") is None
    assert service.get_session("two") is None


def test_list_sessions(tmp_path):
    """list_sessions should return all active sessions."""

    service = SessionService()

    assert service.list_sessions() == []

    s1 = service.create_session(
        session_id="one",
        repository_path=tmp_path,
        source="local_path",
    )
    s2 = service.create_session(
        session_id="two",
        repository_path=tmp_path,
        source="local_path",
    )

    assert service.list_sessions() == [s1, s2]


def test_set_rag_service(tmp_path):
    """Attaching a RAG service to a session should update it."""

    service = SessionService()

    service.create_session(
        session_id="test",
        repository_path=tmp_path,
        source="local_path",
    )

    mock_rag = object()
    service.set_rag_service("test", mock_rag)

    assert service.get_session("test").rag_service is mock_rag


def test_set_rag_service_unknown_session_raises():
    """Attaching a RAG service to unknown session should raise ValueError."""

    service = SessionService()

    with pytest.raises(ValueError, match="Session not found"):
        service.set_rag_service("unknown", object())
