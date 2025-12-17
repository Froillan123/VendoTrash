"""
Redis Session Service
Manages user sessions and detection history using Redis
"""

import json
import logging
from typing import Optional, Dict, List
from datetime import datetime, timedelta
from config import get_redis_client

logger = logging.getLogger(__name__)

# Session TTL: 10 minutes (600 seconds)
SESSION_TTL = 600

# Detection history max items
MAX_DETECTION_HISTORY = 5


def create_session(user_id: int, token: str) -> bool:
    """
    Create a Redis session for a user
    
    Args:
        user_id: User ID
        token: JWT token string
        
    Returns:
        True if session created successfully, False otherwise
    """
    redis_client = get_redis_client()
    if not redis_client:
        logger.warning("Redis not available, session creation skipped")
        return False
    
    try:
        session_key = f"session:{user_id}"
        session_data = {
            "token": token,
            "user_id": user_id,
            "created_at": datetime.utcnow().isoformat(),
            "expires_at": (datetime.utcnow() + timedelta(seconds=SESSION_TTL)).isoformat()
        }
        
        # Store session with TTL
        redis_client.setex(
            session_key,
            SESSION_TTL,
            json.dumps(session_data)
        )
        
        logger.info(f"Created Redis session for user_id: {user_id}")
        return True
    except Exception as e:
        logger.error(f"Error creating session: {str(e)}")
        return False


def get_session(user_id: int) -> Optional[Dict]:
    """
    Get session data for a user
    
    Args:
        user_id: User ID
        
    Returns:
        Session data dict or None if not found
    """
    redis_client = get_redis_client()
    if not redis_client:
        return None
    
    try:
        session_key = f"session:{user_id}"
        session_data = redis_client.get(session_key)
        
        if session_data:
            return json.loads(session_data)
        return None
    except Exception as e:
        logger.error(f"Error getting session: {str(e)}")
        return None


def is_session_active(user_id: int) -> bool:
    """
    Check if user has an active session
    
    Args:
        user_id: User ID
        
    Returns:
        True if session exists and is active, False otherwise
    """
    redis_client = get_redis_client()
    if not redis_client:
        # Redis not available - return False (will fall back to token check)
        return False
    
    session = get_session(user_id)
    return session is not None


def get_active_session_for_user(user_id: int) -> Optional[Dict]:
    """
    Get active session for a user (alias for get_session)
    
    Args:
        user_id: User ID
        
    Returns:
        Session data dict or None if not found
    """
    return get_session(user_id)


def end_session(user_id: int) -> bool:
    """
    Manually end a user's session
    
    Args:
        user_id: User ID
        
    Returns:
        True if session ended successfully, False otherwise
    """
    redis_client = get_redis_client()
    if not redis_client:
        logger.warning("Redis not available, session end skipped")
        return False
    
    try:
        session_key = f"session:{user_id}"
        deleted = redis_client.delete(session_key)
        
        if deleted:
            logger.info(f"Ended session for user_id: {user_id}")
        else:
            logger.warning(f"No active session found for user_id: {user_id}")
        
        return deleted > 0
    except Exception as e:
        logger.error(f"Error ending session: {str(e)}")
        return False


def add_detection_to_history(user_id: int, detection_data: Dict) -> bool:
    """
    Add a detection to user's history (max 5 items)
    
    Args:
        user_id: User ID
        detection_data: Dict with material_type, confidence, points_earned, timestamp
        
    Returns:
        True if added successfully, False otherwise
    """
    redis_client = get_redis_client()
    if not redis_client:
        logger.warning("Redis not available, detection history skipped")
        return False
    
    try:
        history_key = f"detection_history:{user_id}"
        
        # Get current history
        current_history_json = redis_client.get(history_key)
        if current_history_json:
            history = json.loads(current_history_json)
        else:
            history = []
        
        # Add new detection at the beginning
        detection_data["timestamp"] = datetime.utcnow().isoformat()
        history.insert(0, detection_data)
        
        # Keep only last MAX_DETECTION_HISTORY items
        history = history[:MAX_DETECTION_HISTORY]
        
        # Store back to Redis (no expiration for history, or set long TTL)
        redis_client.set(history_key, json.dumps(history))
        
        logger.info(f"Added detection to history for user_id: {user_id}")
        return True
    except Exception as e:
        logger.error(f"Error adding detection to history: {str(e)}")
        return False


def get_detection_history(user_id: int) -> List[Dict]:
    """
    Get detection history for a user (max 5 items)
    
    Args:
        user_id: User ID
        
    Returns:
        List of detection dicts (empty list if none found)
    """
    redis_client = get_redis_client()
    if not redis_client:
        return []
    
    try:
        history_key = f"detection_history:{user_id}"
        history_json = redis_client.get(history_key)
        
        if history_json:
            return json.loads(history_json)
        return []
    except Exception as e:
        logger.error(f"Error getting detection history: {str(e)}")
        return []


def clear_detection_history(user_id: int) -> bool:
    """
    Clear detection history for a user
    
    Args:
        user_id: User ID
        
    Returns:
        True if cleared successfully, False otherwise
    """
    redis_client = get_redis_client()
    if not redis_client:
        return False
    
    try:
        history_key = f"detection_history:{user_id}"
        deleted = redis_client.delete(history_key)
        logger.info(f"Cleared detection history for user_id: {user_id}")
        return deleted > 0
    except Exception as e:
        logger.error(f"Error clearing detection history: {str(e)}")
        return False

