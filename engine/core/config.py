"""Platform configuration management using Pydantic v2 Settings."""

from functools import lru_cache
from typing import Literal

from pydantic import Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Global configuration settings for the trading engine and platform."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Core identification
    app_name: str = Field(default="Automated Trading Platform", alias="APP_NAME")
    environment: Literal["development", "production", "test"] = Field(
        default="development", alias="ENVIRONMENT"
    )
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    # Database
    database_url: str = Field(
        default="sqlite+aiosqlite:///./data/trading_platform.db",
        alias="DATABASE_URL",
    )

    # Security & IPC
    engine_control_secret: SecretStr = Field(
        default=SecretStr("default-insecure-dev-secret-change-in-env"),
        alias="ENGINE_CONTROL_SECRET",
    )

    # Account defaults (DECISIONS D10)
    default_account_currency: str = Field(default="USD", alias="DEFAULT_ACCOUNT_CURRENCY")

    # Safety Gate: Live mode is disabled in Phase 1 (AGENTS.md rule)
    live_mode_enabled: bool = Field(default=False, alias="LIVE_MODE_ENABLED")

    @field_validator("live_mode_enabled")
    @classmethod
    def validate_live_mode_disabled(cls, v: bool) -> bool:
        if v:
            raise ValueError(
                "Live trading is strictly disabled in Phase 1. "
                "Never write code that enables it or removes the live gate."
            )
        return False

    @field_validator("app_name")
    @classmethod
    def validate_app_name(cls, v: str) -> str:
        if "AuraFX" in v:
            raise ValueError("Product name 'AuraFX' is rejected per DECISIONS D1.")
        return v


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return the cached singleton Settings instance."""
    return Settings()
