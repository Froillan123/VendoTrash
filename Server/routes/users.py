from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from db import get_db
from dependencies import get_current_user, get_admin_user
from models import User
from schemas import UserCreate, UserResponse, UserCreateResponse, PaginatedResponse
from controllers.user_controller import create_user, get_user_by_id, get_all_users
from utils import create_access_token

router = APIRouter()


@router.post("/", response_model=UserCreateResponse)
def create_user_route(user_data: UserCreate, db: Session = Depends(get_db)):
    """Create a new user (registration - auto-login after registration)"""
    result = create_user(user_data.model_dump(), db)
    
    # Check if there was an error
    if isinstance(result, dict) and "error" in result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["error"]
        )
    
    # Create JWT token for auto-login
    access_token = create_access_token(data={"sub": result.id})
    
    return UserCreateResponse(
        message="Registration successful",
        access_token=access_token,
        token_type="bearer",
        user=result
    )


@router.get("/me", response_model=UserResponse)
def get_current_user_route(current_user: User = Depends(get_current_user)):
    """Get current authenticated user"""
    return UserResponse.model_validate(current_user)


@router.get("/", response_model=PaginatedResponse[UserResponse])
def get_all_users_route(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=1000),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all users (admin only) with pagination"""
    # Only admin can view all users
    if current_user.role != 'admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    return get_all_users(db, skip, limit)


@router.get("/{user_id}", response_model=UserResponse)
def get_user_route(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user by ID (requires authentication)"""
    # Users can only view their own profile unless admin
    if current_user.id != user_id and current_user.role != 'admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this user"
        )
    
    result = get_user_by_id(user_id, db)
    
    # Check for errors
    if isinstance(result, dict) and "error" in result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=result["error"]
        )
    
    return result


@router.post("/admin", response_model=UserCreateResponse)
def create_admin_user_route(
    user_data: UserCreate,
    current_user: User = Depends(get_admin_user),  # Only admins can create admins
    db: Session = Depends(get_db)
):
    """Create a new admin user (admin only)"""
    # Force admin role for this endpoint
    user_dict = user_data.model_dump()
    user_dict["role"] = "admin"
    
    result = create_user(user_dict, db)
    
    # Check if there was an error
    if isinstance(result, dict) and "error" in result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["error"]
        )
    
    # Create JWT token for auto-login (optional - admin might not want to auto-login)
    access_token = create_access_token(data={"sub": result.id})
    
    return UserCreateResponse(
        message="Admin user created successfully",
        access_token=access_token,
        token_type="bearer",
        user=result
    )

