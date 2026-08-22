from pathlib import Path
from zipfile import ZipFile, BadZipFile

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
