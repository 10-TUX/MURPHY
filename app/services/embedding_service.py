"""MURPHY - Embedding Service

Provides a unified embedding interface for MURPHY.
Primary provider:
    Google Gemini embeddings
Fallback provider:
    Hugging FaceSentence Transformers


"""

from typing import List
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_core.embeddings import Embeddings
from sentence_transformers import SentenceTransformer
from app.core.config import get_settings


class HuggingFaceEmbeddings(Embeddings):
    """Langchain-compatible wrapper around SentenceTransformer."""

    def __init__(self, model_name: str) -> None:
        self.model_name = model_name
        self.model = SentenceTransformer(model_name)

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple documents."""
        embeddings = self.model.encode(
            texts,
            convert_to_numpy=True,
            normalize_embeddings=True,
        )
        return embeddings.tolist()

    def embed_query(self, text: str) -> List[float]:
        """Generate an embedding for a single query."""
        embedding = self.model.encode(
            text,
            convert_to_numpy=True,
            normalize_embeddings=True,
        )
        return embedding.tolist()


class EmbeddingService:
    """Factory and manager for MURPHY embedding providers."""

    def __init__(self) -> None:
        self.settings = get_settings()
        self._embeddings: Embeddings | None = None

    def get_embeddings(self) -> Embeddings:
        """Return the configured embedding provider."""
        if self._embeddings is not None:
            return self._embeddings
        provider = self.settings.embedding_provider.lower().strip()

        if provider == "gemini":
            self._embeddings = self._create_gemini_embeddings()
        elif provider == "huggingface":
            self._embeddings = self._create_huggingface_embeddings()
        else:
            raise ValueError(
                f"Unsupported embedding provider: {provider}. "
                f"Must be one of 'gemini', 'huggingface'."
            )
        return self._embeddings

    def _create_gemini_embeddings(self) -> GoogleGenerativeAIEmbeddings:
        """Create GeminiEmbeddings instance."""
        if not self.settings.google_api_key:
            raise ValueError("Missing GOOGLE_API_KEY for Gemini embeddings")
        return GoogleGenerativeAIEmbeddings(
            model=self.settings.embedding_model,
            google_api_key=self.settings.google_api_key,
            output_dimensionality=self.settings.embedding_dimension,
        )

    def _create_huggingface_embeddings(self) -> HuggingFaceEmbeddings:
        """Create HuggingFaceEmbeddings instance."""
        return HuggingFaceEmbeddings(
            model_name=self.settings.huggingface_embedding_model
        )
