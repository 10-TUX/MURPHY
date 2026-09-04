from unittest.mock import MagicMock, patch

import pytest

from app.core.config import get_settings
from app.services.embedding_service import EmbeddingService


def test_gemini_provider_is_selected(monkeypatch):
    """Gemini should be selected when configured as the provider."""

    monkeypatch.setenv("EMBEDDING_PROVIDER", "gemini")
    monkeypatch.setenv("GOOGLE_API_KEY", "test-api-key")

    get_settings.cache_clear()

    with patch(
        "app.services.embedding_service.GoogleGenerativeAIEmbeddings"
    ) as mock_embeddings:
        service = EmbeddingService()
        result = service.get_embeddings()

        assert result is mock_embeddings.return_value
        mock_embeddings.assert_called_once()


def test_huggingface_provider_is_selected(monkeypatch):
    """HuggingFace should be selected when configured as the provider."""

    monkeypatch.setenv("EMBEDDING_PROVIDER", "huggingface")

    get_settings.cache_clear()

    with patch("app.services.embedding_service.SentenceTransformer") as mock_model:
        mock_model.return_value = MagicMock()

        service = EmbeddingService()
        result = service.get_embeddings()

        assert result is not None
        mock_model.assert_called_once()


def test_invalid_provider_raises_error(monkeypatch):
    """Unsupported providers should raise a clear error."""

    monkeypatch.setenv(
        "EMBEDDING_PROVIDER",
        "invalid-provider",
    )

    get_settings.cache_clear()

    service = EmbeddingService()

    with pytest.raises(
        ValueError,
        match="Unsupported embedding provider",
    ):
        service.get_embeddings()


def test_gemini_requires_api_key(monkeypatch):
    """Gemini should require an API key."""

    monkeypatch.setenv("EMBEDDING_PROVIDER", "gemini")
    monkeypatch.setenv("GOOGLE_API_KEY", "")

    get_settings.cache_clear()

    service = EmbeddingService()

    with pytest.raises(
        ValueError,
        match="Missing GOOGLE_API_KEY",
    ):
        service.get_embeddings()
