"""MURPHY - LLM Service
Provides the configured Google Gemini chat model for MURPHY."""

from langchain_core.language_models import BaseChatModel
from langchain_google_genai import ChatGoogleGenerativeAI

from app.core.config import get_settings


class LLMService:
    """Factory and manager for MURPHY LLM providers."""

    def __init__(self) -> None:
        self.settings = get_settings()
        self._llm: BaseChatModel | None = None

    def get_llm(self) -> BaseChatModel:
        """Return the Google Gemini chat model."""
        if self._llm is not None:
            return self._llm

        if not self.settings.google_api_key:
            raise ValueError("Missing GOOGLE_API_KEY for Gemini LLM")

        self._llm = ChatGoogleGenerativeAI(
            model=self.settings.gemini_model,
            google_api_key=self.settings.google_api_key,
            temperature=self.settings.gemini_temperature,
        )
        return self._llm
