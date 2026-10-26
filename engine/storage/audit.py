"""Append-only audit logging service."""

import json
from datetime import datetime
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from engine.core.time import utc_now
from engine.storage.models import AuditLog


class AuditLogger:
    """Service responsible for appending immutable audit trail records (FR-SEC-4)."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def log_event(
        self,
        event_type: str,
        actor_type: str,
        actor_id: str,
        payload: dict[str, Any],
        profile_id: str | None = None,
        timestamp_utc: datetime | None = None,
    ) -> AuditLog:
        """Append a new record to the audit log table."""
        record = AuditLog(
            timestamp_utc=timestamp_utc or utc_now(),
            event_type=event_type,
            actor_type=actor_type,
            actor_id=actor_id,
            profile_id=profile_id,
            payload_json=json.dumps(payload, default=str),
        )
        self._session.add(record)
        await self._session.commit()
        await self._session.refresh(record)
        return record
