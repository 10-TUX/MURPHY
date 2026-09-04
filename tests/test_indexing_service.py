from langchain_core.embeddings import Embeddings

from app.models.parsed_file import ParsedFile
from app.services.chunking_service import ChunkingService
from app.services.indexing_service import IndexingService
from app.services.vector_store_service import VectorStoreService


class FakeEmbeddings(Embeddings):
    """Deterministic embeddings for testing."""

    def embed_documents(
        self,
        texts: list[str],
    ) -> list[list[float]]:
        return [[float(len(text)), 1.0, 0.0] for text in texts]

    def embed_query(
        self,
        text: str,
    ) -> list[float]:
        return [float(len(text)), 1.0, 0.0]


def test_chunk_files():
    """Parsed files should be converted into documents."""

    parsed_file = ParsedFile(
        file_path="auth.py",
        language="python",
        content="def login():\n    return True",
    )

    indexing_service = IndexingService(
        chunking_service=ChunkingService(
            chunk_size=100,
            chunk_overlap=10,
        ),
        vector_store_service=VectorStoreService(
            embeddings=FakeEmbeddings(),
        ),
    )

    documents = indexing_service.chunk_files([parsed_file])

    assert documents
    assert documents[0].metadata["source"] == "auth.py"
    assert documents[0].metadata["language"] == "python"


def test_index_creates_faiss_store():
    """Indexing parsed files should create a FAISS store."""

    parsed_file = ParsedFile(
        file_path="auth.py",
        language="python",
        content="def login():\n    return True",
    )

    indexing_service = IndexingService(
        vector_store_service=VectorStoreService(
            embeddings=FakeEmbeddings(),
        ),
    )

    vectorstore = indexing_service.index([parsed_file])

    assert vectorstore is not None
    assert indexing_service.vector_store_service.vectorstore is vectorstore


def test_empty_parsed_files_raise_error():
    """Indexing an empty list should fail."""

    indexing_service = IndexingService(
        vector_store_service=VectorStoreService(
            embeddings=FakeEmbeddings(),
        ),
    )

    try:
        indexing_service.index([])
        assert False
    except ValueError as exc:
        assert "empty parsed files" in str(exc)
