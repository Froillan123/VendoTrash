from sqlalchemy.orm import Session
from db import get_db
from models import User
from utils import verify_password, create_access_token
from schemas import LoginResponse, UserResponse


def login_user(data: dict):
    """Login user - business logic
    
    Returns LoginResponse with appropriate message for error handling.
    Route handler will convert messages to proper HTTP status codes.
    """
    db = next(get_db())
    
    try:
        user = db.query(User).filter(User.email == data["email"]).first()
        
        if not user:
            return LoginResponse(
                message="User not found",
                access_token="",
                user=None
            )
        
        if not verify_password(data["password"], user.hashed_password):
            return LoginResponse(
                message="Wrong password",
                access_token="",
                user=None
            )
        
        if not user.is_active:
            return LoginResponse(
                message="User is inactive",
                access_token="",
                user=None
            )
        
        # Create JWT token
        access_token = create_access_token(data={"sub": user.id})
        
        return LoginResponse(
            message="Login successful",
            access_token=access_token,
            token_type="bearer",
            user=UserResponse.model_validate(user)
        )
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Login error: {str(e)}")
        return LoginResponse(
            message="Internal server error",
            access_token="",
            user=None
        )

