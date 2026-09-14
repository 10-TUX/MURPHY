from pathlib import Path
from tempfile import TemporaryDirectory
from uuid import uuid4

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from app.services.session_service import session_service
from app.services.repository_indexing_service import RepositoryIndexingService

from app.models.api_models import RepositoryUploadResponse
from app.services.repository_service import (
    extract_repository,
    discover_files,
    collect_file_metadata,
)


router = APIRouter(
    prefix="/api/repo",
    tags=["Repository"],
    responses={404: {"description": "Repository not found"}},
)


@router.post("/upload", status_code=201)
async def upload_repo(
    file: UploadFile | None = File(default=None),
    repository_path: str | None = Form(default=None),
) -> RepositoryUploadResponse:
    """
    Upload a zip file or provide a local path to a repository.
    """

    if not file and not repository_path:
        raise HTTPException(
            status_code=400,
            detail="Either a file or a repository path must be provided.",
        )

    # Generate session id
    session_id = str(uuid4())
    indexing_service = RepositoryIndexingService()

    # Local path repository
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

        session_service.create_session(
            session_id=session_id,
            repository_path=path,
            source="local_path",
        )

        rag_service = indexing_service.build_rag_service(path)
        session_service.set_rag_service(
            session_id=session_id,
            rag_service=rag_service,
        )

        return RepositoryUploadResponse(
            status="success",
            source="local_path",
            repository_path=str(path),
            session_id=session_id,
            message="Repository loaded successfully.",
        )

    # Zip upload
    if file is not None:
        if not file.filename:
            raise HTTPException(status_code=400, detail="No filename provided.")

        if not file.filename.lower().endswith(".zip"):
            raise HTTPException(status_code=400, detail="File must be a zip file.")

        workspace = TemporaryDirectory(prefix="murphy_repo_")

        try:
            workspace_path = Path(workspace.name)
            # save the uploaded ZIP inside the temporary workspace.
            temp_path = workspace_path / file.filename

            with temp_path.open("wb") as temp_file:
                while chunk := await file.read(1024 * 1024):
                    temp_file.write(chunk)

                # Extract repository into the same workspace.
            extraction_path = workspace_path / "repository"
            repository_path = extract_repository(
                zip_path=temp_path,
                destination=extraction_path,
            )

            # discover supported files
            discovered_files = discover_files(repository_path)

            # collect file metadata
            file_metadata = collect_file_metadata(repository_path)

            session_service.create_session(
                session_id=session_id,
                repository_path=repository_path,
                source="zip_file",
                workspace=workspace,
            )
            rag_service = indexing_service.build_rag_service(repository_path)
            session_service.set_rag_service(
                session_id=session_id,
                rag_service=rag_service,
            )

            return RepositoryUploadResponse(
                status="success",
                source="zip_file",
                filename=file.filename,
                repository_path=str(repository_path),
                session_id=session_id,
                file_count=len(discovered_files),
                files=[item.model_dump(mode="json") for item in file_metadata],
                message="Repository loaded successfully.",
            )

        except (FileNotFoundError, ValueError) as exc:
            workspace.cleanup()
            raise HTTPException(
                status_code=400,
                detail=f"Failed to extract zip file: {str(exc)}",
            ) from exc
        except Exception:
            workspace.cleanup()
            raise
