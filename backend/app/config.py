import os

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Database
    database_url: str

    # CORS
    cors_origins: list[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]

    # Security - REQUIRED: must be set via SECRET_KEY environment variable
    secret_key: str

    # Google OAuth
    google_client_id: str = ""
    google_client_secret: str = ""
    authorized_email: str = ""
    auth_secret: str = ""

    @field_validator("secret_key")
    @classmethod
    def validate_secret_key(cls, v: str) -> str:
        if not v or v == "change-me-in-production":
            raise ValueError(
                "SECRET_KEY environment variable must be set to a secure value"
            )
        if len(v) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters long")
        return v


settings = Settings()
