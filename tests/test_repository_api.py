from io import BytesIO
from zipfile import ZipFile

from fastapi.testclient import TestClient

from main import app


client = TestClient(app)


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

    return buffer.getvalue()


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


def test_upload_local_repository(tmp_path):
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


def test_upload_zip_repository():
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
