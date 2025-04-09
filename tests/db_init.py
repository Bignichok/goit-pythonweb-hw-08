"""Test database initialization module.

This module provides functions for setting up and tearing down the test database.
"""

import asyncio
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base
from app.core.config import settings

# Create test database engine
TEST_DATABASE_URL = settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")
engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
)

# Create async session factory
async_session = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def init_db() -> None:
    """Initialize the test database by creating all tables."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


async def get_test_db() -> AsyncGenerator[AsyncSession, None]:
    """Get a test database session.
    
    Yields:
        AsyncSession: Database session for testing.
    """
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def cleanup_db() -> None:
    """Clean up the test database by dropping all tables."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


async def close_db_connections() -> None:
    """Close all database connections."""
    await engine.dispose()


# Create event loop for running async functions
def run_async(coro):
    """Run an async function in a new event loop.
    
    Args:
        coro: Async function to run.
    """
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close() 