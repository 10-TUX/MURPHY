from unittest.mock import MagicMock

from fastapi.testclient import TestClient

from main import app
from app.api.query import set_rag_service
from app.services.rag_service import RAGResult
from langchain_core.documents import Document


client = TestClient(app)


def test_query_requires_initialized_rag_service():
    set_rag_service(None)

    response = client.post(
        "/api/query",
        json={"question": "What does this project do?"},
    )

    assert response.status_code == 503
    assert response.json()["detail"] == "RAG service is not initialized."


def test_query_returns_answer_and_sources():
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

    set_rag_service(rag_service)

    response = client.post(
        "/api/query",
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


def test_query_rejects_empty_question():
    rag_service = MagicMock()
    set_rag_service(rag_service)

    response = client.post(
        "/api/query",
        json={"question": ""},
    )

    assert response.status_code == 422


def test_query_handles_rag_value_error():
    rag_service = MagicMock()
    rag_service.invoke.side_effect = ValueError("Question cannot be empty.")

    set_rag_service(rag_service)

    response = client.post(
        "/api/query",
        json={"question": "   "},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Question cannot be empty."
