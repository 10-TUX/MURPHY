from pathlib import Path
from zipfile import ZipFile, BadZipFile
from datetime import datetime
from app.models.file_metadata import FileMetadata

# ── Supported_Extensions ─────────────────────────────

SUPPORTED_EXTENSIONS = {
    ".py",
    ".java",
    ".cpp",
    ".js",
    ".ts",
    ".json",
    ".yaml",
    ".yml",
    ".html",
    ".css",
    ".v",
    ".sv",
    ".md",
    ".txt",
}


# ── Main repository service ─────────────────────────────


def extract_repository(zip_path: str | Path, destination: str | Path) -> Path:
    """
    Extract a zip file to a specified directory.
    """
    zip_path = Path(zip_path).resolve()
    destination = Path(destination).resolve()

    if not zip_path.is_file():
        raise FileNotFoundError(f"Zip file not found: {zip_path}")
    if zip_path.suffix.lower() != ".zip":
        raise ValueError(f"File is not a zip file: {zip_path}")

    # Create destination directory if it doesn't exist
    destination.mkdir(parents=True, exist_ok=True)

    try:
        with ZipFile(zip_path, "r") as zip_file:
            for member in zip_file.infolist():
                member_path = (destination / member.filename).resolve()

                # Skip if it tries to break out of the directory
                if not member_path.is_relative_to(destination):
                    raise ValueError(f"Unsafe ZIP entry detected: {member.filename}")
            zip_file.extractall(destination)
    except BadZipFile as exc:
        raise ValueError(f"Invalid zip file") from exc

    return destination


def discover_files(repository_path: str | Path) -> list[Path]:
    """
    Discover all files in a directory, excluding unwanted files.
    Returns:
            a list containing the absolute paths of all discovered files.
    """
    repository_path = Path(repository_path).resolve()
    if not repository_path.exists():
        raise FileNotFoundError(f"Repository path not found: {repository_path}")
    if not repository_path.is_dir():
        raise ValueError(f"Repository path is not a directory: {repository_path}")

    # Set for ignored directories
    ignored_directories = {
        "__pycache__",
        ".git",
        "node_modules",
        ".venv",
        "dist",
        "build",
        ".vscode",
        ".idea",
        ".env",
    }
    discovered_files = []

    # List all files in the repository
    for path in repository_path.rglob("*"):
        if not path.is_file():
            continue
        if any(part in ignored_directories for part in path.parts):
            continue
        if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            continue
        discovered_files.append(path)
    return discovered_files


def collect_file_metadata(
    repository_path: str | Path,
) -> list[FileMetadata]:
    """Discover supported files and collect metadata for each file"""

    repository_path = Path(repository_path).resolve()

    files = discover_files(repository_path)

    metadata = []

    for file_path in files:
        stat = file_path.stat()
        metadata.append(
            FileMetadata(
                filename=file_path.name,
                relative_path=str(file_path.relative_to(repository_path)),
                absolute_path=str(file_path),
                extension=file_path.suffix.lower(),
                size_bytes=stat.st_size,
                last_modified=datetime.fromtimestamp(stat.st_mtime),
            )
        )

    return metadata


def read_file_content(file_path: str | Path) -> str:
    """
    Read the content of a file.
    UTF-8 is attempted first. If decoding fails, fall back to UTF-8 with replacement characters
    """
    file_path = Path(file_path).resolve()

    if not file_path.is_file():
        raise FileNotFoundError(f"File not found: {file_path}")
    try:
        return file_path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return file_path.read_text(encoding="utf-8", errors="replace")
