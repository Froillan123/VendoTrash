import hashlib
from typing import Optional


def hash_password(password: str) -> str:
    """Simple password hashing (use bcrypt in production)"""
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    return hash_password(plain_password) == hashed_password


def generate_token(user_id: int) -> str:
    """Simple token generation (use JWT in production)"""
    return hashlib.md5(f"{user_id}_secret".encode()).hexdigest()

