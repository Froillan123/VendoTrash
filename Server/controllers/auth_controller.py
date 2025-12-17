from sqlalchemy.orm import Session
from db import get_db
from models import User
from utils import verify_password
from schemas import LoginResponse, UserResponse


def login_user(data: dict):
    """Login user - business logic"""
    db = next(get_db())
    
    user = db.query(User).filter(User.email == data["email"]).first()
    
    if not user:
        return LoginResponse(message="User not found")
    
    if not verify_password(data["password"], user.hashed_password):
        return LoginResponse(message="Wrong password")
    
    if not user.is_active:
        return LoginResponse(message="User is inactive")
    
    return LoginResponse(
        message="Login successful",
        user=UserResponse.model_validate(user)
    )

