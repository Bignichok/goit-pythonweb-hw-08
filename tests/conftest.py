"""Test configuration and fixtures.

This module provides test configuration and fixtures for the test suite.
"""

import pytest
import pytest_asyncio
from typing import AsyncGenerator, Generator
from datetime import datetime, UTC, date

from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from httpx import AsyncClient
from fastapi import FastAPI
from sqlalchemy import select

from app.main import app
from app.core.database import Base, get_db
from app.core.config import settings
from app.models.user import User
from app.models.contact import Contact

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


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create an event loop for the test session."""
    import asyncio
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session", autouse=True)
async def setup_database() -> None:
    """Set up the test database before running tests."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture
async def db() -> AsyncGenerator[AsyncSession, None]:
    """Get a test database session."""
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


@pytest_asyncio.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    """Create a test client for the FastAPI app."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


@pytest_asyncio.fixture
async def test_user(db: AsyncSession) -> User:
    """Create a test user for authentication."""
    email = "test@example.com"
    # First check if user exists
    stmt = select(User).where(User.email == email)
    result = await db.execute(stmt)
    existing_user = result.scalar_one_or_none()
    
    if existing_user:
        return existing_user
        
    user = User(
        email=email,
        hashed_password="$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # "password123"
        is_active=True,
        is_verified=True,
        created_at=datetime.now(UTC)
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@pytest_asyncio.fixture
async def auth_token(test_user: User) -> str:
    """Get an authentication token for the test user."""
    from app.core.auth import create_access_token
    token = create_access_token(data={"sub": test_user.email})
    return token


@pytest_asyncio.fixture
async def test_contact(db: AsyncSession, test_user: User) -> Contact:
    """Create a test contact."""
    contact = Contact(
        first_name="Test",
        last_name="User",
        email="test.contact@example.com",
        phone="+1234567890",
        birthday=date(1990, 1, 1),
        user_id=test_user.id
    )
    db.add(contact)
    await db.commit()  # Ensure contact is committed to database
    await db.refresh(contact)
    return contact


@pytest_asyncio.fixture(autouse=True)
async def clean_tables(db: AsyncSession):
    """Clean all tables after each test."""
    try:
        yield
    finally:
        # Delete all contacts first (due to foreign key constraints)
        await db.execute(Contact.__table__.delete())
        # Then delete all users
        await db.execute(User.__table__.delete())
        await db.commit() 