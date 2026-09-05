from unittest.mock import patch

import pytest

from app.services.llm_service import LLMService


def test_get_llm_requires_api_key():
    """LLM creation should fail when the API key is missing."""

    with patch("app.services.llm_service.get_settings") as mock_settings:
        mock_settings.return_value.google_api_key = ""
        mock_settings.return_value.gemini_model = "gemini-2.5-flash"
        mock_settings.return_value.gemini_temperature = 0.2

        service = LLMService()

        with pytest.raises(ValueError, match="Missing GOOGLE_API_KEY"):
            service.get_llm()


def test_get_llm_creates_gemini_model():
    """LLM service should create a Gemini chat model."""

    with patch("app.services.llm_service.get_settings") as mock_settings:
        mock_settings.return_value.google_api_key = "test-key"
        mock_settings.return_value.gemini_model = "gemini-2.5-flash"
        mock_settings.return_value.gemini_temperature = 0.2

        service = LLMService()

        with patch("app.services.llm_service.ChatGoogleGenerativeAI") as mock_llm:
            llm = service.get_llm()

            mock_llm.assert_called_once_with(
                model="gemini-2.5-flash",
                google_api_key="test-key",
                temperature=0.2,
            )

            assert llm is mock_llm.return_value


def test_get_llm_is_cached():
    """LLM service should reuse the same model instance."""

    with patch("app.services.llm_service.get_settings") as mock_settings:
        mock_settings.return_value.google_api_key = "test-key"
        mock_settings.return_value.gemini_model = "gemini-2.5-flash"
        mock_settings.return_value.gemini_temperature = 0.2

        service = LLMService()

        with patch("app.services.llm_service.ChatGoogleGenerativeAI") as mock_llm:
            first = service.get_llm()
            second = service.get_llm()

            assert first is second
            mock_llm.assert_called_once()
