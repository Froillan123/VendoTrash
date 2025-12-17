from sqlalchemy.orm import Session
from sqlalchemy import func
from models import User
from utils import hash_password, create_access_token
from schemas import UserResponse


def create_user(data: dict, db: Session):
    """Create a new user - business logic"""
    # Check if user exists
    existing_user = db.query(User).filter(
        (User.email == data["email"]) | (User.username == data["username"])
    ).first()
    
    if existing_user:
        if existing_user.email == data["email"]:
            return {"error": "Email already exists"}
        return {"error": "Username already exists"}
    
    # Create new user
    # Only allow customer role during registration (admin role must be set by existing admin)
    role = data.get("role", "customer")
    # Force customer role for public registration - admins must be created by existing admins
    if role != "customer":
        role = "customer"
    
    new_user = User(
        email=data["email"],
        username=data["username"],
        hashed_password=hash_password(data["password"]),
        role=role,
        is_active=True,
        total_points=0,
        total_plastic=0,
        total_metal=0,
        total_transactions=0
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return UserResponse.model_validate(new_user)


def get_user_by_id(user_id: int, db: Session):
    """Get user by ID - business logic"""
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        return {"error": "User not found"}
    
    return UserResponse.model_validate(user)


def get_all_users(db: Session, skip: int = 0, limit: int = 100):
    """Get all users - business logic (admin only)"""
    users = db.query(User).order_by(User.created_at.desc()).offset(skip).limit(limit).all()
    total = db.query(func.count(User.id)).scalar()
    return {
        "items": [UserResponse.model_validate(u) for u in users],
        "total": total,
        "skip": skip,
        "limit": limit,
        "has_more": (skip + limit) < total
    }

