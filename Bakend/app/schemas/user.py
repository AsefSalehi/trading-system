from typing import Optional
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime

from app.models.user import UserRole


# Shared properties
class UserBase(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    full_name: Optional[str] = None
    role: UserRole = UserRole.VIEWER
    is_active: bool = True


# Properties to receive via API on creation
class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=100)


# Properties to receive via API on update
class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    full_name: Optional[str] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None
    password: Optional[str] = Field(None, min_length=8, max_length=100)


# Properties to return via API
class User(UserBase):
    id: int
    is_verified: bool
    created_at: datetime
    updated_at: Optional[datetime]
    last_login: Optional[datetime]

    class Config:
        from_attributes = True


# Properties for login
class UserLogin(BaseModel):
    username: str
    password: str


# Token schemas
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class TokenData(BaseModel):
    username: Optional[str] = None
    user_id: Optional[int] = None
    role: Optional[UserRole] = None
