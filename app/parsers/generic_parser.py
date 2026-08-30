from app.models.parsed_file import ParsedFile
from app.parsers.base import Parser
from app.utils.language_detector import detect_language


class GenericParser(Parser):
    """Parser for source files without language-specific AST parsing."""

    def parse(self, source_code: str, file_path: str) -> ParsedFile:
        """Create a structured representation of a generic text file."""

        return ParsedFile(
            file_path=file_path,
            language=detect_language(file_path),
            content=source_code,
        )
