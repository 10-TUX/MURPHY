"""MURPHY - Indexing Service

Coordinates parsing output, chunking, and vector store creation.
"""

from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

from app.models.parsed_file import ParsedFile
from app.services.chunking_service import ChunkingService
from app.services.vector_store_service import VectorStoreService


class IndexingService:
    """Service responsible for indexing parsed source files."""

    def __init__(
        self,
        chunking_service: ChunkingService | None = None,
        vector_store_service: VectorStoreService | None = None,
    ) -> None:
        """Initialize the indexing service."""

        self.chunking_service = (
            chunking_service if chunking_service is not None else ChunkingService()
        )

        self.vector_store_service = (
            vector_store_service
            if vector_store_service is not None
            else VectorStoreService()
        )

    def chunk_files(
        self,
        parsed_files: list[ParsedFile],
    ) -> list[Document]:
        """Chunk all parsed files into LangChain documents."""

        documents: list[Document] = []

        for parsed_file in parsed_files:
            documents.extend(self.chunking_service.chunk(parsed_file))

        return documents

    def index(
        self,
        parsed_files: list[ParsedFile],
    ) -> FAISS:
        """Create a FAISS index from parsed files."""

        if not parsed_files:
            raise ValueError("Cannot create index from empty parsed files.")

        documents = self.chunk_files(parsed_files)

        if not documents:
            raise ValueError("No documents were produced from parsed files.")

        return self.vector_store_service.create(documents)
