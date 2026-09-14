from pathlib import Path

from fastapi.testclient import TestClient

from main import app
from app.services.session_service import session_service


client = TestClient(app)


def create_test_repository(tmp_path: Path) -> Path:
    """Create a small repository for testing."""

    repository = tmp_path / "test_repo"
    repository.mkdir()

    (repository / "main.py").write_text(
        "print('hello')\n",
        encoding="utf-8",
    )

    (repository / "README.md").write_text(
        "# Test Repository\n",
        encoding="utf-8",
    )

    return repository


def teardown_sessions():
    """Clean up test sessions."""

    session_service.clear()


def test_files_requires_valid_session():
    response = client.get("/api/files?session_id=missing-session")

    assert response.status_code == 404
    assert response.json()["detail"] == "Session not found."


def test_files_returns_repository_files(tmp_path):
    repository = create_test_repository(tmp_path)

    session_service.create_session(
        session_id="test-session",
        repository_path=repository,
        source="local_path",
    )

    response = client.get("/api/files?session_id=test-session")

    assert response.status_code == 200

    data = response.json()

    assert "files" in data
    assert len(data["files"]) == 2

    filenames = {file["filename"] for file in data["files"]}

    assert filenames == {
        "main.py",
        "README.md",
    }

    teardown_sessions()
