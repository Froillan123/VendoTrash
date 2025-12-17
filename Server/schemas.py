from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional
from datetime import datetime


# User Schemas
class UserBase(BaseModel):
    """Base user schema"""
    email: EmailStr
    username: str


class UserCreate(UserBase):
    """Schema for creating a user"""
    password: str


class UserResponse(UserBase):
    """Schema for user response"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    is_active: bool
    created_at: datetime


# Booking Schemas
class BookingBase(BaseModel):
    """Base booking schema"""
    title: str
    description: Optional[str] = None


class BookingCreate(BookingBase):
    """Schema for creating a booking"""
    user_id: int


class BookingResponse(BookingBase):
    """Schema for booking response"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    user_id: int
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None


# Auth Schemas
class LoginRequest(BaseModel):
    """Schema for login request"""
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    """Schema for login response"""
    message: str
    user: Optional[UserResponse] = None

