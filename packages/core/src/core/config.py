"""Application configuration models and helpers."""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path
from typing import Any, Literal

from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

Environment = Literal["development", "test", "production"]

ENV_FILE_NAME = ".env"


def find_env_file(start_dir: Path | None = None) -> Path | None:
    """Searches the current directory and its parents for a `.env` file."""
    current_dir = (start_dir or Path.cwd()).resolve()

    for directory in (current_dir, *current_dir.parents):
        candidate = directory / ENV_FILE_NAME
        if candidate.is_file():
            return candidate

    return None


class Settings(BaseSettings):
    """Defines environment-backed settings used throughout the workspace."""

    app_name: str = "tech-career-platform"
    environment: Environment = "development"

    # Database
    database_url: str | None = None
    db_echo: bool = True

    # App / API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    log_level: str = "INFO"

    # Auth
    host: str = "localhost:4200"
    jwt_secret: str = "reallysecuresecret-dev-default-key"
    jwt_algorithm: str = "HS256"

    #OpenAI
    openai_api_key: str | None = Field(default=None, validation_alias=AliasChoices("AZURE_OPENAI_API_KEY", "OPENAI_API_KEY"))
    openai_model: str = Field(default="gpt-4o-mini", validation_alias=AliasChoices("AZURE_OPENAI_DEPLOYMENT", "OPENAI_MODEL"))
    openai_endpoint: str | None = Field(default=None, validation_alias=AliasChoices("AZURE_OPENAI_ENDPOINT", "OPENAI_ENDPOINT"))

    # CORS
    allowed_origins: list[str] = Field(default=["http://localhost:4200"])

    model_config = SettingsConfigDict(
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    def __init__(self, **values: Any) -> None:
        """Builds settings using the nearest `.env` file when present."""
        environment = str(
            values.get("environment")
            or os.environ.get("ENVIRONMENT")
            or "development"
        ).lower()
        env_file = find_env_file()

        if env_file is None and environment == "development":
            raise FileNotFoundError(
                "No .env file found in the current working directory or any parent "
                "directory. Copy .env.example to .env in the root of the repo before "
                "running in development."
            )

        super().__init__(_env_file=env_file, **values)

    @property
    def effective_database_url(self) -> str:
        """Returns the configured database URL or the default for the environment."""
        if self.database_url:
            return self.database_url

        if self.environment == "test":
            return "postgresql+psycopg://postgres:postgres@postgres:5432/platform_test"

        return "postgresql+psycopg://postgres:postgres@postgres:5432/platform_dev"

    @property
    def is_development(self) -> bool:
        return self.environment == "development"

    @property
    def is_test(self) -> bool:
        return self.environment == "test"

    @property
    def is_production(self) -> bool:
        return self.environment == "production"


@lru_cache
def get_settings() -> Settings:
    """Returns a cached settings instance for the current process."""
    return Settings()