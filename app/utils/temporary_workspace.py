from pathlib import Path
from tempfile import TemporaryDirectory


class TemporaryWorkspace:
    """Manages a temporary workspace for the repository processing"""

    def __init__(self, prefix: str = "murphy_repo_"):
        self.prefix = prefix
        self._temporary_directory = None
        self.path: Path | None = None

    def __enter__(self) -> Path:
        self._temporary_directory = TemporaryDirectory(prefix=self.prefix)
        self.path = Path(self._temporary_directory.name)
        return self.path

    def __exit__(self, exc_type, exc_value, traceback):
        if self._temporary_directory is not None:
            self._temporary_directory.cleanup()
        self.path = None
        self._temporary_directory = None
