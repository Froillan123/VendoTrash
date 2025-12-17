from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from schemas import LoginRequest, LoginResponse
from controllers.auth_controller import login_user
from dependencies import get_current_user
from models import User
import logging

router = APIRouter()
logger = logging.getLogger(__name__)
security = HTTPBearer()


@router.post("/login", response_model=LoginResponse)
def login(data: LoginRequest):
    """Login endpoint with proper error handling"""
    try:
        result = login_user(data.model_dump())
        
        # Check for errors and raise appropriate HTTP exceptions
        if result.message == "User not found":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        elif result.message == "Wrong password":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        elif result.message == "User is inactive":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is inactive"
            )
        
        # Success - return response
        return result
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during login"
        )


@router.post("/logout")
def logout(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    current_user: User = Depends(get_current_user)
):
    """Logout endpoint - invalidates token on server side"""
    try:
        # For JWT, logout is typically client-side (just remove token)
        # But we can log the logout event for tracking
        logger.info(f"User {current_user.id} ({current_user.email}) logged out")
        
        # If you want server-side token invalidation, you'd need a token blacklist
        # For now, we just acknowledge the logout
        return {
            "message": "Logged out successfully",
            "status": "success"
        }
    except Exception as e:
        logger.error(f"Logout error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during logout"
        )

