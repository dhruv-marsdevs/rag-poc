from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List
from datetime import datetime


class UserBase(BaseModel):
    """Base user schema."""

    email: EmailStr
    is_active: bool = True
    is_superuser: bool = False
    full_name: Optional[str] = None


class UserCreate(UserBase):
    """User creation schema."""

    password: str


class UserUpdate(BaseModel):
    """User update schema."""

    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None


class UserInDBBase(UserBase):
    """User stored in DB."""

    id: str
    created_at: datetime

    class Config:
        from_attributes = True


class User(UserInDBBase):
    """User schema (returned to API)."""

    pass


class UserInDB(UserInDBBase):
    """User with password hash stored in DB."""

    hashed_password: str


class ApiKey(BaseModel):
    """API key schema."""

    id: str
    name: str
    prefix: str
    user_id: str
    created_at: datetime
    last_used: Optional[datetime] = None

    class Config:
        from_attributes = True


class ApiKeyCreate(BaseModel):
    """API key creation schema."""

    name: str = Field(..., min_length=1)


class ApiKeyResponse(BaseModel):
    """API key response with full key (only returned once)."""

    id: str
    name: str
    api_key: str
    prefix: str
    created_at: datetime


class PasswordChange(BaseModel):
    """
    Schema for password change request
    """
    current_password: str = Field(..., min_length=8)
    new_password: str = Field(..., min_length=8)
    
    class Config:
        from_attributes = True
