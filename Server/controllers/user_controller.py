from sqlalchemy.orm import Session
from models import User
from utils import hash_password
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
    new_user = User(
        email=data["email"],
        username=data["username"],
        hashed_password=hash_password(data["password"]),
        is_active=True
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

