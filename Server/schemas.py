from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional, Generic, TypeVar, List
from datetime import datetime
import uuid

T = TypeVar('T')

class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response schema"""
    items: List[T]
    total: int
    skip: int
    limit: int
    has_more: bool


# User Schemas
class UserBase(BaseModel):
    """Base user schema"""
    email: EmailStr
    username: str
    role: str = "customer"  # admin, customer


class UserCreate(UserBase):
    """Schema for creating a user"""
    password: str
    role: str = "customer"  # Default to customer, admin can be set during registration


class UserResponse(UserBase):
    """Schema for user response"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    role: str
    is_active: bool
    total_points: int
    total_plastic: int
    total_metal: int
    total_transactions: int
    created_at: datetime


class UserCreateResponse(BaseModel):
    """Schema for user creation response with token (same as LoginResponse)"""
    message: str
    access_token: str
    token_type: str = "bearer"
    user: Optional[UserResponse] = None


class AddPointsRequest(BaseModel):
    """Schema for adding points to a user"""
    points: int


# Machine Schemas
class MachineBase(BaseModel):
    """Base machine schema"""
    name: str
    location: str


class MachineCreate(MachineBase):
    """Schema for creating a machine"""
    bin_capacity: int = 100


class MachineResponse(MachineBase):
    """Schema for machine response"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    status: str
    last_activity: datetime
    bin_capacity: int
    total_collected: int
    created_at: datetime


# Transaction Schemas
class TransactionBase(BaseModel):
    """Base transaction schema"""
    material_type: str  # PLASTIC, NON_PLASTIC


class TransactionCreate(TransactionBase):
    """Schema for creating a transaction"""
    machine_id: int
    points_earned: int
    # user_id comes from JWT token, not from request


class TransactionResponse(TransactionBase):
    """Schema for transaction response"""
    model_config = ConfigDict(from_attributes=True)
    
    id: uuid.UUID
    user_id: int
    machine_id: int
    points_earned: int
    status: str
    created_at: datetime


# Reward Schemas
class RewardBase(BaseModel):
    """Base reward schema"""
    name: str
    description: Optional[str] = None
    points_required: int
    category: str  # wifi, data, voucher


class RewardCreate(RewardBase):
    """Schema for creating a reward"""
    is_active: bool = True


class RewardResponse(RewardBase):
    """Schema for reward response"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    is_active: bool
    created_at: datetime


class RewardUpdate(BaseModel):
    """Schema for updating a reward"""
    name: Optional[str] = None
    description: Optional[str] = None
    points_required: Optional[int] = None
    category: Optional[str] = None
    is_active: Optional[bool] = None


# Redemption Schemas
class RedemptionBase(BaseModel):
    """Base redemption schema"""
    points_used: int


class RedemptionCreate(RedemptionBase):
    """Schema for creating a redemption"""
    reward_id: int
    # user_id comes from JWT token, not from request


class RedemptionResponse(RedemptionBase):
    """Schema for redemption response"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    user_id: int
    reward_id: int
    reward: Optional[RewardResponse] = None  # Include reward relationship
    status: str
    created_at: datetime


# Auth Schemas
class LoginRequest(BaseModel):
    """Schema for login request"""
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    """Schema for login response"""
    message: str
    access_token: str
    token_type: str = "bearer"
    user: Optional[UserResponse] = None


# Vendo Command Schemas
class VendoCommandRequest(BaseModel):
    """Schema for vendo command"""
    material: str  # PLASTIC, NON_PLASTIC
    action: Optional[str] = "SORT"


class VendoCommandResponse(BaseModel):
    """Schema for vendo command response"""
    status: str
    message: str
    material: Optional[str] = None


class VendoClassifyRequest(BaseModel):
    """Request schema for trash classification"""
    image_base64: Optional[str] = None  # Optional: if provided, uses it; if not, captures from webcam
    machine_id: int = 1  # Default machine


class VendoClassifyResponse(BaseModel):
    """Response schema for trash classification"""
    status: str  # success, rejected
    material_type: str  # PLASTIC, NON_PLASTIC, or REJECTED
    confidence: float
    points_earned: int
    transaction_id: Optional[str] = None  # UUID as string (None if rejected)

