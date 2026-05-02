from __future__ import annotations

import logging
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    """Application settings loaded from environment variables.

    Environment variables use the `RESEARCH_` prefix and are loaded from
    `.env` when present.
    """

    openalex_email: str | None = None
    openalex_api_key: str | None = None
    semantic_scholar_api_key: str | None = None
    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = "research2026"
    data_dir: Path = Path("data/")
    cache_dir: Path = Path("data/cache/")
    log_level: str = "INFO"
    api_key: str | None = None
    rate_limit: str = "60/minute"
    cors_origins: str = "*"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="RESEARCH_",
        extra="ignore",
    )


settings = Settings()
