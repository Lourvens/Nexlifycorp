"""Core configuration - shared by ingestion, retrieval, and other modules."""
from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        extra="ignore",
        env_file=".env",
        env_file_encoding="utf-8",
    )

    # Qdrant
    qdrant_url: str = "http://localhost:6333"
    qdrant_collection: str = "nexlify_kb"

    # Embeddings
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    embedding_dim: int = 384

    # Paths
    data_dir: Path = Path("data")
    sec_filings_dir: Path = Path("data/sec-filings")
    internal_docs_dir: Path = Path("data/internal")

    # SEC EDGAR
    sec_edgar_company_name: str = "Nexlify Corp"
    sec_edgar_email: str = "nexlify@nexlify.com"

    # HuggingFace (for future use)
    huggingface_api_key: str | None = None


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


@lru_cache(maxsize=1)
def get_config() -> Settings:
    """Alias for get_settings for backward compatibility."""
    return get_settings()


def get_qdrant_url() -> str:
    """Get Qdrant URL from settings or env."""
    import os
    return os.getenv("QDRANT_URL", get_config().qdrant_url)


def get_collection_name() -> str:
    """Get collection name from settings or env."""
    import os
    return os.getenv("QDRANT_COLLECTION", get_config().qdrant_collection)