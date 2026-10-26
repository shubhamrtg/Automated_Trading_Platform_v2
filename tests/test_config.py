"""Tests for platform configuration, UTC enforcement, and logging redaction."""

from datetime import UTC, datetime

import pytest
from pydantic import SecretStr, ValidationError

from engine.core.config import Settings
from engine.core.logging import redact_secrets
from engine.core.time import ensure_utc, iso_utc, utc_now


def test_default_config_values() -> None:
    """Verify standard default configuration values."""
    settings = Settings(
        DATABASE_URL="sqlite+aiosqlite:///:memory:",
        ENGINE_CONTROL_SECRET=SecretStr("test-secret"),
    )
    assert settings.app_name == "Automated Trading Platform"
    assert settings.environment == "development"
    assert settings.default_account_currency == "USD"
    assert settings.live_mode_enabled is False


def test_live_mode_safety_gate_rejection() -> None:
    """Safety rule: live_mode_enabled=True must raise a validation error."""
    with pytest.raises(ValidationError) as exc_info:
        Settings(
            LIVE_MODE_ENABLED=True,
            ENGINE_CONTROL_SECRET=SecretStr("test-secret"),
        )
    assert "Live trading is strictly disabled in Phase 1" in str(exc_info.value)


def test_reject_aurafx_placeholder() -> None:
    """DECISIONS D1: 'AuraFX' is rejected as product name."""
    with pytest.raises(ValidationError) as exc_info:
        Settings(
            APP_NAME="AuraFX Pro",
            ENGINE_CONTROL_SECRET=SecretStr("test-secret"),
        )
    assert "AuraFX" in str(exc_info.value)


def test_utc_helpers() -> None:
    """Verify UTC timestamp generation and normalization."""
    now = utc_now()
    assert now.tzinfo is not None
    assert now.tzinfo == UTC

    naive = datetime(2026, 10, 26, 12, 0, 0)
    aware = ensure_utc(naive)
    assert aware.tzinfo == UTC

    iso_str = iso_utc(aware)
    assert iso_str.endswith("Z")
    assert "+00:00" not in iso_str


def test_log_secret_redaction() -> None:
    """Verify structured log processor redacts sensitive fields."""
    event_dict = {
        "event": "user_login",
        "username": "trader",
        "password": "super-secret-password",
        "api_key": "my-secret-key",
        "nested": {
            "token": "bearer-token",
            "normal_data": "visible",
        },
    }
    redacted = redact_secrets(None, "info", event_dict)

    assert redacted["password"] == "[REDACTED]"
    assert redacted["api_key"] == "[REDACTED]"
    assert redacted["nested"]["token"] == "[REDACTED]"
    assert redacted["nested"]["normal_data"] == "visible"
    assert redacted["username"] == "trader"
