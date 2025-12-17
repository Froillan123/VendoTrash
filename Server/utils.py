import hashlib
from typing import Optional
from datetime import datetime, timedelta
from jose import JWTError, jwt
from config import settings

# JWT Configuration
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30 * 24 * 60  # 30 days


def hash_password(password: str) -> str:
    """Simple password hashing (use bcrypt in production)"""
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    return hash_password(plain_password) == hashed_password


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    
    # Ensure 'sub' (subject) is a string (JWT standard requirement)
    if "sub" in to_encode:
        to_encode["sub"] = str(to_encode["sub"])
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    
    # Use secret key from settings, or fallback for development
    secret_key = settings.SECRET_KEY if settings.SECRET_KEY else "dev-secret-key-change-in-production-min-32-chars"
    
    if len(secret_key) < 16:
        import logging
        logger = logging.getLogger(__name__)
        logger.warning("SECRET_KEY is very short! Consider using at least 32 characters for production.")
        # Still use it, but warn
    
    encoded_jwt = jwt.encode(to_encode, secret_key, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> Optional[dict]:
    """Verify JWT token and return payload"""
    try:
        # Use same secret key logic as create_access_token
        secret_key = settings.SECRET_KEY if settings.SECRET_KEY else "dev-secret-key-change-in-production-min-32-chars"
        
        payload = jwt.decode(token, secret_key, algorithms=[ALGORITHM])
        return payload
    except JWTError as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Token verification failed: {str(e)}")
        return None


def get_user_id_from_token(token: str) -> Optional[int]:
    """Extract user ID from JWT token"""
    payload = verify_token(token)
    if payload:
        sub = payload.get("sub")
        # Convert string back to int if needed
        if sub:
            return int(sub) if isinstance(sub, str) else sub
    return None

