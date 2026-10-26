"""Database engine configuration, WAL mode pragma, and append-only trigger installation."""

from pathlib import Path
from typing import Any

from sqlalchemy import event, text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from engine.core.config import get_settings
from engine.storage.models import Base

# DDL Triggers enforcing append-only immutability in SQLite
TRIGGERS = [
    """
    CREATE TRIGGER IF NOT EXISTS audit_log_no_update
    BEFORE UPDATE ON audit_log
    BEGIN
        SELECT RAISE(ABORT, 'Audit log is append-only: UPDATE operations are strictly prohibited');
    END;
    """,
    """
    CREATE TRIGGER IF NOT EXISTS audit_log_no_delete
    BEFORE DELETE ON audit_log
    BEGIN
        SELECT RAISE(ABORT, 'Audit log is append-only: DELETE operations are strictly prohibited');
    END;
    """,
    """
    CREATE TRIGGER IF NOT EXISTS trade_journal_no_update
    BEFORE UPDATE ON trade_journal
    BEGIN
        SELECT RAISE(ABORT, 'Trade journal is append-only: UPDATE operations are strictly prohibited');
    END;
    """,
    """
    CREATE TRIGGER IF NOT EXISTS trade_journal_no_delete
    BEFORE DELETE ON trade_journal
    BEGIN
        SELECT RAISE(ABORT, 'Trade journal is append-only: DELETE operations are strictly prohibited');
    END;
    """,
]


def create_engine(database_url: str | None = None) -> AsyncEngine:
    """Create and configure an async SQLAlchemy engine with SQLite pragmas."""
    url = database_url or get_settings().database_url

    # Ensure local directory exists for file-based SQLite databases
    if "sqlite" in url and ":///" in url and not url.endswith(":memory:"):
        db_path = url.split(":///", 1)[1]
        parent_dir = Path(db_path).parent
        if parent_dir and not parent_dir.exists():
            parent_dir.mkdir(parents=True, exist_ok=True)

    engine = create_async_engine(
        url,
        echo=False,
        future=True,
    )

    # Enable WAL mode and foreign keys for SQLite connections
    if "sqlite" in url:
        @event.listens_for(engine.sync_engine, "connect")
        def set_sqlite_pragma(dbapi_connection: Any, connection_record: Any) -> None:
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA journal_mode=WAL;")
            cursor.execute("PRAGMA foreign_keys=ON;")
            cursor.close()

    return engine


async def init_db(engine: AsyncEngine) -> None:
    """Initialize database tables and register SQLite append-only triggers."""
    async with engine.begin() as conn:
        # Create all declared tables
        await conn.run_sync(Base.metadata.create_all)

        # Install SQLite immutability triggers
        for trigger_sql in TRIGGERS:
            await conn.execute(text(trigger_sql.strip()))


def get_session_factory(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    """Create an async session maker bound to the given engine."""
    return async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
    )
