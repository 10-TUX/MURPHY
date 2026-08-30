from app.parsers.python_parser import PythonParser
from textwrap import dedent
import pytest


def test_parse_module_docstring_and_imports():
    source_code = '''
"""Repository utilities."""

import os
import numpy as np

from pathlib import Path
from typing import Optional, List
'''

    parser = PythonParser()
    result = parser.parse(source_code, "repository.py")

    assert result.module_docstring == "Repository utilities."

    assert len(result.imports) == 4

    assert result.imports[0].module == "os"
    assert result.imports[0].alias is None

    assert result.imports[1].module == "numpy"
    assert result.imports[1].alias == "np"

    assert result.imports[2].module == "pathlib"
    assert result.imports[2].names == ["Path"]

    assert result.imports[3].module == "typing"
    assert result.imports[3].names == ["Optional", "List"]

    assert result.file_path == "repository.py"
    assert result.language == "python"
    assert result.content == source_code


def test_parse_function():
    source_code = '''
def calculate_total(price: float, tax: float = 0.18) -> float:
    """Calculate the final price."""
    return price + price * tax
'''

    parser = PythonParser()
    result = parser.parse(source_code, "repository.py")

    assert len(result.functions) == 1

    function = result.functions[0]

    assert function.name == "calculate_total"
    assert function.arguments == ["price", "tax"]
    assert function.return_type == "float"
    assert function.docstring == "Calculate the final price."
    assert function.start_line == 2
    assert function.end_line == 4


def test_parse_class_and_methods():
    source_code = '''
class Repository(BaseService):
    """Handles repository operations."""

    def upload(self, path: str) -> bool:
        """Upload a repository."""
        return True

    async def process(self, path: str) -> None:
        """Process the repository."""
        pass


def process_file(path: str) -> str:
    """Process a file."""
    return path
'''

    parser = PythonParser()
    result = parser.parse(source_code, "repository.py")

    assert len(result.classes) == 1

    repository = result.classes[0]

    assert repository.name == "Repository"
    assert repository.bases == ["BaseService"]
    assert repository.docstring == "Handles repository operations."

    assert len(repository.methods) == 2

    upload = repository.methods[0]

    assert upload.name == "upload"
    assert upload.arguments == ["self", "path"]
    assert upload.return_type == "bool"
    assert upload.docstring == "Upload a repository."
    assert upload.start_line == 5
    assert upload.end_line == 7

    process = repository.methods[1]

    assert process.name == "process"
    assert process.arguments == ["self", "path"]
    assert process.return_type == "None"
    assert process.docstring == "Process the repository."

    assert len(result.functions) == 1
    assert result.functions[0].name == "process_file"


def test_parse_complex_function_arguments():
    source_code = """
def request(
    url,
    timeout=10,
    *args,
    headers=None,
    **kwargs
):
    pass
"""

    parser = PythonParser()
    result = parser.parse(source_code, "repository.py")

    assert len(result.functions) == 1

    function = result.functions[0]

    assert function.name == "request"
    assert function.arguments == [
        "url",
        "timeout",
        "*args",
        "headers",
        "**kwargs",
    ]


def test_parse_comments():
    source_code = dedent(
        """
    # Module comment

    import os

    #Function comment
    def hello():
        #inside function
        print("hello") #inline comment
    """
    )

    parser = PythonParser()
    result = parser.parse(source_code, "repository.py")

    assert len(result.comments) == 4
    assert result.comments[0].content == "Module comment"
    assert result.comments[0].start_line == 2
    assert result.comments[0].end_line == 2

    assert result.comments[1].content == "Function comment"
    assert result.comments[1].start_line == 6
    assert result.comments[1].end_line == 6

    assert result.comments[2].content == "inside function"
    assert result.comments[2].start_line == 8
    assert result.comments[2].end_line == 8

    assert result.comments[3].content == "inline comment"
    assert result.comments[3].start_line == 9
    assert result.comments[3].end_line == 9


def test_parse_invalid_python():
    source_code = """ def broken_function() pass """
    parser = PythonParser()

    with pytest.raises(SyntaxError):
        parser.parse(source_code, "repository.py")


def test_parsed_file_contains_metadata():
    source_code = dedent(
        """
        import os
        
        def hello(name):
            return f"hello {name}"
    """
    )

    parser = PythonParser()
    result = parser.parse(source_code, "repository.py")

    assert len(result.imports) == 1
    assert result.imports[0].module == "os"

    assert len(result.functions) == 1
    assert result.functions[0].name == "hello"

    assert result.file_path == "repository.py"
    assert result.language == "python"
    assert result.content == source_code
