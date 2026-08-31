from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter, Language
from app.models.parsed_file import ParsedFile


class ChunkingService:
    """Service responsible for chunking parsed files into smaller chunks."""

    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200) -> None:
        """Initialize the ChunkingService."""
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def _create_splitter(self, language: str) -> RecursiveCharacterTextSplitter:
        """Create a language-aware splitter"""
        language_map = {
            "python": Language.PYTHON,
            "js": Language.JS,
            "ts": Language.TS,
            "java": Language.JAVA,
            "go": Language.GO,
            "c": Language.C,
            "cpp": Language.CPP,
            "csharp": Language.CSHARP,
            "php": Language.PHP,
            "ruby": Language.RUBY,
            "rust": Language.RUST,
            "swift": Language.SWIFT,
            "kotlin": Language.KOTLIN,
            "scala": Language.SCALA,
            "perl": Language.PERL,
            "lua": Language.LUA,
            "html": Language.HTML,
            "markdown": Language.MARKDOWN,
        }
        splitter_language = language_map.get(language.lower())
        if splitter_language is not None:
            return RecursiveCharacterTextSplitter.from_language(
                language=splitter_language,
                chunk_size=self.chunk_size,
                chunk_overlap=self.chunk_overlap,
            )
        return RecursiveCharacterTextSplitter(
            separators=["\n\n", "\n", " ", ""],
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=len,
            is_separator_regex=False,
            keep_separator=True,
        )

    def split_text(self, content: str) -> list[str]:
        """split generic source code into smaller chunks."""
        if not content:
            return []

        splitter = self._create_splitter("generic")
        return splitter.split_text(content)

    def chunk(self, parsed_file: ParsedFile) -> list[Document]:
        """Split a parsed file into smaller chunks using language aware separators."""
        if not parsed_file:
            return []

        splitter = self._create_splitter(parsed_file.language)
        chunks = splitter.split_text(parsed_file.content)

        documents = []

        for chunk in chunks:
            documents.append(
                Document(
                    page_content=chunk,
                    metadata={
                        "source": parsed_file.file_path,
                        "language": parsed_file.language,
                    },
                )
            )
        return documents
