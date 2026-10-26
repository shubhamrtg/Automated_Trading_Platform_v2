"""Pytest fixtures for database engines, sessions, and test configurations."""

from collections.abc import AsyncGenerator

import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession

from engine.storage.db import create_engine, get_session_factory, init_db


@pytest_asyncio.fixture
async def test_engine() -> AsyncGenerator[AsyncEngine, None]:
    """Provide an isolated in-memory SQLite engine for each test."""
    engine = create_engine("sqlite+aiosqlite:///:memory:")
    await init_db(engine)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(test_engine: AsyncEngine) -> AsyncGenerator[AsyncSession, None]:
    """Provide an async database session for testing."""
    session_factory = get_session_factory(test_engine)
    async with session_factory() as session:
        yield session
