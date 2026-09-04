"""MURPHY - Vector Store Service
Provides FAISS - based vector storage and similarity search for code/document chunks."""

from pathlib import Path
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_community.vectorstores import FAISS

from app.core.config import get_settings
from app.services.embedding_service import EmbeddingService


class VectorStoreService:
    """Service responsible for creating and managing a FAISS vector store."""

    def __init__(
        self,
        embeddings: Embeddings | None = None,
    ) -> None:
        """Initialize the vector store service."""
        self.embeddings = (
            embeddings
            if embeddings is not None
            else EmbeddingService().get_embeddings()
        )
        self.vectorstore: FAISS | None = None

    def create(self, documents: list[Document]) -> FAISS:
        """Create a FAISS vector store from documents"""
        if not documents:
            raise ValueError("Cannot create vector store from empty documents.")
        self.vectorstore = FAISS.from_documents(
            documents,
            self.embeddings,
        )

        return self.vectorstore

    def similarity_search(
        self,
        query: str,
        k: int = 4,
    ) -> list[Document]:
        """
        Performs a similarity search using the vector store.
        Returns the top k most relevant documents.
        """
        if self.vectorstore is None:
            raise ValueError("Vector store has not been created.")

        if not query.strip():
            return []

        return self.vectorstore.similarity_search(query, k=k)

    def save(
        self,
        path: str | Path,
    ) -> None:
        """Persist the FAISS vector store to disk"""
        if self.vectorstore is None:
            raise ValueError("Vector store has not been created.")

        save_path = Path(path)
        save_path.mkdir(parents=True, exist_ok=True)

        # Saves the vectorstore to disk
        self.vectorstore.save_local(str(save_path))

    def load(
        self,
        path: str | Path,
    ) -> FAISS:
        """Load a previously saved FAISS vector store from disk"""
        load_path = Path(path)

        if not load_path.exists():
            raise FileNotFoundError(f"Vector store path does not exist: {load_path}")
        self.vectorstore = FAISS.load_local(
            str(load_path),
            self.embeddings,
            allow_dangerous_deserialization=True,
        )
        return self.vectorstore
