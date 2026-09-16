"""
Configuration settings for the RelayCX backend.
Reads environment variables with graceful fallback for local development.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment or .env file.
    """
    TURSO_DATABASE_URL: str = ""
    TURSO_AUTH_TOKEN: str = ""
    DATABASE_URL: str = "sqlite:///./relaycx.db"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
