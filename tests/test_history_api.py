from pathlib import Path

from fastapi.testclient import TestClient
from langchain_core.messages import AIMessage, HumanMessage

from main import app
from app.services.session_service import session_service


client = TestClient(app)


def create_session():
    return session_service.create_session(
        session_id="test-session",
        repository_path=Path(".").resolve(),
        source="local_path",
    )


def teardown_sessions():
    session_service.clear()


def test_history_requires_valid_session():
    response = client.get("/api/history?session_id=missing-session")

    assert response.status_code == 404
    assert response.json()["detail"] == "Session not found."


def test_history_returns_empty_when_rag_not_initialized():
    create_session()

    response = client.get("/api/history?session_id=test-session")

    assert response.status_code == 200
    assert response.json() == {"messages": []}

    teardown_sessions()


def test_history_returns_conversation_messages():
    session = create_session()

    class FakeRAGService:
        chat_history = [
            HumanMessage(content="What does this project do?"),
            AIMessage(content="This project is an AI codebase assistant."),
        ]

    session.rag_service = FakeRAGService()

    response = client.get("/api/history?session_id=test-session")

    assert response.status_code == 200

    assert response.json() == {
        "messages": [
            {
                "role": "user",
                "content": "What does this project do?",
                "timestamp": None,
            },
            {
                "role": "assistant",
                "content": "This project is an AI codebase assistant.",
                "timestamp": None,
            },
        ]
    }

    teardown_sessions()
