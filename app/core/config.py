"""
MURPHY — Application Configuration

Loads environment variables using python-dotenv and exposes them
as a validated Pydantic Settings object used throughout the app.
"""

import os
from pathlib import Path
from functools import lru_cache

from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings

# ── Load .env file ──────────────────────────────────────
# Resolve from project root regardless of where the app is launched from.
_env_path = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(dotenv_path=_env_path)


class Settings(BaseSettings):
    """Centralised application configuration.

    Values are read from environment variables (or .env file).
    """

    # ── Google Gemini ───────────────────────────────────
    google_api_key: str = Field(
        default="",
        description="Google Gemini API key",
    )

    # ── Application ─────────────────────────────────────
    app_name: str = Field(default="MURPHY")
    app_env: str = Field(default="development")
    debug: bool = Field(default=True)

    # ── Embedding Provider ──────────────────────────────
    embedding_provider: str = Field(
        default="gemini",
        description="'gemini' or 'huggingface'",
    )

    # ── FAISS / Vector Store ────────────────────────────
    vectorstore_path: str = Field(default="./vectorstore")

    # ── Upload Settings ─────────────────────────────────
    upload_dir: str = Field(default="./uploads")
    max_upload_size_mb: int = Field(default=100)

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Return a cached Settings instance (singleton)."""
    return Settings()
