"""Contact management endpoints.

This module provides endpoints for managing contacts, including CRUD operations,
search, and birthday tracking.
"""

import logging
from datetime import date, timedelta
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_active_user
from app.core.database import get_db
from app.models import contact as models
from app.models.user import User
from app.schemas import contact as schemas

router = APIRouter()


@router.post("/", response_model=schemas.Contact, status_code=201)
async def create_contact(
    contact: schemas.ContactCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Create a new contact.
    
    Args:
        contact (ContactCreate): Contact data to create.
        db (AsyncSession): Database session.
        current_user (User): Authenticated user.
        
    Returns:
        Contact: Created contact data.
        
    Raises:
        HTTPException: If contact with same email already exists.
    """
    # Check if contact with same email already exists for this user
    stmt = select(models.Contact).where(
        models.Contact.email == contact.email,
        models.Contact.user_id == current_user.id,
    )
    result = await db.execute(stmt)
    existing_contact = result.scalar_one_or_none()

    if existing_contact:
        raise HTTPException(
            status_code=400, detail="Contact with this email already exists"
        )

    db_contact = models.Contact(**contact.model_dump(), user_id=current_user.id)
    db.add(db_contact)
    await db.commit()
    await db.refresh(db_contact)
    return db_contact


@router.get("/", response_model=List[schemas.Contact])
async def read_contacts(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get list of contacts with optional search and pagination.
    
    Args:
        skip (int): Number of records to skip.
        limit (int): Maximum number of records to return.
        search (Optional[str]): Search term for filtering contacts.
        db (AsyncSession): Database session.
        current_user (User): Authenticated user.
        
    Returns:
        List[Contact]: List of contacts matching the criteria.
    """
    stmt = select(models.Contact).where(models.Contact.user_id == current_user.id)

    if search:
        stmt = stmt.where(
            or_(
                models.Contact.first_name.ilike(f"%{search}%"),
                models.Contact.last_name.ilike(f"%{search}%"),
                models.Contact.email.ilike(f"%{search}%"),
            )
        )

    stmt = stmt.offset(skip).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.get("/{contact_id}", response_model=schemas.Contact)
async def read_contact(
    contact_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get a specific contact by ID.
    
    Args:
        contact_id (int): ID of the contact to retrieve.
        db (AsyncSession): Database session.
        current_user (User): Authenticated user.
        
    Returns:
        Contact: Contact data.
        
    Raises:
        HTTPException: If contact is not found.
    """
    stmt = select(models.Contact).where(
        models.Contact.id == contact_id,
        models.Contact.user_id == current_user.id,
    )
    result = await db.execute(stmt)
    db_contact = result.scalar_one_or_none()
    
    if db_contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    return db_contact


@router.put("/{contact_id}", response_model=schemas.Contact)
async def update_contact(
    contact_id: int,
    contact: schemas.ContactUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Update an existing contact.
    
    Args:
        contact_id (int): ID of the contact to update.
        contact (ContactUpdate): Updated contact data.
        db (AsyncSession): Database session.
        current_user (User): Authenticated user.
        
    Returns:
        Contact: Updated contact data.
        
    Raises:
        HTTPException: If contact is not found.
    """
    stmt = select(models.Contact).where(
        models.Contact.id == contact_id,
        models.Contact.user_id == current_user.id,
    )
    result = await db.execute(stmt)
    db_contact = result.scalar_one_or_none()
    
    if db_contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")

    for key, value in contact.model_dump(exclude_unset=True).items():
        setattr(db_contact, key, value)

    await db.commit()
    await db.refresh(db_contact)
    return db_contact


@router.delete("/{contact_id}")
async def delete_contact(
    contact_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Delete a contact.
    
    Args:
        contact_id (int): ID of the contact to delete.
        db (AsyncSession): Database session.
        current_user (User): Authenticated user.
        
    Returns:
        dict: Success message.
        
    Raises:
        HTTPException: If contact is not found.
    """
    stmt = select(models.Contact).where(
        models.Contact.id == contact_id,
        models.Contact.user_id == current_user.id,
    )
    result = await db.execute(stmt)
    db_contact = result.scalar_one_or_none()
    
    if db_contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")

    await db.delete(db_contact)
    await db.commit()
    return {"message": "Contact deleted successfully"}


@router.get("/birthdays/upcoming", response_model=List[schemas.Contact])
async def get_upcoming_birthdays(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get contacts with birthdays in the next 7 days.
    
    Args:
        db (AsyncSession): Database session.
        current_user (User): Authenticated user.
        
    Returns:
        List[Contact]: List of contacts with upcoming birthdays.
    """
    today = date.today()
    next_week = today + timedelta(days=7)

    stmt = select(models.Contact).where(models.Contact.user_id == current_user.id)
    result = await db.execute(stmt)
    contacts = result.scalars().all()
    
    upcoming_birthdays = []

    for contact in contacts:
        # Adjust birthday to current year for comparison
        birthday_this_year = contact.birthday.replace(year=today.year)
        if birthday_this_year < today:
            birthday_this_year = birthday_this_year.replace(year=today.year + 1)

        if today <= birthday_this_year <= next_week:
            upcoming_birthdays.append(contact)

    return upcoming_birthdays
