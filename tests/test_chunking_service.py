from app.models.parsed_file import ParsedFile
from app.services.chunking_service import ChunkingService


def test_split_text_empty_content():
    service = ChunkingService()

    result = service.split_text("")

    assert result == []


def test_split_text_creates_chunks():
    service = ChunkingService(chunk_size=100, chunk_overlap=20)

    content = "hello world " * 100

    chunks = service.split_text(content)

    assert len(chunks) > 1
    assert all(len(chunk) <= 100 for chunk in chunks)


def test_chunk_uses_parsed_file_language():
    service = ChunkingService(chunk_size=100, chunk_overlap=20)

    parsed_file = ParsedFile(
        file_path="test.py",
        language="python",
        content="def hello():\n    print('Hello')",
    )

    chunks = service.chunk(parsed_file)

    assert len(chunks) >= 1
    assert "def hello" in chunks[0].page_content


def test_chunk_empty_content():
    service = ChunkingService()

    parsed_file = ParsedFile(
        file_path="empty.py",
        language="python",
        content="",
    )

    chunks = service.chunk(parsed_file)

    assert chunks == []


def test_chunk_size():
    service = ChunkingService(chunk_size=1000, chunk_overlap=200)

    parsed_file = ParsedFile(
        file_path="test.py",
        language="python",
        content="hello world " * 500,
    )

    chunks = service.chunk(parsed_file)

    assert len(chunks) > 1
    assert all(len(chunk.page_content) <= 1000 for chunk in chunks)

    assert chunks[0].metadata["source"] == "test.py"
    assert chunks[0].metadata["language"] == "python"


def test_small_file_stays_as_one_chunk():
    service = ChunkingService()

    parsed_file = ParsedFile(
        file_path="small.py",
        language="python",
        content="def hello():\n    return 'hello'",
    )

    chunks = service.chunk(parsed_file)

    assert len(chunks) == 1
    assert chunks[0].page_content == parsed_file.content


def test_large_file_creates_multiple_chunks():
    service = ChunkingService(
        chunk_size=1000,
        chunk_overlap=200,
    )

    parsed_file = ParsedFile(
        file_path="large.py",
        language="python",
        content="hello world " * 500,
    )

    chunks = service.chunk(parsed_file)

    assert len(chunks) > 1
    assert all(len(chunk.page_content) <= 1000 for chunk in chunks)
