import pytest
from datetime import datetime, timedelta, UTC
from unittest.mock import MagicMock, patch, AsyncMock
from fastapi import HTTPException
from jose import jwt
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.auth import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    get_current_user,
    get_current_active_user
)
from app.models.user import User
from app.core.config import settings

@pytest.fixture
def mock_user() -> User:
    """Create a mock user for testing."""
    return User(
        id=1,
        email="test@example.com",
        hashed_password="hashed_password",
        is_active=True,
        is_verified=True,
        created_at=datetime.now(UTC)
    )

@pytest.fixture
def mock_db() -> AsyncSession:
    """Create a mock database session."""
    mock = AsyncMock(spec=AsyncSession)
    mock.execute.return_value = MagicMock(scalar_one_or_none=lambda: None)
    return mock

def test_verify_password():
    """Test password verification functionality."""
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    plain_password = "test_password"
    hashed_password = pwd_context.hash(plain_password)
    
    assert verify_password(plain_password, hashed_password) is True
    assert verify_password("wrong_password", hashed_password) is False

def test_get_password_hash():
    """Test password hashing functionality."""
    password = "test_password"
    hashed_password = get_password_hash(password)
    assert hashed_password != password
    assert len(hashed_password) > 0

def test_create_access_token():
    """Test access token creation."""
    data = {"sub": "test@example.com"}
    expires_delta = timedelta(minutes=30)
    token = create_access_token(data, expires_delta)
    
    decoded = jwt.decode(
        token,
        settings.SECRET_KEY,
        algorithms=[settings.ALGORITHM]
    )
    
    assert decoded["sub"] == data["sub"]
    assert "exp" in decoded

def test_create_refresh_token():
    """Test refresh token creation."""
    data = {"sub": "test@example.com"}
    expires_delta = timedelta(days=7)
    token = create_refresh_token(data, expires_delta)
    
    decoded = jwt.decode(
        token,
        settings.SECRET_KEY,
        algorithms=[settings.ALGORITHM]
    )
    
    assert decoded["sub"] == data["sub"]
    assert "exp" in decoded

@pytest.mark.asyncio
async def test_get_current_user_invalid_token(mock_db):
    """Test getting current user with invalid token."""
    with pytest.raises(HTTPException) as exc_info:
        await get_current_user("invalid_token", mock_db)
    
    assert exc_info.value.status_code == 401
    assert "Could not validate credentials" in str(exc_info.value.detail)

@pytest.mark.asyncio
async def test_get_current_active_user_active(mock_user):
    """Test getting current active user with active user."""
    result = await get_current_active_user(mock_user)
    assert result == mock_user

@pytest.mark.asyncio
async def test_get_current_active_user_inactive():
    """Test getting current active user with inactive user."""
    inactive_user = User(
        id=1,
        email="test@example.com",
        hashed_password="hashed_password",
        is_active=False,
        is_verified=True,
        created_at=datetime.now(UTC)
    )
    
    with pytest.raises(HTTPException) as exc_info:
        await get_current_active_user(inactive_user)
    
    assert exc_info.value.status_code == 400
    assert "Inactive user" in str(exc_info.value.detail) 