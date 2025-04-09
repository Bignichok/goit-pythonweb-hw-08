"""Authentication and user management endpoints.

This module provides endpoints for user registration, login, email verification,
and avatar management.
"""

import logging
from datetime import timedelta

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from jose import JWTError, jwt

from app.core.auth import (
    create_access_token,
    create_refresh_token,
    get_current_active_user,
    get_password_hash,
    verify_password,
)
from app.core.cloudinary import upload_avatar
from app.core.config import settings
from app.core.database import get_db
from app.core.email import send_verification_email
from app.models.user import User
from app.schemas.auth import Token, UserCreate, UserResponse

router = APIRouter()


@router.post(
    "/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user.
    
    Args:
        user_data (UserCreate): User registration data including email and password.
        db (Session): Database session.
        
    Returns:
        UserResponse: Created user data.
        
    Raises:
        HTTPException: If email is already registered.
    """
    # Check if user already exists
    db_user = db.query(User).filter(User.email == user_data.email).first()
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
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

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
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    """Authenticate user and return access tokens.
    
    Args:
        form_data (OAuth2PasswordRequestForm): Login credentials.
        db (Session): Database session.
        
    Returns:
        Token: Access and refresh tokens.
        
    Raises:
        HTTPException: If credentials are invalid.
    """
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(
        data={"sub": user.email},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    refresh_token = create_refresh_token(data={"sub": user.email})

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.get("/verify-email/{token}")
async def verify_email(token: str, db: Session = Depends(get_db)):
    """Verify user's email address using verification token.
    
    Args:
        token (str): Email verification token.
        db (Session): Database session.
        
    Returns:
        dict: Success message.
        
    Raises:
        HTTPException: If token is invalid, expired, or user not found.
    """
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid verification token: missing email",
            )
            
        # Find user by email
        user = db.query(User).filter(User.email == email).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )
            
        # Check if already verified
        if user.is_verified:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already verified",
            )
            
        # Update user verification status
        user.is_verified = True
        db.commit()
        
        return {"message": "Email verified successfully"}
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Verification token has expired",
        )
    except jwt.JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid verification token: {str(e)}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred during email verification: {str(e)}",
        )


@router.post("/avatar", response_model=UserResponse)
async def update_avatar(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Update user's avatar.
    
    Args:
        file (UploadFile): Image file to upload.
        current_user (User): Authenticated user.
        db (Session): Database session.
        
    Returns:
        UserResponse: Updated user data with new avatar URL.
        
    Raises:
        HTTPException: If file upload fails.
    """
    avatar_url = await upload_avatar(file)
    current_user.avatar = avatar_url
    db.commit()
    db.refresh(current_user)
    return current_user


@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    """Get current user's profile.
    
    Args:
        current_user (User): Authenticated user.
        
    Returns:
        UserResponse: Current user's data.
    """
    return current_user
