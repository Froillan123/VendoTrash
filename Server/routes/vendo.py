from fastapi import APIRouter, HTTPException, Depends
from schemas import VendoCommandRequest, VendoCommandResponse, VendoClassifyRequest, VendoClassifyResponse
from controllers.vendo_controller import send_command_to_esp32, get_esp32_status, classify_trash_image, capture_and_classify_trash
from dependencies import get_current_user, get_current_user_optional
from models import User
from typing import Optional
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


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
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    Capture image from webcam and classify trash
    - If authenticated: Uses current user from JWT token
    - If not authenticated: Uses default user (for Arduino bridge script)
    
    Accepts:
    - image_base64: Optional (if provided, uses it; if not, captures from webcam)
    - machine_id: Machine ID (default: 1)
    """
    try:
        # Determine user_id: use authenticated user if available, otherwise default
        user_id = None
        if current_user:
            user_id = current_user.id
            logger.info(f"Using authenticated user ID: {user_id}")
        
        # If image_base64 is provided, use it; otherwise capture from webcam
        if request.image_base64:
            # Use provided image (for testing)
            if not user_id:
                from models import User
                db = SessionLocal()
                try:
                    default_user = db.query(User).filter(User.is_active == True).first()
                    if not default_user:
                        raise HTTPException(status_code=500, detail="No active user found")
                    user_id = default_user.id
                finally:
                    db.close()
            
            result = await classify_trash_image(
                image_base64=request.image_base64,
                user_id=user_id,
                machine_id=request.machine_id
            )
        else:
            # Capture from webcam
            result = await capture_and_classify_trash(
                machine_id=request.machine_id,
                user_id=user_id  # Use authenticated user or None (will use default)
            )
        
        return VendoClassifyResponse(**result)
    except Exception as e:
        logger.error(f"Capture and classify error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

