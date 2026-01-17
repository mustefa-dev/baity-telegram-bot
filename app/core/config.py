from functools import lru_cache
from typing import Any

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with validation."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    APP_NAME: str = "Baity Telegram Bot"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = Field(default="development", pattern="^(development|staging|production)$")

    # API
    API_V1_PREFIX: str = "/api/v1"

    # Security
    WEBHOOK_API_KEY: str = Field(default="baity-webhook-secret-key-2024", min_length=16)

    # Telegram
    BOT_TOKEN: str = Field(default="8139940477:AAG_q-ghGtDzvVePKZcSQZuDXYu2NDRRAu0", min_length=40)

    # City to Channel mapping (loaded from env as JSON or configured here)
    # Format: {"1": "@channel1", "2": "@channel2"}
    CITY_CHANNELS: dict[int, str] = Field(default_factory=lambda: {
        1: "@mu_baghdad_baity",
    })

    # Logging
    LOG_LEVEL: str = Field(default="INFO", pattern="^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$")
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # Rate limiting
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_PERIOD: int = 60  # seconds

    # Retry configuration
    MAX_RETRIES: int = 3
    RETRY_DELAY: float = 1.0  # seconds

    @field_validator("CITY_CHANNELS", mode="before")
    @classmethod
    def parse_city_channels(cls, v: Any) -> dict[int, str]:
        """Parse city channels from JSON string or dict."""
        if isinstance(v, str):
            import json
            parsed = json.loads(v)
            return {int(k): str(val) for k, val in parsed.items()}
        if isinstance(v, dict):
            return {int(k): str(val) for k, val in v.items()}
        return v

    @model_validator(mode="after")
    def validate_settings(self) -> "Settings":
        """Validate settings after all fields are set."""
        if self.ENVIRONMENT == "production" and self.DEBUG:
            raise ValueError("DEBUG must be False in production environment")
        return self

    def get_channel_for_city(self, city_id: int) -> str | None:
        """Get Telegram channel ID for a city."""
        return self.CITY_CHANNELS.get(city_id)


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


settings = get_settings()
