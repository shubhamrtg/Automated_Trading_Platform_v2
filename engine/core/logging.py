"""Structured logging configuration using structlog."""

import logging
import sys
from collections.abc import MutableMapping
from typing import Any, cast

import structlog

REDACTED_KEYS = {
    "password",
    "secret",
    "api_key",
    "token",
    "authorization",
    "engine_control_secret",
    "gemini_api_key",
    "smtp_password",
    "telegram_bot_token",
}


def redact_secrets(
    logger: Any, method_name: str, event_dict: MutableMapping[str, Any]
) -> MutableMapping[str, Any]:
    """Redact any sensitive dictionary keys to prevent credential leakage in logs."""
    for key, value in list(event_dict.items()):
        if any(sensitive in key.lower() for sensitive in REDACTED_KEYS):
            event_dict[key] = "[REDACTED]"
        elif isinstance(value, MutableMapping):
            event_dict[key] = redact_secrets(logger, method_name, value)
    return event_dict


def setup_logging(log_level: str = "INFO", json_format: bool = False) -> None:
    """Configure structlog and standard library logging."""
    shared_processors: list[structlog.types.Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso", utc=True),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        redact_secrets,
    ]

    structlog.configure(
        processors=[*shared_processors, structlog.stdlib.ProcessorFormatter.wrap_for_formatter],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    formatter: structlog.types.Processor
    if json_format:
        formatter = structlog.processors.JSONRenderer()
    else:
        formatter = structlog.dev.ConsoleRenderer(colors=True)

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(
        structlog.stdlib.ProcessorFormatter(
            foreign_pre_chain=shared_processors,
            processor=formatter,
        )
    )

    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.addHandler(handler)
    root_logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """Return a configured structlog bound logger."""
    return cast(structlog.stdlib.BoundLogger, structlog.get_logger(name))
