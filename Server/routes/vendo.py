from fastapi import APIRouter, HTTPException, Depends, WebSocket, WebSocketDisconnect
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from schemas import VendoCommandRequest, VendoCommandResponse, VendoClassifyRequest, VendoClassifyResponse
from controllers.vendo_controller import (
    send_command_to_esp32, 
    get_esp32_status, 
    classify_trash_image, 
    capture_and_classify_trash,
    store_customer_token,
    remove_customer_token,
    get_active_customer_token
)
from dependencies import get_current_user, get_current_user_optional, get_customer_user
from models import User
from db import SessionLocal
from typing import Optional, Dict, Set
import logging
import json
import asyncio
from datetime import datetime
from services.session_service import (
    create_session,
    is_session_active,
    end_session,
    add_detection_to_history,
    get_detection_history,
    get_active_session_for_user
)

security = HTTPBearer()

router = APIRouter()
logger = logging.getLogger(__name__)

# WebSocket connection management
# Store active WebSocket connections per user: {user_id: Set[WebSocket]}
active_websocket_connections: Dict[int, Set[WebSocket]] = {}
# Note: asyncio.Lock() must be created per-request, not at module level
# We'll use a regular lock for thread safety and async-safe operations


@router.post("/command", response_model=VendoCommandResponse)
async def send_vendo_command(command: VendoCommandRequest):
    """Send sorting command to ESP32/Arduino"""
    try:
        result = await send_command_to_esp32(command.material)
        
        if result["status"] == "error":
            raise HTTPException(status_code=500, detail=result["message"])
        
        return VendoCommandResponse(
            status=result["status"],
            message=result["message"],
            material=command.material
        )
    except Exception as e:
        logger.error(f"Error in vendo command endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status")
async def get_vendo_status():
    """Get status from ESP32
    
    Returns status from ESP32 if connected, or offline status if ESP32 is not reachable.
    This is expected behavior when ESP32 is not yet connected or is offline.
    """
    try:
        status = await get_esp32_status()
        # Return appropriate HTTP status based on ESP32 connection
        if status.get("status") == "offline":
            # 503 Service Unavailable - ESP32 is offline (expected)
            from fastapi import status as http_status
            return status
        elif status.get("status") == "error":
            # 500 Internal Server Error - unexpected error
            from fastapi import status as http_status
            return status
        else:
            # 200 OK - ESP32 is online and responding
            return status
    except Exception as e:
        error_msg = str(e) if str(e) else "Unknown error"
        logger.error(f"Error getting ESP32 status: {error_msg}")
        return {
            "status": "error",
            "message": error_msg
        }


@router.get("/test")
async def test_esp32_connection():
    """Test endpoint for ESP32 connectivity testing"""
    return {
        "status": "ok",
        "message": "ESP32 can reach server",
        "server": "VendoTrash FastAPI",
        "endpoint": "/api/vendo/test"
    }


@router.post("/classify", response_model=VendoClassifyResponse)
async def classify_trash(
    request: VendoClassifyRequest,
    current_user: User = Depends(get_current_user)
):
    """Classify trash image using Google Cloud Vision (with base64 image)"""
    try:
        result = await classify_trash_image(
            image_base64=request.image_base64,
            user_id=current_user.id,
            machine_id=request.machine_id
        )
        
        return VendoClassifyResponse(**result)
    except Exception as e:
        logger.error(f"Classification error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/capture-and-classify", response_model=VendoClassifyResponse)
async def capture_and_classify(
    request: VendoClassifyRequest,
    current_user: User = Depends(get_customer_user),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Capture image from webcam and classify trash
    - REQUIRES: Authenticated customer (admin users cannot access)
    - REQUIRES: Active Redis session (created via /prepare-insert)
    - Stores JWT token for Arduino bridge script access
    - Adds detection to Redis history
    
    Accepts:
    - image_base64: Optional (if provided, uses it; if not, captures from webcam)
    - machine_id: Machine ID (default: 1)
    """
    try:
        # Check if session is active (only if Redis is available)
        # If Redis is down, fall back to token-based check
        from config import get_redis_client
        redis_available = get_redis_client() is not None
        
        if redis_available:
            if not is_session_active(current_user.id):
                raise HTTPException(
                    status_code=403,
                    detail="No active session. Please click 'Insert Trash' button first."
                )
        else:
            # Redis is down - fall back to token check (backward compatibility)
            token = get_active_customer_token()
            if not token:
                raise HTTPException(
                    status_code=403,
                    detail="No active session. Please click 'Insert Trash' button first."
                )
        
        # Get JWT token from credentials
        jwt_token = credentials.credentials
        
        # Store token for Arduino bridge access (backward compatibility)
        store_customer_token(current_user.id, jwt_token)
        logger.info(f"Stored token for customer user_id: {current_user.id}")
        
        # If image_base64 is provided, use it; otherwise capture from webcam
        if request.image_base64:
            result = await classify_trash_image(
                image_base64=request.image_base64,
                user_id=current_user.id,
                machine_id=request.machine_id
            )
        else:
            # Capture from webcam
            result = await capture_and_classify_trash(
                machine_id=request.machine_id,
                user_id=current_user.id
            )
        
        # Add detection to Redis history (including rejected items for visibility)
        detection_data = {
            "material_type": result.get("material_type", "REJECTED"),
            "confidence": result.get("confidence", 0.0),
            "points_earned": result.get("points_earned", 0),
            "transaction_id": result.get("transaction_id"),
            "status": result.get("status", "unknown"),
            "timestamp": datetime.utcnow().isoformat()
        }
        add_detection_to_history(current_user.id, detection_data)
        
        # Broadcast detection update via WebSocket (real-time)
        logger.info(f"📡 Broadcasting detection update via WebSocket for user {current_user.id}: {detection_data['material_type']}")
        await broadcast_detection_update(current_user.id, detection_data)
        
        return VendoClassifyResponse(**result)
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Capture and classify error: {error_msg}")
        
        # Provide user-friendly error messages
        if "webcam" in error_msg.lower() or "camera" in error_msg.lower():
            detail = "Webcam not available. Please ensure webcam is connected and not used by another application."
        elif "user" in error_msg.lower():
            detail = "User authentication error. Please login and try again."
        elif "vision" in error_msg.lower() or "google" in error_msg.lower():
            detail = "Google Vision API error. Please check API credentials configuration."
        elif "database" in error_msg.lower() or "connection" in error_msg.lower():
            detail = "Database connection error. Please check database configuration."
        else:
            detail = f"Classification failed: {error_msg}"
        
        raise HTTPException(status_code=500, detail=detail)


@router.post("/prepare-insert")
async def prepare_insert_session(
    current_user: User = Depends(get_customer_user),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Prepare insert session - creates Redis session and stores JWT token
    Called when user clicks "Insert Trash" button
    Does NOT capture or classify - just prepares the session
    """
    try:
        # Get JWT token from credentials
        jwt_token = credentials.credentials
        
        # If there's an existing session, end it first (cleanup)
        existing_session = get_active_session_for_user(current_user.id)
        if existing_session:
            logger.info(f"Ending existing session for user_id: {current_user.id} before creating new one")
            end_session(current_user.id)
        
        # Store token for Arduino bridge access (backward compatibility)
        # This MUST happen before creating session to ensure token is available
        store_customer_token(current_user.id, jwt_token)
        logger.info(f"Stored token for customer user_id: {current_user.id}")
        
        # Create Redis session
        session_created = create_session(current_user.id, jwt_token)
        if not session_created:
            logger.warning(f"Failed to create Redis session for user_id: {current_user.id}, but continuing with token storage")
        
        logger.info(f"Prepared insert session for customer user_id: {current_user.id}")
        
        return {
            "status": "success",
            "message": "System ready. Please insert trash into the machine.",
            "user_id": current_user.id,
            "session_active": session_created
        }
    except Exception as e:
        logger.error(f"Error preparing insert session: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to prepare insert session")


@router.post("/clear-token")
async def clear_customer_token(
    current_user: User = Depends(get_customer_user)
):
    """
    Clear stored JWT token for customer (called on logout)
    """
    try:
        remove_customer_token(current_user.id)
        return {"status": "success", "message": "Token cleared successfully"}
    except Exception as e:
        logger.error(f"Error clearing token: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to clear token")


@router.get("/active-token")
async def get_token_for_bridge():
    """
    Get active customer token for Arduino bridge script (no auth required)
    Returns the most recently active customer token
    """
    try:
        token = get_active_customer_token()
        if token:
            return {"status": "success", "token": token}
        else:
            return {"status": "not_found", "message": "No active customer token available"}
    except Exception as e:
        logger.error(f"Error getting active token: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get active token")


@router.post("/end-session")
async def end_user_session(
    current_user: User = Depends(get_customer_user)
):
    """
    End the current active session for the user
    Called when user clicks "End Session" button
    """
    try:
        ended = end_session(current_user.id)
        
        # Also clear token (backward compatibility)
        remove_customer_token(current_user.id)
        
        if ended:
            return {
                "status": "success",
                "message": "Session ended successfully",
                "user_id": current_user.id
            }
        else:
            return {
                "status": "not_found",
                "message": "No active session found",
                "user_id": current_user.id
            }
    except Exception as e:
        logger.error(f"Error ending session: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to end session")


@router.get("/session-status")
async def get_session_status():
    """
    Get session status for bridge script (no auth required)
    Checks if any user has an active Redis session
    Returns status indicating if session is active
    """
    try:
        # Check if there's an active token (backward compatibility)
        token = get_active_customer_token()
        
        if not token:
            return {
                "status": "inactive",
                "has_session": False,
                "message": "No active session"
            }
        
        # Try to check Redis sessions
        # Since we don't know user_id, we'll check if token exists
        # In practice, if token exists, there should be a session
        # We can improve this by storing a global "active_sessions" set in Redis
        # For now, we'll use token as indicator
        
        # Additional check: try to find any active Redis session
        # This is a simplified check - in production you might want to store
        # a global list of active user IDs
        has_redis_session = False
        try:
            from config import get_redis_client
            redis_client = get_redis_client()
            if redis_client:
                # Check if any session key exists (pattern: session:*)
                # This is a simple check - in production you might want a more efficient approach
                keys = redis_client.keys("session:*")
                has_redis_session = len(keys) > 0
        except Exception as redis_error:
            logger.debug(f"Redis check failed (non-critical): {str(redis_error)}")
        
        # If token exists, consider session active (backward compatibility)
        # If Redis is available and has sessions, that's even better
        has_session = token is not None or has_redis_session
        
        return {
            "status": "active" if has_session else "inactive",
            "has_session": has_session,
            "message": "Active session found" if has_session else "No active session"
        }
    except Exception as e:
        logger.error(f"Error getting session status: {str(e)}")
        return {
            "status": "error",
            "has_session": False,
            "message": f"Error checking session: {str(e)}"
        }


@router.get("/detection-history")
async def get_user_detection_history(
    current_user: User = Depends(get_customer_user)
):
    """
    Get detection history for the current user (max 5 items)
    """
    try:
        history = get_detection_history(current_user.id)
        
        return {
            "status": "success",
            "history": history,
            "count": len(history)
        }
    except Exception as e:
        logger.error(f"Error getting detection history: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get detection history")


@router.websocket("/ws/detection-updates/{user_id}")
async def websocket_detection_updates(websocket: WebSocket, user_id: int):
    """
    WebSocket endpoint for real-time detection updates
    Connects clients to receive instant detection notifications
    """
    await websocket.accept()
    logger.info(f"✅ WebSocket connected for user {user_id}")
    
    # Add connection to active connections
    if user_id not in active_websocket_connections:
        active_websocket_connections[user_id] = set()
    active_websocket_connections[user_id].add(websocket)
    
    try:
        # Send initial connection confirmation
        await websocket.send_json({
            "type": "connection",
            "status": "connected",
            "user_id": user_id,
            "message": "WebSocket connected. Ready to receive detection updates."
        })
        
        # Keep connection alive and handle incoming messages
        while True:
            try:
                # Wait for ping messages or any client message
                data = await asyncio.wait_for(websocket.receive_text(), timeout=30.0)
                
                # Handle ping/pong for keepalive
                if data == "ping":
                    await websocket.send_json({"type": "pong"})
                elif data.startswith("{"):
                    # Handle JSON messages if needed in the future
                    try:
                        message = json.loads(data)
                        logger.debug(f"Received message from user {user_id}: {message}")
                    except json.JSONDecodeError:
                        pass
            except asyncio.TimeoutError:
                # Send keepalive ping
                try:
                    await websocket.send_json({"type": "keepalive"})
                except Exception:
                    # Connection might be closed
                    break
                    
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for user {user_id}")
    except Exception as e:
        logger.error(f"WebSocket error for user {user_id}: {str(e)}")
    finally:
        # Remove connection
        if user_id in active_websocket_connections:
            active_websocket_connections[user_id].discard(websocket)
            if not active_websocket_connections[user_id]:
                del active_websocket_connections[user_id]
        logger.info(f"WebSocket connection cleaned up for user {user_id}")


async def broadcast_detection_update(user_id: int, detection_data: dict):
    """
    Broadcast detection update to all connected WebSocket clients for a user
    
    Args:
        user_id: User ID to broadcast to
        detection_data: Detection data to send
    """
    if user_id not in active_websocket_connections:
        logger.debug(f"No active WebSocket connections for user {user_id} - skipping broadcast")
        return  # No active connections for this user
    
    message = {
        "type": "detection_update",
        "data": detection_data,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    disconnected = set()
    # Get a copy of connections to iterate over (safe iteration)
    connections = active_websocket_connections.get(user_id, set()).copy()
    connection_count = len(connections)
    
    logger.info(f"📤 Broadcasting to {connection_count} WebSocket connection(s) for user {user_id}")
    
    for websocket in connections:
        try:
            await websocket.send_json(message)
            logger.info(f"✅ Sent detection update to user {user_id} via WebSocket: {detection_data['material_type']}")
        except Exception as e:
            logger.warning(f"❌ Failed to send WebSocket message to user {user_id}: {str(e)}")
            disconnected.add(websocket)
    
    # Clean up disconnected connections
    if disconnected:
        logger.info(f"🧹 Cleaning up {len(disconnected)} disconnected WebSocket connection(s) for user {user_id}")
        if user_id in active_websocket_connections:
            active_websocket_connections[user_id] -= disconnected
            if not active_websocket_connections[user_id]:
                del active_websocket_connections[user_id]

