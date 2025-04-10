"""Authentication and user management endpoints.

This module provides endpoints for user registration, login, email verification,
and avatar management.
"""

import logging
from datetime import timedelta

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from jose import JWTError, jwt

from app.core.auth import (
    create_access_token,
    create_refresh_token,
    get_current_active_user,
    get_password_hash,
    verify_password,
    oauth2_scheme,
)
from app.core.cloudinary import upload_avatar
from app.core.config import settings
from app.core.database import get_db
from app.core.email import send_verification_email, send_password_reset_email
from app.models.user import User
from app.schemas.auth import Token, UserCreate, UserResponse, PasswordReset, PasswordResetConfirmResponse, PasswordResetRequest, PasswordResetResponse
from app.core.security import get_current_admin_user

router = APIRouter()


@router.post(
    "/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
async def register(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    """Register a new user.
    
    Args:
        user_data (UserCreate): User registration data including email, password, and role.
        db (AsyncSession): Database session.
        
    Returns:
        UserResponse: Created user data.
        
    Raises:
        HTTPException: If email is already registered.
    """
    # Check if user already exists
    result = await db.execute(select(User).where(User.email == user_data.email))
    db_user = result.scalar_one_or_none()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Email already registered"
        )

    # Create new user
    hashed_password = get_password_hash(user_data.password)
    db_user = User(
        email=user_data.email,
        hashed_password=hashed_password,
        is_verified=True,  # Auto-verify in development
        role=user_data.role,
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)

    # Try to send verification email, but don't fail if it doesn't work
    try:
        verification_token = create_access_token(
            data={"sub": user_data.email}, expires_delta=timedelta(days=1)
        )
        send_verification_email(user_data.email, verification_token)
        logging.info(f"Verification email sent to {user_data.email}")
    except Exception as e:
        logging.warning(f"Failed to send verification email: {e}")
        # Continue without verification in development

    return db_user


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)
):
    """Authenticate user and return access tokens.
    
    Args:
        form_data (OAuth2PasswordRequestForm): Login credentials.
        db (AsyncSession): Database session.
        
    Returns:
        Token: Access and refresh tokens.
        
    Raises:
        HTTPException: If credentials are invalid.
    """
    result = await db.execute(select(User).where(User.email == form_data.username))
    user = result.scalar_one_or_none()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": user.email})
    refresh_token = create_refresh_token(data={"sub": user.email})
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.get("/verify-email/{token}")
async def verify_email(token: str, db: AsyncSession = Depends(get_db)):
    """Verify user email using token.
    
    Args:
        token (str): Verification token.
        db (AsyncSession): Database session.
        
    Returns:
        dict: Success message.
        
    Raises:
        HTTPException: If token is invalid or expired.
    """
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid verification token",
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid verification token",
        )

    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    user.is_verified = True
    await db.commit()
    return {"message": "Email verified successfully"}


@router.post("/avatar", response_model=UserResponse)
async def update_avatar(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """Update user avatar. Only admin users can update their avatar.
    
    Args:
        file (UploadFile): Avatar image file.
        current_user (User): Current authenticated admin user.
        db (AsyncSession): Database session.
        
    Returns:
        UserResponse: Updated user data.
    """
    avatar_url = await upload_avatar(file)
    current_user.avatar = avatar_url
    await db.commit()
    await db.refresh(current_user)
    return current_user


@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    """Get current user information.
    
    Args:
        current_user (User): Current authenticated user.
        
    Returns:
        UserResponse: Current user data.
    """
    return current_user


@router.post("/refresh", response_model=Token)
async def refresh_token(
    token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)
):
    """Refresh access token using refresh token.
    
    Args:
        token (str): Refresh token.
        db (AsyncSession): Database session.
        
    Returns:
        Token: New access and refresh tokens.
        
    Raises:
        HTTPException: If token is invalid or expired.
    """
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": user.email})
    refresh_token = create_refresh_token(data={"sub": user.email})
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.post("/request-password-reset", response_model=PasswordResetResponse)
async def request_password_reset(
    reset_request: PasswordResetRequest,
    db: AsyncSession = Depends(get_db),
):
    """Request password reset by email."""
    # Get user from database
    stmt = select(User).where(User.email == reset_request.email)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        # Return success even if user doesn't exist to prevent email enumeration
        return PasswordResetResponse()

    # Create reset token
    reset_token = create_access_token(
        data={"sub": user.email},
        expires_delta=timedelta(minutes=60),  # 1 hour expiration
    )

    # Send reset email
    await send_password_reset_email(
        email=user.email,
        reset_token=reset_token,
    )

    return PasswordResetResponse()


@router.post("/reset-password", response_model=PasswordResetConfirmResponse)
async def reset_password(
    reset_data: PasswordReset,
    db: AsyncSession = Depends(get_db),
):
    """Reset password using reset token."""
    try:
        # Verify reset token
        payload = jwt.decode(
            reset_data.token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid reset token",
            )

        # Get user from database
        stmt = select(User).where(User.email == email)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()

        if user is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User not found",
            )

        # Update password
        user.hashed_password = get_password_hash(reset_data.new_password)
        await db.commit()

        return PasswordResetConfirmResponse()

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token",
        )
