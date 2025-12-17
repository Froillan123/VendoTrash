import httpx
import logging
from config import settings
from typing import Optional, Dict
from services.vision_service import vision_service
from db import SessionLocal
from controllers.transaction_controller import create_transaction
from threading import Lock

logger = logging.getLogger(__name__)

# Token storage for Arduino bridge access
# Maps user_id -> JWT token
_customer_tokens: Dict[int, str] = {}
_token_lock = Lock()


async def send_command_to_esp32(material: str) -> dict:
    """Send command to ESP32/Arduino - business logic"""
    try:
        esp32_url = f"http://{settings.ESP32_IP}:{settings.ESP32_PORT}/command"
        
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.post(
                esp32_url,
                json={
                    "command": "SORT",
                    "material": material
                }
            )
            
            if response.status_code == 200:
                logger.info(f"Command sent to ESP32: {material}")
                return {
                    "status": "success",
                    "message": f"Command sent: {material}",
                    "response": response.json()
                }
            else:
                logger.error(f"ESP32 returned status {response.status_code}")
                return {
                    "status": "error",
                    "message": f"ESP32 returned status {response.status_code}"
                }
                
    except httpx.TimeoutException:
        logger.error("ESP32 connection timeout")
        return {
            "status": "error",
            "message": "ESP32 device unreachable (timeout)"
        }
    except Exception as e:
        logger.error(f"Error sending command to ESP32: {str(e)}")
        return {
            "status": "error",
            "message": f"Error: {str(e)}"
        }


async def get_esp32_status() -> dict:
    """Get status from ESP32 - business logic"""
    try:
        esp32_url = f"http://{settings.ESP32_IP}:{settings.ESP32_PORT}/status"
        
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(esp32_url)
            
            if response.status_code == 200:
                return response.json()
            else:
                return {
                    "status": "error",
                    "message": f"ESP32 returned status {response.status_code}",
                    "esp32_url": esp32_url
                }
                
    except httpx.TimeoutException:
        logger.warning(f"ESP32 status check timeout - device may be offline at {settings.ESP32_IP}:{settings.ESP32_PORT}")
        return {
            "status": "offline",
            "message": "ESP32 device unreachable (timeout) - device may be offline or not connected",
            "esp32_url": f"http://{settings.ESP32_IP}:{settings.ESP32_PORT}/status"
        }
    except httpx.ConnectError as e:
        logger.warning(f"ESP32 connection error - device not reachable: {str(e)}")
        return {
            "status": "offline",
            "message": f"ESP32 device not reachable: {str(e)}",
            "esp32_url": f"http://{settings.ESP32_IP}:{settings.ESP32_PORT}/status"
        }
    except Exception as e:
        error_msg = str(e) if str(e) else "Unknown error"
        logger.error(f"Error getting ESP32 status: {error_msg}")
        return {
            "status": "error",
            "message": error_msg,
            "esp32_url": f"http://{settings.ESP32_IP}:{settings.ESP32_PORT}/status"
        }


async def capture_and_classify_trash(machine_id: int = 1, user_id: Optional[int] = None) -> Dict:
    """
    Capture image from webcam and classify trash
    
    Args:
        machine_id: Machine ID for transaction
        user_id: Optional user ID (if None, uses default test user)
        
    Returns:
        Dict with status, material_type, confidence, points_earned, transaction_id
    """
    try:
        from services.webcam_service import get_webcam_service
        import cv2
        
        # Capture image from webcam
        logger.info("Capturing image from webcam...")
        
        # Try different camera indices (0, 1, 2)
        image_base64 = None
        for camera_index in range(3):
            try:
                webcam_service = get_webcam_service(camera_index)
                image_base64 = webcam_service.capture_image()
                if image_base64:
                    logger.info(f"Successfully captured image from camera index {camera_index}")
                    break
            except Exception as e:
                logger.warning(f"Failed to capture from camera index {camera_index}: {str(e)}")
                continue
        
        if not image_base64:
            error_msg = "Failed to capture image from webcam. Please ensure webcam is connected and not used by another application."
            logger.error(error_msg)
            raise Exception(error_msg)
        
        logger.info("Image captured successfully, classifying...")
        
        # Use default user if not provided (for bridge script)
        if user_id is None:
            # Try to get a default user (admin or first user)
            from models import User
            db = SessionLocal()
            try:
                default_user = db.query(User).filter(User.is_active == True).first()
                if default_user:
                    user_id = default_user.id
                    logger.info(f"Using default user ID: {user_id}")
                else:
                    raise Exception("No active user found in database. Please register or login first.")
            finally:
                db.close()
        
        # Classify using existing function
        return await classify_trash_image(image_base64, user_id, machine_id)
        
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Error capturing and classifying trash: {error_msg}")
        # Provide more helpful error messages
        if "webcam" in error_msg.lower() or "camera" in error_msg.lower():
            raise Exception("Webcam error: " + error_msg)
        elif "user" in error_msg.lower():
            raise Exception("User error: " + error_msg)
        elif "vision" in error_msg.lower() or "google" in error_msg.lower():
            raise Exception("Vision API error: " + error_msg)
        else:
            raise Exception(f"Classification error: {error_msg}")


def store_customer_token(user_id: int, token: str) -> None:
    """
    Store JWT token for customer to be used by Arduino bridge
    
    Args:
        user_id: Customer user ID
        token: JWT token string
    """
    with _token_lock:
        _customer_tokens[user_id] = token
        logger.info(f"Stored token for customer user_id: {user_id}")


def get_customer_token(user_id: int) -> Optional[str]:
    """
    Get stored JWT token for customer
    
    Args:
        user_id: Customer user ID
        
    Returns:
        JWT token string or None if not found
    """
    with _token_lock:
        return _customer_tokens.get(user_id)


def remove_customer_token(user_id: int) -> None:
    """
    Remove stored JWT token for customer (on logout)
    
    Args:
        user_id: Customer user ID
    """
    with _token_lock:
        if user_id in _customer_tokens:
            del _customer_tokens[user_id]
            logger.info(f"Removed token for customer user_id: {user_id}")


def get_active_customer_token() -> Optional[str]:
    """
    Get token for the most recently active customer (for bridge script)
    
    Returns:
        JWT token string or None if no active customer
    """
    with _token_lock:
        if _customer_tokens:
            # Return the most recent token (last one in dict)
            return list(_customer_tokens.values())[-1]
        return None


async def classify_trash_image(image_base64: str, user_id: int, machine_id: int) -> Dict:
    """
    Classify trash image and create transaction
    
    Args:
        image_base64: Base64 encoded JPEG image
        user_id: User ID for transaction
        machine_id: Machine ID for transaction
        
    Returns:
        Dict with status, material_type, confidence, points_earned, transaction_id
    """
    try:
        # Classify using Google Vision
        classification = await vision_service.classify_trash(image_base64)
        material_type = classification["material_type"]
        
        # If item is rejected, don't create transaction
        if material_type == "REJECTED":
            logger.info("Item rejected - no transaction created")
            return {
                "status": "rejected",
                "material_type": "REJECTED",
                "confidence": classification["confidence"],
                "points_earned": 0,
                "transaction_id": None
            }
        
        # Calculate points (Plastic=2, Non-plastic=1)
        points = 2 if material_type == "PLASTIC" else 1
        
        # Create transaction in database
        db = SessionLocal()
        try:
            transaction = create_transaction({
                "user_id": user_id,
                "machine_id": machine_id,
                "material_type": material_type,
                "points_earned": points
            }, db)
            
            return {
                "status": "success",
                "material_type": material_type,
                "confidence": classification["confidence"],
                "points_earned": points,
                "transaction_id": str(transaction.id)  # UUID as string
            }
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Error classifying trash: {str(e)}")
        raise

