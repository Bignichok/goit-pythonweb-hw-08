"""Integration tests for contacts endpoints."""

import pytest
from datetime import date, timedelta
from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.contact import Contact
from app.core.config import settings

API_PREFIX = settings.API_V1_STR


@pytest.mark.asyncio
async def test_create_contact(client: AsyncClient, db: AsyncSession, auth_token: str):
    """Test creating a new contact."""
    contact_data = {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@example.com",
        "phone": "+1234567890",
        "birthday": "1990-01-01",
        "additional_data": "Test contact"
    }
    
    response = await client.post(
        f"{API_PREFIX}/contacts/",
        json=contact_data,
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == status.HTTP_201_CREATED
    
    data = response.json()
    assert data["first_name"] == contact_data["first_name"]
    assert data["last_name"] == contact_data["last_name"]
    assert data["email"] == contact_data["email"]
    assert data["phone"] == contact_data["phone"]
    assert data["birthday"] == contact_data["birthday"]
    assert data["additional_data"] == contact_data["additional_data"]
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data


@pytest.mark.asyncio
async def test_get_contacts(client: AsyncClient, db: AsyncSession, auth_token: str):
    """Test getting all contacts."""
    response = await client.get(
        f"{API_PREFIX}/contacts/",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_get_contact(client: AsyncClient, db: AsyncSession, auth_token: str, test_contact: Contact):
    """Test getting a specific contact."""
    response = await client.get(
        f"{API_PREFIX}/contacts/{test_contact.id}",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    
    data = response.json()
    assert data["id"] == test_contact.id
    assert data["first_name"] == test_contact.first_name
    assert data["last_name"] == test_contact.last_name
    assert data["email"] == test_contact.email


@pytest.mark.asyncio
async def test_update_contact(client: AsyncClient, db: AsyncSession, auth_token: str, test_contact: Contact):
    """Test updating a contact."""
    update_data = {
        "first_name": "Updated",
        "last_name": "Name",
        "email": "updated@example.com"
    }
    
    response = await client.put(
        f"{API_PREFIX}/contacts/{test_contact.id}",
        json=update_data,
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    
    data = response.json()
    assert data["first_name"] == update_data["first_name"]
    assert data["last_name"] == update_data["last_name"]
    assert data["email"] == update_data["email"]


@pytest.mark.asyncio
async def test_delete_contact(client: AsyncClient, db: AsyncSession, auth_token: str, test_contact: Contact):
    """Test deleting a contact."""
    response = await client.delete(
        f"{API_PREFIX}/contacts/{test_contact.id}",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    
    # Verify contact is deleted
    get_response = await client.get(
        f"{API_PREFIX}/contacts/{test_contact.id}",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert get_response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_search_contacts(client: AsyncClient, db: AsyncSession, auth_token: str, test_contact: Contact):
    """Test searching contacts."""
    response = await client.get(
        f"{API_PREFIX}/contacts/?search={test_contact.first_name}",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert any(contact["id"] == test_contact.id for contact in data)


@pytest.mark.asyncio
async def test_get_upcoming_birthdays(client: AsyncClient, db: AsyncSession, auth_token: str):
    """Test getting contacts with upcoming birthdays."""
    # Create a contact with birthday in 3 days
    tomorrow = date.today() + timedelta(days=3)
    contact_data = {
        "first_name": "Birthday",
        "last_name": "Person",
        "email": "birthday@example.com",
        "phone": "+1234567890",
        "birthday": tomorrow.isoformat(),
    }
    
    create_response = await client.post(
        f"{API_PREFIX}/contacts/",
        json=contact_data,
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert create_response.status_code == status.HTTP_201_CREATED
    
    response = await client.get(
        f"{API_PREFIX}/contacts/birthdays/upcoming",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert any(contact["email"] == contact_data["email"] for contact in data) 