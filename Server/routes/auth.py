from fastapi import APIRouter, Depends
from schemas import LoginRequest, LoginResponse
from controllers.auth_controller import login_user

router = APIRouter()


@router.post("/login", response_model=LoginResponse)
def login(data: LoginRequest):
    """Login endpoint"""
    return login_user(data.dict())

