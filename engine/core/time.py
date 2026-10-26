"""UTC timestamp handling and normalization utilities."""

from datetime import UTC, datetime


def utc_now() -> datetime:
    """Return the current datetime strictly in UTC timezone."""
    return datetime.now(UTC)


def ensure_utc(dt: datetime) -> datetime:
    """Ensure a given datetime has UTC timezone.

    If naive, attaches UTC. If non-UTC aware, converts to UTC.
    """
    if dt.tzinfo is None:
        return dt.replace(tzinfo=UTC)
    return dt.astimezone(UTC)


def iso_utc(dt: datetime) -> str:
    """Format datetime as ISO 8601 UTC string (with Z suffix)."""
    utc_dt = ensure_utc(dt)
    return utc_dt.isoformat().replace("+00:00", "Z")
