"""Contact management endpoints.

This module provides endpoints for managing contacts, including CRUD operations,
search, and birthday tracking.
"""

import logging
from datetime import date, timedelta
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.core.auth import get_current_active_user
from app.core.database import get_db
from app.models import contact as models
from app.models.user import User
from app.schemas import contact as schemas

router = APIRouter()


@router.post("/", response_model=schemas.Contact, status_code=201)
def create_contact(
    contact: schemas.ContactCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Create a new contact.
    
    Args:
        contact (ContactCreate): Contact data to create.
        db (Session): Database session.
        current_user (User): Authenticated user.
        
    Returns:
        Contact: Created contact data.
        
    Raises:
        HTTPException: If contact with same email already exists.
    """
    # Check if contact with same email already exists for this user
    existing_contact = (
        db.query(models.Contact)
        .filter(
            models.Contact.email == contact.email,
            models.Contact.owner_id == current_user.id,
        )
        .first()
    )

    if existing_contact:
        raise HTTPException(
            status_code=400, detail="Contact with this email already exists"
        )

    db_contact = models.Contact(**contact.model_dump(), owner_id=current_user.id)
    db.add(db_contact)
    db.commit()
    db.refresh(db_contact)
    return db_contact


@router.get("/", response_model=List[schemas.Contact])
def read_contacts(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get list of contacts with optional search and pagination.
    
    Args:
        skip (int): Number of records to skip.
        limit (int): Maximum number of records to return.
        search (Optional[str]): Search term for filtering contacts.
        db (Session): Database session.
        current_user (User): Authenticated user.
        
    Returns:
        List[Contact]: List of contacts matching the criteria.
    """
    query = db.query(models.Contact).filter(models.Contact.owner_id == current_user.id)

    if search:
        query = query.filter(
            or_(
                models.Contact.first_name.ilike(f"%{search}%"),
                models.Contact.last_name.ilike(f"%{search}%"),
                models.Contact.email.ilike(f"%{search}%"),
            )
        )

    return query.offset(skip).limit(limit).all()


@router.get("/{contact_id}", response_model=schemas.Contact)
def read_contact(
    contact_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get a specific contact by ID.
    
    Args:
        contact_id (int): ID of the contact to retrieve.
        db (Session): Database session.
        current_user (User): Authenticated user.
        
    Returns:
        Contact: Contact data.
        
    Raises:
        HTTPException: If contact is not found.
    """
    db_contact = (
        db.query(models.Contact)
        .filter(
            models.Contact.id == contact_id, models.Contact.owner_id == current_user.id
        )
        .first()
    )
    if db_contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    return db_contact


@router.put("/{contact_id}", response_model=schemas.Contact)
def update_contact(
    contact_id: int,
    contact: schemas.ContactUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Update an existing contact.
    
    Args:
        contact_id (int): ID of the contact to update.
        contact (ContactUpdate): Updated contact data.
        db (Session): Database session.
        current_user (User): Authenticated user.
        
    Returns:
        Contact: Updated contact data.
        
    Raises:
        HTTPException: If contact is not found.
    """
    db_contact = (
        db.query(models.Contact)
        .filter(
            models.Contact.id == contact_id, models.Contact.owner_id == current_user.id
        )
        .first()
    )
    if db_contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")

    for key, value in contact.model_dump(exclude_unset=True).items():
        setattr(db_contact, key, value)

    db.commit()
    db.refresh(db_contact)
    return db_contact


@router.delete("/{contact_id}")
def delete_contact(
    contact_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Delete a contact.
    
    Args:
        contact_id (int): ID of the contact to delete.
        db (Session): Database session.
        current_user (User): Authenticated user.
        
    Returns:
        dict: Success message.
        
    Raises:
        HTTPException: If contact is not found.
    """
    db_contact = (
        db.query(models.Contact)
        .filter(
            models.Contact.id == contact_id, models.Contact.owner_id == current_user.id
        )
        .first()
    )
    if db_contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")

    db.delete(db_contact)
    db.commit()
    return {"message": "Contact deleted successfully"}


@router.get("/birthdays/upcoming", response_model=List[schemas.Contact])
def get_upcoming_birthdays(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)
):
    """Get contacts with birthdays in the next 7 days.
    
    Args:
        db (Session): Database session.
        current_user (User): Authenticated user.
        
    Returns:
        List[Contact]: List of contacts with upcoming birthdays.
    """
    today = date.today()
    next_week = today + timedelta(days=7)

    contacts = (
        db.query(models.Contact)
        .filter(models.Contact.owner_id == current_user.id)
        .all()
    )
    upcoming_birthdays = []

    for contact in contacts:
        # Adjust birthday to current year for comparison
        birthday_this_year = contact.birthday.replace(year=today.year)
        if birthday_this_year < today:
            birthday_this_year = birthday_this_year.replace(year=today.year + 1)

        if today <= birthday_this_year <= next_week:
            upcoming_birthdays.append(contact)

    return upcoming_birthdays
