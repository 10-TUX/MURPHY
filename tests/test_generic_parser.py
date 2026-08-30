from app.parsers.generic_parser import GenericParser


def test_parse_markdown_file():
    source_code = "# Murphy\n\nAI codebase assistant."

    parser = GenericParser()
    result = parser.parse(source_code, "README.md")

    assert result.file_path == "README.md"
    assert result.language == "markdown"
    assert result.content == source_code

    assert result.module_docstring is None
    assert result.imports == []
    assert result.functions == []
    assert result.classes == []


def test_parse_unknown_file_as_text():
    source_code = "Some plain text content."
    parser = GenericParser()
    result = parser.parse(source_code, "notes.xyz")

    assert result.file_path == "notes.xyz"
    assert result.language == "text"
    assert result.content == source_code
