from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db import get_db
from schemas import UserCreate, UserResponse
from controllers.user_controller import create_user, get_user_by_id

router = APIRouter()


@router.post("/", response_model=UserResponse)
def create_user_route(user_data: UserCreate, db: Session = Depends(get_db)):
    """Create a new user"""
    return create_user(user_data.dict(), db)


@router.get("/{user_id}", response_model=UserResponse)
def get_user_route(user_id: int, db: Session = Depends(get_db)):
    """Get user by ID"""
    return get_user_by_id(user_id, db)

