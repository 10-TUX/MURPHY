from fastapi.testclient import TestClient

from main import app
from app.api.query import set_rag_service


client = TestClient(app)


def test_status_when_rag_is_not_initialized():
    set_rag_service(None)

    response = client.get("/api/status")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "not_ready"
    assert data["message"] == "RAG service is not initialized."


def test_status_when_rag_is_initialized():
    set_rag_service(object())

    response = client.get("/api/status")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "ready"
    assert data["message"] == "MURPHY RAG service is ready."
