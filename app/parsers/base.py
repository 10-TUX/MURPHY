from abc import ABC, abstractmethod

from app.models.parsed_file import ParsedFile


class Parser(ABC):
    """Base class for all parsers."""

    @abstractmethod
    def parse(self, source_code: str, file_path: str) -> ParsedFile:
        """Parse source code into a structured representation."""
        pass
