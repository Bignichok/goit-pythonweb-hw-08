"""Integration tests for authentication endpoints."""

import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.schemas.auth import UserCreate, UserLogin
from app.core.config import settings

API_PREFIX = settings.API_V1_STR


@pytest.mark.asyncio
async def test_register_user(client: AsyncClient, db: AsyncSession):
    """Test user registration endpoint."""
    user_data = {
        "email": "test@example.com",
        "password": "testpassword123"
    }
    
    response = await client.post(f"{API_PREFIX}/auth/register", json=user_data)
    assert response.status_code == status.HTTP_201_CREATED
    
    data = response.json()
    assert data["email"] == user_data["email"]
    assert "id" in data
    assert "is_active" in data
    assert "is_verified" in data
    assert "created_at" in data
    assert "password" not in data


@pytest.mark.asyncio
async def test_register_duplicate_email(client: AsyncClient, db: AsyncSession):
    """Test registration with duplicate email."""
    # First registration
    user_data = {
        "email": "duplicate@example.com",
        "password": "testpassword123"
    }
    await client.post(f"{API_PREFIX}/auth/register", json=user_data)
    
    # Second registration with same email
    response = await client.post(f"{API_PREFIX}/auth/register", json=user_data)
    assert response.status_code == status.HTTP_409_CONFLICT
    assert response.json()["detail"] == "Email already registered"


@pytest.mark.asyncio
async def test_login_user(client: AsyncClient, db: AsyncSession):
    """Test user login endpoint."""
    # First register a user
    user_data = {
        "email": "login@example.com",
        "password": "testpassword123"
    }
    await client.post(f"{API_PREFIX}/auth/register", json=user_data)
    
    # Then try to login
    login_data = {
        "username": user_data["email"],
        "password": user_data["password"]
    }
    response = await client.post(f"{API_PREFIX}/auth/login", data=login_data)
    assert response.status_code == status.HTTP_200_OK
    
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert "token_type" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_invalid_credentials(client: AsyncClient, db: AsyncSession):
    """Test login with invalid credentials."""
    login_data = {
        "username": "nonexistent@example.com",
        "password": "wrongpassword"
    }
    response = await client.post(f"{API_PREFIX}/auth/login", data=login_data)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Incorrect email or password"


@pytest.mark.asyncio
async def test_refresh_token(client: AsyncClient, db: AsyncSession):
    """Test token refresh endpoint."""
    # First register and login
    user_data = {
        "email": "refresh@example.com",
        "password": "testpassword123"
    }
    await client.post(f"{API_PREFIX}/auth/register", json=user_data)
    
    login_data = {
        "username": user_data["email"],
        "password": user_data["password"]
    }
    login_response = await client.post(f"{API_PREFIX}/auth/login", data=login_data)
    refresh_token = login_response.json()["refresh_token"]
    
    # Then try to refresh
    response = await client.post(
        f"{API_PREFIX}/auth/refresh",
        headers={"Authorization": f"Bearer {refresh_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert "token_type" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_get_current_user(client: AsyncClient, db: AsyncSession):
    """Test getting current user information."""
    # First register and login
    user_data = {
        "email": "current@example.com",
        "password": "testpassword123"
    }
    await client.post(f"{API_PREFIX}/auth/register", json=user_data)
    
    login_data = {
        "username": user_data["email"],
        "password": user_data["password"]
    }
    login_response = await client.post(f"{API_PREFIX}/auth/login", data=login_data)
    access_token = login_response.json()["access_token"]
    
    # Then get current user
    response = await client.get(
        f"{API_PREFIX}/auth/me",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    
    data = response.json()
    assert data["email"] == user_data["email"]
    assert "id" in data
    assert "is_active" in data
    assert "is_verified" in data
    assert "password" not in data 