"""MURPHY - Repository Indexing Service.

Coordinates repository parsing, vector indexing, and RAG creation.
"""

from pathlib import Path

from app.models.parsed_file import ParsedFile
from app.parsers.generic_parser import GenericParser
from app.parsers.python_parser import PythonParser
from app.services.indexing_service import IndexingService
from app.services.rag_service import RAGService
from app.services.repository_service import (
    discover_files,
    read_file_content,
)
from app.services.vector_store_service import VectorStoreService


class RepositoryIndexingService:
    """Build a searchable RAG pipeline from a repository."""

    def __init__(
        self,
        indexing_service: IndexingService | None = None,
        llm: object | None = None,
    ) -> None:
        self._indexing_service = indexing_service
        self.llm = llm
        self.python_parser = PythonParser()
        self.generic_parser = GenericParser()

    @property
    def indexing_service(self) -> IndexingService:
        """Return the indexing service, creating it on demand."""
        if self._indexing_service is None:
            self._indexing_service = IndexingService()
        return self._indexing_service

    @indexing_service.setter
    def indexing_service(self, value: IndexingService) -> None:
        self._indexing_service = value

    def parse_file(
        self,
        file_path: Path,
        repository_path: Path,
    ) -> ParsedFile:
        """Parse a single repository file."""

        source_code = read_file_content(file_path)

        relative_path = str(file_path.relative_to(repository_path))

        if file_path.suffix.lower() == ".py":
            parser = self.python_parser
        else:
            parser = self.generic_parser

        return parser.parse(
            source_code=source_code,
            file_path=relative_path,
        )

    def parse_repository(
        self,
        repository_path: str | Path,
    ) -> list[ParsedFile]:
        """Discover and parse all supported repository files."""

        repository_path = Path(repository_path).resolve()

        files = discover_files(repository_path)

        parsed_files = []

        for file_path in files:
            parsed_files.append(
                self.parse_file(
                    file_path=file_path,
                    repository_path=repository_path,
                )
            )

        return parsed_files

    def index_repository(
        self,
        repository_path: str | Path,
    ):
        """Parse a repository and build its vector index."""

        parsed_files = self.parse_repository(repository_path)

        if not parsed_files:
            raise ValueError("No supported files found in repository.")

        return self.indexing_service.index(parsed_files)

    def build_rag_service(
        self,
        repository_path: str | Path,
        llm: object | None = None,
    ) -> RAGService:
        """Build a RAG service for a repository."""

        vector_store = self.index_repository(repository_path)

        vector_store_service = self.indexing_service.vector_store_service

        return RAGService(
            vector_store=vector_store_service,
            llm=llm if llm is not None else self.llm,
        )
