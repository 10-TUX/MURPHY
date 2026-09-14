from io import BytesIO
from pathlib import Path
from zipfile import ZipFile
from unittest.mock import MagicMock, patch
from app.services.rag_service import RAGResult
from app.services.repository_indexing_service import RepositoryIndexingService
from langchain_core.documents import Document
import pytest
from fastapi.testclient import TestClient

from main import app
from app.services.session_service import session_service


client = TestClient(app)


@pytest.fixture(autouse=True)
def cleanup_session():
    """Clean repository sessions after each API test."""
    yield
    session_service.clear()


@pytest.fixture
def mock_indexing_service():
    """Provide a fake repository indexing service."""
    with patch("app.api.repository.RepositoryIndexingService") as mock_class:
        mock_service = MagicMock()
        mock_service.build_rag_service.return_value = MagicMock()
        mock_class.return_value = mock_service
        yield mock_service


def create_test_zip() -> bytes:
    """Create an in-memory ZIP repository for testing."""

    buffer = BytesIO()

    with ZipFile(buffer, "w") as zip_file:
        zip_file.writestr(
            "main.py",
            "def hello():\n    return 'Hello MURPHY'\n",
        )
        zip_file.writestr(
            "README.md",
            "# MURPHY\n",
        )

    buffer.seek(0)
    return buffer.read()


def test_upload_requires_file_or_repository_path():
    """Upload should reject requests without a file or path."""

    response = client.post("/api/repo/upload")

    assert response.status_code == 400
    assert response.json()["detail"] == (
        "Either a file or a repository path must be provided."
    )


def test_upload_rejects_invalid_repository_path(tmp_path):
    """Upload should reject a repository path that does not exist."""

    missing_path = tmp_path / "does_not_exist"

    response = client.post(
        "/api/repo/upload",
        data={"repository_path": str(missing_path)},
    )

    assert response.status_code == 400
    assert "does not exist" in response.json()["detail"]


def test_upload_rejects_repository_file(tmp_path):
    """Upload should reject a path that points to a file."""

    file_path = tmp_path / "not_a_repository.txt"
    file_path.write_text("not a repository")

    response = client.post(
        "/api/repo/upload",
        data={"repository_path": str(file_path)},
    )

    assert response.status_code == 400
    assert "not a directory" in response.json()["detail"]


def test_upload_local_repository(tmp_path, mock_indexing_service):
    """Upload should accept a valid local repository path."""

    (tmp_path / "main.py").write_text(
        "print('Hello MURPHY')",
        encoding="utf-8",
    )

    response = client.post(
        "/api/repo/upload",
        data={"repository_path": str(tmp_path)},
    )

    assert response.status_code == 201

    data = response.json()

    assert data["status"] == "success"
    assert data["source"] == "local_path"
    assert data["repository_path"] == str(tmp_path.resolve())
    assert data["message"] == "Repository loaded successfully."


def test_upload_zip_repository(mock_indexing_service):
    """Upload should accept a valid ZIP repository."""

    zip_bytes = create_test_zip()

    response = client.post(
        "/api/repo/upload",
        files={
            "file": (
                "repository.zip",
                zip_bytes,
                "application/zip",
            )
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["status"] == "success"
    assert data["source"] == "zip_file"
    assert data["filename"] == "repository.zip"
    assert data["file_count"] == 2
    assert data["message"] == "Repository loaded successfully."

    assert len(data["files"]) == 2

    filenames = {item["filename"] for item in data["files"]}

    assert "main.py" in filenames
    assert "README.md" in filenames


def test_upload_rejects_non_zip_file():
    """Upload should reject files that are not ZIP archives."""

    response = client.post(
        "/api/repo/upload",
        files={
            "file": (
                "repository.txt",
                b"not a zip",
                "text/plain",
            )
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "File must be a zip file."


def test_upload_local_repository_creates_session(tmp_path, mock_indexing_service):
    """A local repository upload should create an active session."""

    response = client.post(
        "/api/repo/upload",
        data={"repository_path": str(tmp_path)},
    )

    assert response.status_code == 201

    data = response.json()

    session_id = data["session_id"]

    session = session_service.get_session(session_id)

    assert session is not None
    assert session.session_id == session_id
    assert session.repository_path == tmp_path.resolve()
    assert session.source == "local_path"
    assert session.rag_service is not None

    mock_indexing_service.build_rag_service.assert_called_once_with(tmp_path.resolve())


def test_upload_zip_repository_keeps_workspace_alive(mock_indexing_service):
    """A ZIP repository should remain available after the upload request."""

    zip_bytes = create_test_zip()

    response = client.post(
        "/api/repo/upload",
        files={
            "file": (
                "repository.zip",
                zip_bytes,
                "application/zip",
            )
        },
    )
    assert response.status_code == 201

    data = response.json()

    session_id = data["session_id"]
    session = session_service.get_session(session_id)

    assert session is not None
    assert session.source == "zip_file"
    assert session.rag_service is not None
    assert session.repository_path.exists()
    assert session.repository_path.is_dir()
    assert (session.repository_path / "main.py").exists()
    assert session.rag_service is not None

    mock_indexing_service.build_rag_service.assert_called_once_with(
        session.repository_path
    )


def test_upload_then_query_uses_created_session():
    """A repository upload should create a session usable by query."""

    with patch("app.api.repository.RepositoryIndexingService") as mock_class:
        mock_indexing_service = MagicMock()

        rag_service = MagicMock()

        rag_service.invoke.return_value = RAGResult(
            answer="The repository contains a Python application.",
            documents=[
                Document(
                    page_content="print('Hello MURPHY')",
                    metadata={
                        "source": "main.py",
                        "start_line": 1,
                        "end_line": 1,
                    },
                )
            ],
        )

        mock_indexing_service.build_rag_service.return_value = rag_service
        mock_class.return_value = mock_indexing_service

        repository = Path(".").resolve()

        upload_response = client.post(
            "/api/repo/upload",
            data={
                "repository_path": str(repository),
            },
        )

    assert upload_response.status_code == 201

    session_id = upload_response.json()["session_id"]

    session = session_service.get_session(session_id)

    assert session is not None
    assert session.rag_service is rag_service

    query_response = client.post(
        f"/api/query?session_id={session_id}",
        json={"question": "What does this repository contain?"},
    )

    assert query_response.status_code == 200

    data = query_response.json()

    assert data["answer"] == ("The repository contains a Python application.")

    assert data["sources"] == [
        {
            "source": "main.py",
            "start_line": 1,
            "end_line": 1,
        }
    ]

    rag_service.invoke.assert_called_once_with("What does this repository contain?")
