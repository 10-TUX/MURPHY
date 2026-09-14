from pathlib import Path
from fastapi.testclient import TestClient

from main import app
from app.api.query import set_rag_service
from app.services.session_service import session_service


client = TestClient(app)


def setup_function():
    session_service.clear()


def teardown_function():
    session_service.clear()


def test_status_when_no_session():
    response = client.get("/api/status")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "not_ready"
    assert data["message"] == "RAG service is not initialized."


def test_status_when_rag_is_not_initialized():
    session_service.create_session(
        session_id="test-session",
        repository_path=Path(".").resolve(),
        source="local_path",
    )

    response = client.get("/api/status?session_id=test-session")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "not_ready"
    assert data["message"] == "RAG service is not initialized for this session."


def test_status_when_rag_is_initialized():
    session_service.create_session(
        session_id="test-session",
        repository_path=Path(".").resolve(),
        source="local_path",
    )
    set_rag_service("test-session", object())

    response = client.get("/api/status?session_id=test-session")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "ready"
    assert data["message"] == "MURPHY RAG service is ready."


def test_status_general_when_any_rag_is_initialized():
    session_service.create_session(
        session_id="test-session",
        repository_path=Path(".").resolve(),
        source="local_path",
    )
    set_rag_service("test-session", object())

    response = client.get("/api/status")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "ready"
    assert data["message"] == "MURPHY RAG service is ready."


def test_status_unknown_session_returns_404():
    response = client.get("/api/status?session_id=unknown-session")

    assert response.status_code == 404
    assert response.json()["detail"] == "Session not found."
