from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from langchain_core.embeddings import FakeEmbeddings
from app.services.vector_store_service import VectorStoreService
from app.services.indexing_service import IndexingService
from app.models.parsed_file import ParsedFile
from app.services.rag_service import RAGService
from app.services.repository_indexing_service import RepositoryIndexingService


@pytest.fixture(autouse=True)
def mock_llm_service():
    """Mock LLMService so creating RAGService does not require Google API credentials."""
    with patch("app.services.rag_service.LLMService") as mock:
        mock.return_value.get_llm.return_value = MagicMock()
        yield mock


def create_test_repository(tmp_path: Path) -> Path:
    """Create a small test repository."""

    repository = tmp_path / "test_repo"
    repository.mkdir()

    (repository / "main.py").write_text(
        "def hello():\n" "    return 'Hello MURPHY'\n",
        encoding="utf-8",
    )

    (repository / "README.md").write_text(
        "# MURPHY\n" "AI codebase assistant.\n",
        encoding="utf-8",
    )

    (repository / "image.png").write_bytes(b"not a supported source file")

    return repository


def test_parse_file_uses_python_parser(tmp_path):
    repository = create_test_repository(tmp_path)

    service = RepositoryIndexingService()

    parsed_file = service.parse_file(
        repository / "main.py",
        repository,
    )

    assert isinstance(parsed_file, ParsedFile)
    assert parsed_file.file_path == "main.py"
    assert parsed_file.language == "python"


def test_parse_file_uses_generic_parser_for_other_files(tmp_path):
    repository = create_test_repository(tmp_path)

    service = RepositoryIndexingService()

    parsed_file = service.parse_file(
        repository / "README.md",
        repository,
    )

    assert isinstance(parsed_file, ParsedFile)
    assert parsed_file.file_path == "README.md"


def test_parse_repository_parses_supported_files(tmp_path):
    repository = create_test_repository(tmp_path)

    service = RepositoryIndexingService()

    parsed_files = service.parse_repository(repository)

    assert len(parsed_files) == 2

    file_paths = {parsed_file.file_path for parsed_file in parsed_files}

    assert file_paths == {
        "main.py",
        "README.md",
    }


def test_index_repository_delegates_to_indexing_service(tmp_path):
    repository = create_test_repository(tmp_path)

    indexing_service = MagicMock()
    indexing_service.index.return_value = "fake-vector-store"

    service = RepositoryIndexingService(
        indexing_service=indexing_service,
    )

    result = service.index_repository(repository)

    assert result == "fake-vector-store"

    indexing_service.index.assert_called_once()

    parsed_files = indexing_service.index.call_args.args[0]

    assert len(parsed_files) == 2
    assert all(isinstance(parsed_file, ParsedFile) for parsed_file in parsed_files)


def test_index_repository_rejects_empty_repository(tmp_path):
    repository = tmp_path / "empty_repo"
    repository.mkdir()

    service = RepositoryIndexingService()

    try:
        service.index_repository(repository)
        assert False, "Expected ValueError"
    except ValueError as exc:
        assert str(exc) == "No supported files found in repository."


def test_build_rag_service_creates_rag_service(tmp_path):
    repository = create_test_repository(tmp_path)

    indexing_service = MagicMock()

    vector_store_service = MagicMock()
    indexing_service.vector_store_service = vector_store_service
    indexing_service.index.return_value = MagicMock()

    service = RepositoryIndexingService(
        indexing_service=indexing_service,
    )

    rag_service = service.build_rag_service(repository)

    assert isinstance(rag_service, RAGService)

    assert rag_service.vector_store is vector_store_service

    indexing_service.index.assert_called_once()

    parsed_files = indexing_service.index.call_args.args[0]

    assert len(parsed_files) == 2
    assert all(isinstance(parsed_file, ParsedFile) for parsed_file in parsed_files)


def test_index_repository_builds_real_vector_store(tmp_path):
    """Repository indexing should build a real FAISS vector store."""

    repository = create_test_repository(tmp_path)

    embeddings = FakeEmbeddings(size=32)

    vector_store_service = VectorStoreService(
        embeddings=embeddings,
    )

    indexing_service = IndexingService(
        vector_store_service=vector_store_service,
    )

    service = RepositoryIndexingService(
        indexing_service=indexing_service,
    )

    vector_store = service.index_repository(repository)

    assert vector_store is not None
    assert vector_store_service.vectorstore is vector_store

    results = vector_store_service.similarity_search(
        "Hello MURPHY",
        k=2,
    )

    assert len(results) == 2
