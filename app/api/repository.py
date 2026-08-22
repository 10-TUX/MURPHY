from pathlib import Path
from tempfile import NamedTemporaryFile, mkdtemp
from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from app.services.repository_service import extract_repository


router = APIRouter(
    prefix="/api/repo",
    tags=["Repository"],
    responses={404: {"description": "Repository not found"}},
)


@router.post("/upload", status_code=201)
async def upload_repo(
    file: UploadFile | None = File(default=None),
    repository_path: str | None = Form(default=None),
):
    """
    Upload a zip file or provide a local path to a repository.
    """

    if not file and not repository_path:
        raise HTTPException(
            status_code=400,
            detail="Either a file or a repository path must be provided.",
        )

    if repository_path is not None:
        path = Path(repository_path).resolve()
        if not path.exists():
            raise HTTPException(
                status_code=400,
                detail=f"Repository path {repository_path} does not exist.",
            )

        if not path.is_dir():
            raise HTTPException(
                status_code=400,
                detail=f"Repository path {repository_path} is not a directory.",
            )
        return {
            "status": "success",
            "source": "local_path",
            "repository_path": str(path),
            "message": "Repository loaded successfully.",
        }

    # Zip upload
    if file is not None:
        if not file.filename:
            raise HTTPException(status_code=400, detail="No filename provided.")

        if not file.filename.lower().endswith(".zip"):
            raise HTTPException(status_code=400, detail="File must be a zip file.")

        with NamedTemporaryFile(suffix=".zip", delete=False) as temp_file:
            while chunk := await file.read(1024 * 1024):
                temp_file.write(chunk)
            temp_path = Path(temp_file.name)
        extraction_path = Path(mkdtemp(prefix="murphy-repo_"))

        try:
            repository_path = extract_repository(
                zip_path=temp_path, destination=extraction_path
            )
        except (FileNotFoundError, ValueError) as exc:
            raise HTTPException(
                status_code=400,
                detail=f"Failed to extract zip file: {str(exc)}",
            ) from exc

        return {
            "status": "success",
            "source": "zip_file",
            "filename": file.filename,
            "repository_path": str(repository_path),
            "message": "Repository loaded successfully.",
        }
