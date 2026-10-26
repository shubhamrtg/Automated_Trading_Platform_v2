"""Tests for append-only audit log and trade journal immutability triggers."""

import pytest
from sqlalchemy import delete, select, update
from sqlalchemy.exc import DBAPIError
from sqlalchemy.ext.asyncio import AsyncSession

from engine.storage.audit import AuditLogger
from engine.storage.models import AuditLog, TradeJournal


@pytest.mark.asyncio
async def test_audit_log_append_success(db_session: AsyncSession) -> None:
    """Verify appending a new audit log record succeeds."""
    logger = AuditLogger(db_session)
    record = await logger.log_event(
        event_type="ORDER_SUBMITTED",
        actor_type="ENGINE",
        actor_id="engine_main",
        profile_id="gold_trend_v1",
        payload={"symbol": "XAUUSD", "side": "BUY", "volume": 0.1},
    )
    assert record.id is not None
    assert record.event_type == "ORDER_SUBMITTED"

    # Query back
    result = await db_session.execute(select(AuditLog).where(AuditLog.id == record.id))
    fetched = result.scalar_one_or_none()
    assert fetched is not None
    assert "XAUUSD" in fetched.payload_json


@pytest.mark.asyncio
async def test_audit_log_update_blocked_by_trigger(db_session: AsyncSession) -> None:
    """Verify SQLite trigger aborts any attempt to UPDATE an existing audit record."""
    logger = AuditLogger(db_session)
    record = await logger.log_event(
        event_type="CONFIG_CHANGED",
        actor_type="USER",
        actor_id="trader1",
        payload={"param": "max_spread", "value": 2.0},
    )

    # Attempt to tamper with the audit record
    stmt = update(AuditLog).where(AuditLog.id == record.id).values(event_type="TAMPERED")
    with pytest.raises(DBAPIError) as exc_info:
        await db_session.execute(stmt)
        await db_session.commit()

    assert "Audit log is append-only" in str(exc_info.value)
    await db_session.rollback()


@pytest.mark.asyncio
async def test_audit_log_delete_blocked_by_trigger(db_session: AsyncSession) -> None:
    """Verify SQLite trigger aborts any attempt to DELETE an audit record."""
    logger = AuditLogger(db_session)
    record = await logger.log_event(
        event_type="RISK_HALT",
        actor_type="ENGINE",
        actor_id="risk_manager",
        payload={"reason": "Daily drawdown limit reached"},
    )

    # Attempt to delete the audit record
    stmt = delete(AuditLog).where(AuditLog.id == record.id)
    with pytest.raises(DBAPIError) as exc_info:
        await db_session.execute(stmt)
        await db_session.commit()

    assert "Audit log is append-only" in str(exc_info.value)
    await db_session.rollback()


@pytest.mark.asyncio
async def test_trade_journal_update_and_delete_blocked(db_session: AsyncSession) -> None:
    """Verify trade_journal triggers abort UPDATE and DELETE operations."""
    journal_entry = TradeJournal(
        author_type="You",
        note="Initial entry: Long trade taken after EMA cross.",
        profile_id="gold_trend_v1",
    )
    db_session.add(journal_entry)
    await db_session.commit()
    await db_session.refresh(journal_entry)
    entry_id = journal_entry.id

    # Attempt UPDATE
    update_stmt = (
        update(TradeJournal).where(TradeJournal.id == entry_id).values(note="Tampered note")
    )
    with pytest.raises(DBAPIError) as exc_info:
        await db_session.execute(update_stmt)
        await db_session.commit()
    assert "Trade journal is append-only" in str(exc_info.value)
    await db_session.rollback()

    # Attempt DELETE
    delete_stmt = delete(TradeJournal).where(TradeJournal.id == entry_id)
    with pytest.raises(DBAPIError) as exc_info:
        await db_session.execute(delete_stmt)
        await db_session.commit()
    assert "Trade journal is append-only" in str(exc_info.value)
    await db_session.rollback()
