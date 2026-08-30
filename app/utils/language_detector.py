from pathlib import Path


LANGUAGE_MAP = {
    ".py": "python",
    ".js": "javascript",
    ".jsx": "javascript",
    ".ts": "typescript",
    ".tsx": "typescript",
    ".java": "java",
    ".c": "c",
    ".h": "c",
    ".cpp": "cpp",
    ".cc": "cpp",
    ".cxx": "cpp",
    ".hpp": "cpp",
    ".go": "go",
    ".rs": "rust",
    ".rb": "ruby",
    ".php": "php",
    ".cs": "csharp",
    ".swift": "swift",
    ".kt": "kotlin",
    ".kts": "kotlin",
    ".md": "markdown",
    ".json": "json",
    ".yaml": "yaml",
    ".yml": "yaml",
    ".xml": "xml",
    ".html": "html",
    ".css": "css",
    ".scss": "scss",
    ".sql": "sql",
    ".txt": "text",
}


SPECIAL_FILES = {
    "Dockerfile": "dockerfile",
    "Makefile": "makefile",
    ".env": "dotenv",
}


def detect_language(file_path: str) -> str:
    """Detect the language of a file from its name or extension."""

    path = Path(file_path)

    if path.name in SPECIAL_FILES:
        return SPECIAL_FILES[path.name]

    return LANGUAGE_MAP.get(path.suffix.lower(), "text")
