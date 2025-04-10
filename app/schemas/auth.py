from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, ConfigDict


class UserBase(BaseModel):
    email: EmailStr


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)
    role: str = Field(default="user", pattern="^(user|admin)$")


class UserLogin(UserBase):
    password: str


class UserResponse(UserBase):
    id: int
    is_active: bool
    is_verified: bool
    role: str
    avatar: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None
    exp: Optional[datetime] = None


class TokenPayload(BaseModel):
    sub: str
    exp: datetime


class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordResetResponse(BaseModel):
    message: str = "Password reset email sent if the email exists"


class PasswordReset(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8)


class PasswordResetConfirmResponse(BaseModel):
    message: str = "Password has been reset successfully"
