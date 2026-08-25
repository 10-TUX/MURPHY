from pathlib import Path
import pytest
from datetime import datetime
from zipfile import ZipFile
from app.services.repository_service import (
    extract_repository,
    discover_files,
    collect_file_metadata,
    read_file_content,
)


def test_discover_files_filters_unsupported_files(tmp_path: Path):

    (tmp_path / "main.py").write_text("print('hello')")
    (tmp_path / "README.md").write_text("# MURPHY")
    (tmp_path / "image.png").write_bytes(b"fake image")
    (tmp_path / "program.exe").write_bytes(b"fake exe")

    files = discover_files(tmp_path)
    filenames = {file.name for file in files}

    assert "main.py" in filenames
    assert "README.md" in filenames
    assert "image.png" not in filenames
    assert "program.exe" not in filenames


def test_discover_files_is_recursive(tmp_path: Path):
    """Files inside nested directories should be discovered"""
    source_dir = tmp_path / "src" / "utils"
    source_dir.mkdir(parents=True)
    test_file = source_dir / "helper.py"
    test_file.write_text("def hi(): pass")

    files = discover_files(tmp_path)
    assert test_file.resolve() in files


def test_discover_files_ignores_unwanted_directories(tmp_path: Path):
    """Ignores __pycache__, .git, node_modules, .venv"""
    unwanted_dirs = [
        "__pycache__",
        ".git",
        "node_modules",
        ".venv",
        "dist",
        "build",
        ".vscode",
        ".idea",
        ".env",
    ]
    for dirname in unwanted_dirs:
        folder = tmp_path / dirname
        folder.mkdir()
        (folder / "hidden.py").write_text("should not be discovered")

    files = discover_files(tmp_path)
    filenames = {file.name for file in files}

    assert "hidden.py" not in filenames


def test_discover_files_file_Instead_of_directory(tmp_path: Path):
    """If a file and folder have the same name, directory should take precedence"""
    file_path = tmp_path / "repository.py"
    file_path.write_text("test")
    with pytest.raises(ValueError):
        discover_files(file_path)


def test_collect_file_metadata(tmp_path: Path):
    """
    Tests if the metadata generated matches the actual file properties.
    """
    # Create a dummy file with specific characteristics
    test_file = tmp_path / "main.py"
    content = "print('hello MURPHY')"
    test_file.write_text(content, encoding="utf-8")

    # Collect metadata
    metadata = collect_file_metadata(tmp_path)

    # Check if exactly one file's metadata was collected
    assert len(metadata) == 1
    file_metadata = metadata[0]

    # Verify the metadata fields
    assert file_metadata.filename == "main.py"
    assert file_metadata.relative_path == "main.py"
    assert file_metadata.absolute_path == str(test_file.resolve())
    assert file_metadata.extension == ".py"
    assert file_metadata.size_bytes == len(content.encode("utf-8"))

    # Verify last_modified is a datetime object
    assert isinstance(file_metadata.last_modified, datetime)


def test_collect_file_metadata_handles_unsupported_files(tmp_path: Path):
    """
    Tests that unsupported files are ignored when collecting metadata.
    """
    # Create a supported file
    (tmp_path / "main.py").write_text("def main(): pass")

    # Create an unsupported file
    (tmp_path / "image.png").write_bytes(b"fake image data")

    # Create a directory with unsupported file
    (tmp_path / "node_modules").mkdir()
    (tmp_path / "node_modules" / "large_library.js").write_text("library code")

    metadata = collect_file_metadata(tmp_path)

    # Should only find the supported file
    assert len(metadata) == 1
    assert metadata[0].filename == "main.py"
    assert metadata[0].extension == ".py"


def test_read_file_content(tmp_path: Path):
    """UTF-8 text files should be read correctly"""
    test_file = tmp_path / "hello.py"
    content = "print('Hello MURPHY')"
    test_file.write_text(content, encoding="utf-8")

    result = read_file_content(test_file)
    assert result == content


def test_read_file_content_fallback_utf8(tmp_path: Path):
    """UTF-8 files with replacement characters should be handled gracefully."""
    test_file = tmp_path / "bad.txt"
    # Raw bytes containing invalid UTF-8 sequences
    content = b"Hello \x80\xff World"
    test_file.write_bytes(content)

    # Should not crash and return a readable string
    result = read_file_content(test_file)
    assert "Hello" in result
    assert "World" in result
    assert "\x80" not in result  # Replaced


def test_read_file_content_non_existent(tmp_path: Path):
    """Reading a non-existent file should raise FileNotFoundError."""
    non_existent_file = tmp_path / "missing.py"

    with pytest.raises(FileNotFoundError):
        read_file_content(non_existent_file)


def test_read_file_content_directory(tmp_path: Path):
    """Reading a directory should raise an error."""
    with pytest.raises(FileNotFoundError):
        read_file_content(tmp_path)


def test_extract_repository(tmp_path: Path):
    """A valid ZIP should be extracted correctly."""

    zip_path = tmp_path / "repository.zip"
    extraction_path = tmp_path / "extracted"

    with ZipFile(zip_path, "w") as zip_file:
        zip_file.writestr("src/main.py", "print('Hello MURPHY')")
        zip_file.writestr("README.md", "# MURPHY")

    result = extract_repository(
        zip_path,
        extraction_path,
    )

    assert result == extraction_path.resolve()
    assert (extraction_path / "src" / "main.py").exists()
    assert (extraction_path / "README.md").exists()

    assert (extraction_path / "src" / "main.py").read_text() == "print('Hello MURPHY')"


def test_extract_repository_missing_zip(tmp_path: Path):
    """A missing ZIP should raise FileNotFoundError."""

    zip_path = tmp_path / "missing.zip"
    destination = tmp_path / "extracted"

    with pytest.raises(FileNotFoundError):
        extract_repository(zip_path, destination)


def test_extract_repository_invalid_extension(tmp_path: Path):
    """A non-ZIP file should raise ValueError."""

    file_path = tmp_path / "repository.txt"
    file_path.write_text("not a zip file")

    destination = tmp_path / "extracted"

    with pytest.raises(ValueError):
        extract_repository(file_path, destination)


def test_extract_repository_invalid_zip(tmp_path: Path):
    """A corrupted ZIP should raise ValueError."""

    zip_path = tmp_path / "corrupted.zip"
    zip_path.write_bytes(b"This is not a valid ZIP file")

    destination = tmp_path / "extracted"

    with pytest.raises(ValueError, match="Invalid zip file"):
        extract_repository(zip_path, destination)


def test_extract_repository_blocks_path_traversal(tmp_path: Path):
    """ZIP entries must not be allowed to escape the destination."""

    zip_path = tmp_path / "malicious.zip"
    destination = tmp_path / "extracted"

    with ZipFile(zip_path, "w") as zip_file:
        zip_file.writestr("../malicious.py", "print('malicious')")

    with pytest.raises(
        ValueError,
        match="Unsafe ZIP entry detected",
    ):
        extract_repository(zip_path, destination)

    assert not (tmp_path / "malicious.py").exists()
