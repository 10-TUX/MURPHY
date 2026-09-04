from langchain_core.embeddings import Embeddings
from langchain_core.documents import Document

from app.services.vector_store_service import VectorStoreService


class FakeEmbeddings(Embeddings):
    """Deterministic embeddings for testing."""

    def embed_documents(
        self,
        texts: list[str],
    ) -> list[list[float]]:
        return [[float(len(text)), 1.0, 0.0] for text in texts]

    def embed_query(
        self,
        text: str,
    ) -> list[float]:
        return [float(len(text)), 1.0, 0.0]


def test_create_vector_store():
    """Vector store should be created from documents."""

    documents = [
        Document(
            page_content="def login(): pass",
            metadata={"source": "auth.py"},
        ),
        Document(
            page_content="def calculate_total(): pass",
            metadata={"source": "cart.py"},
        ),
    ]

    service = VectorStoreService(
        embeddings=FakeEmbeddings(),
    )

    vectorstore = service.create(documents)

    assert vectorstore is not None
    assert service.vectorstore is vectorstore


def test_similarity_search_returns_documents():
    """Similarity search should return matching documents."""

    documents = [
        Document(
            page_content="def login(): pass",
            metadata={"source": "auth.py"},
        ),
        Document(
            page_content="def calculate_total(): pass",
            metadata={"source": "cart.py"},
        ),
    ]

    service = VectorStoreService(
        embeddings=FakeEmbeddings(),
    )

    service.create(documents)

    results = service.similarity_search(
        "def login(): pass",
        k=1,
    )

    assert len(results) == 1
    assert isinstance(results[0], Document)


def test_empty_documents_raise_error():
    """Creating a vector store without documents should fail."""

    service = VectorStoreService(
        embeddings=FakeEmbeddings(),
    )

    try:
        service.create([])
        assert False
    except ValueError as exc:
        assert "empty documents" in str(exc)


def test_search_before_creation_raises_error():
    """Searching before creating a vector store should fail."""

    service = VectorStoreService(
        embeddings=FakeEmbeddings(),
    )

    try:
        service.similarity_search("login")
        assert False
    except ValueError as exc:
        assert "not been created" in str(exc)


def test_empty_query_returns_empty_list():
    """Empty queries should not perform a search."""

    documents = [
        Document(
            page_content="def login(): pass",
            metadata={"source": "auth.py"},
        ),
    ]

    service = VectorStoreService(
        embeddings=FakeEmbeddings(),
    )

    service.create(documents)

    results = service.similarity_search("   ")

    assert results == []


def test_save_and_load_vector_store(tmp_path):
    """A saved vector store should be loadable."""
    documents = [
        Document(page_content="def login(): pass", metadata={"source": "auth.py"}),
        Document(
            page_content="def calculate_total(): pass", metadata={"source": "cart.py"}
        ),
    ]
    embeddings = FakeEmbeddings()
    service = VectorStoreService(embeddings=embeddings)

    service.create(documents)
    save_path = tmp_path / "vectorstore"
    service.save(save_path)
    assert save_path.exists()

    loaded_service = VectorStoreService(embeddings=embeddings)
    vectorstore = loaded_service.load(str(save_path))

    assert vectorstore is not None
    assert loaded_service.vectorstore is vectorstore

    results = loaded_service.similarity_search("def login(): pass", k=1)
    assert len(results) == 1
    assert results[0].metadata["source"] == "auth.py"
