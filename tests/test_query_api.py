from unittest.mock import MagicMock

from fastapi.testclient import TestClient

from main import app
from pathlib import Path
from app.api.query import set_rag_service
from app.services.rag_service import RAGResult
from app.services.session_service import session_service
from langchain_core.documents import Document


client = TestClient(app)


def create_session():
    """Create a test session."""

    return session_service.create_session(
        session_id="test-session",
        repository_path=Path(".").resolve(),
        source="local_path",
    )


def teardown_sessions():
    """Clean up test sessions."""

    session_service.clear()


def test_query_requires_valid_session():
    """Query should reject an unknown session."""

    response = client.post(
        "/api/query?session_id=missing-session",
        json={"question": "What does this project do?"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Session not found."


def test_query_requires_initialized_rag_service():
    """Query should reject a session without RAG."""

    create_session()

    response = client.post(
        "/api/query?session_id=test-session",
        json={"question": "What does this project do?"},
    )

    assert response.status_code == 503
    assert response.json()["detail"] == (
        "RAG service is not initialized for this session."
    )

    teardown_sessions()


def test_query_returns_answer_and_sources():
    """Query should return the answer and source references."""

    create_session()

    rag_service = MagicMock()

    documents = [
        Document(
            page_content="def hello(): pass",
            metadata={
                "source": "main.py",
                "start_line": 1,
                "end_line": 1,
            },
        ),
        Document(
            page_content="class Example: pass",
            metadata={
                "source": "app/example.py",
                "start_line": 5,
                "end_line": 5,
            },
        ),
    ]

    rag_service.invoke.return_value = RAGResult(
        answer="The project contains a hello function and an Example class.",
        documents=documents,
    )

    set_rag_service(
        "test-session",
        rag_service,
    )

    response = client.post(
        "/api/query?session_id=test-session",
        json={"question": "What does the project contain?"},
    )

    assert response.status_code == 200

    data = response.json()

    assert data["answer"] == (
        "The project contains a hello function and an Example class."
    )

    assert len(data["sources"]) == 2

    assert data["sources"][0] == {
        "source": "main.py",
        "start_line": 1,
        "end_line": 1,
    }

    assert data["sources"][1] == {
        "source": "app/example.py",
        "start_line": 5,
        "end_line": 5,
    }

    rag_service.invoke.assert_called_once_with("What does the project contain?")

    teardown_sessions()


def test_query_rejects_empty_question():
    """Query should reject an empty question."""

    create_session()

    rag_service = MagicMock()
    set_rag_service("test-session", rag_service)

    response = client.post(
        "/api/query?session_id=test-session",
        json={"question": ""},
    )

    assert response.status_code == 422

    teardown_sessions()


def test_query_handles_rag_value_error():
    """Query should convert RAG validation errors to HTTP 400."""

    create_session()

    rag_service = MagicMock()
    rag_service.invoke.side_effect = ValueError("Question cannot be empty.")

    set_rag_service("test-session", rag_service)

    response = client.post(
        "/api/query?session_id=test-session",
        json={"question": "   "},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Question cannot be empty."

    teardown_sessions()


def test_query_uses_rag_service_attached_to_session():
    session_service.create_session(
        session_id="query-session",
        repository_path=Path(".").resolve(),
        source="local_path",
    )

    rag_service = MagicMock()

    rag_service.invoke.return_value = RAGResult(
        answer="MURPHY is an AI codebase assistant.",
        documents=[
            Document(
                page_content="MURPHY code",
                metadata={
                    "source": "main.py",
                    "start_line": 1,
                    "end_line": 5,
                },
            )
        ],
    )

    session_service.set_rag_service(
        "query-session",
        rag_service,
    )

    response = client.post(
        "/api/query?session_id=query-session",
        json={"question": "What is MURPHY?"},
    )

    assert response.status_code == 200

    data = response.json()

    assert data["answer"] == ("MURPHY is an AI codebase assistant.")

    assert data["sources"] == [
        {
            "source": "main.py",
            "start_line": 1,
            "end_line": 5,
        }
    ]

    rag_service.invoke.assert_called_once_with("What is MURPHY?")
