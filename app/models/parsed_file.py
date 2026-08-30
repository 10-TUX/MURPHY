from typing import Optional

from pydantic import BaseModel


class ImportInfo(BaseModel):
    """Information about an import statement."""

    module: str
    names: list[str] = []
    alias: Optional[str] = None


class FunctionInfo(BaseModel):
    """Information about a Python function."""

    name: str
    arguments: list[str] = []
    return_type: Optional[str] = None
    docstring: Optional[str] = None
    start_line: int
    end_line: int


class ClassInfo(BaseModel):
    """Information about a Python class."""

    name: str
    bases: list[str] = []
    docstring: Optional[str] = None
    methods: list[FunctionInfo] = []
    start_line: int
    end_line: int


class CommentInfo(BaseModel):
    """Information about a comment."""

    content: str
    start_line: int
    end_line: int


class ParsedFile(BaseModel):
    """Language Independent Structured representation of a parsed source file."""

    file_path: str
    language: str
    content: str

    module_docstring: Optional[str] = None
    imports: list[ImportInfo] = []
    functions: list[FunctionInfo] = []
    classes: list[ClassInfo] = []
    comments: list[CommentInfo] = []
