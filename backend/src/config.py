"""SynthData application configuration."""

from __future__ import annotations

import os
from functools import lru_cache

from dotenv import load_dotenv

load_dotenv()


class Settings:
    """Application settings loaded from environment variables."""

    # App
    APP_NAME: str = "SynthData"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))

    # CORS
    CORS_ORIGINS: list[str] = os.getenv(
        "CORS_ORIGINS", "http://localhost:3000"
    ).split(",")

    # Azure OpenAI
    AZURE_OPENAI_ENDPOINT: str = os.getenv("AZURE_OPENAI_ENDPOINT", "")
    AZURE_OPENAI_API_KEY: str = os.getenv("AZURE_OPENAI_API_KEY", "")
    AZURE_OPENAI_API_VERSION: str = os.getenv(
        "AZURE_OPENAI_API_VERSION", "2024-06-01"
    )
    AZURE_OPENAI_DEPLOYMENT: str = os.getenv(
        "AZURE_OPENAI_DEPLOYMENT", "gpt-4o"
    )

    # Azure Speech
    AZURE_SPEECH_KEY: str = os.getenv("AZURE_SPEECH_KEY", "")
    AZURE_SPEECH_REGION: str = os.getenv("AZURE_SPEECH_REGION", "eastus")

    # Azure Storage
    AZURE_STORAGE_CONNECTION_STRING: str = os.getenv(
        "AZURE_STORAGE_CONNECTION_STRING", ""
    )
    AZURE_STORAGE_CONTAINER: str = os.getenv(
        "AZURE_STORAGE_CONTAINER", "synthdata-datasets"
    )

    # Job defaults
    MAX_ROWS_PER_REQUEST: int = int(os.getenv("MAX_ROWS_PER_REQUEST", "10000"))
    DEFAULT_OUTPUT_FORMAT: str = os.getenv("DEFAULT_OUTPUT_FORMAT", "json")


@lru_cache
def get_settings() -> Settings:
    """Return cached application settings."""
    return Settings()
