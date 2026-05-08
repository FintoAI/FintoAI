"""Application configuration.

All config comes from environment variables, loaded from .env in development.
Never hardcode secrets. Never log the Settings object.
"""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # GoCardless
    gocardless_secret_id: str = Field(default="", alias="GOCARDLESS_SECRET_ID")
    gocardless_secret_key: str = Field(default="", alias="GOCARDLESS_SECRET_KEY")

    # Anthropic
    anthropic_api_key: str = Field(default="", alias="ANTHROPIC_API_KEY")

    # Storage
    database_url: str = Field(default="sqlite:///./fintoai.db", alias="DATABASE_URL")

    # App
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")


@lru_cache
def get_settings() -> Settings:
    """Cached settings accessor. Use this everywhere instead of constructing Settings()."""
    return Settings()
