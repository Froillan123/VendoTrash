import httpx
import logging
from config import settings
from typing import Optional, Dict
from services.vision_service import vision_service
from db import SessionLocal
from controllers.transaction_controller import create_transaction

logger = logging.getLogger(__name__)


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
        
        # Capture image from webcam
        logger.info("Capturing image from webcam...")
        webcam_service = get_webcam_service(0)  # Use default camera (index 0)
        image_base64 = webcam_service.capture_image()
        
        if not image_base64:
            raise Exception("Failed to capture image from webcam")
        
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
                    raise Exception("No active user found in database")
            finally:
                db.close()
        
        # Classify using existing function
        return await classify_trash_image(image_base64, user_id, machine_id)
        
    except Exception as e:
        logger.error(f"Error capturing and classifying trash: {str(e)}")
        raise


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
        
        # Calculate points (Plastic=2, Non-plastic=1)
        points = 2 if classification["material_type"] == "PLASTIC" else 1
        
        # Create transaction in database
        db = SessionLocal()
        try:
            transaction = create_transaction({
                "user_id": user_id,
                "machine_id": machine_id,
                "material_type": classification["material_type"],
                "points_earned": points
            }, db)
            
            return {
                "status": "success",
                "material_type": classification["material_type"],
                "confidence": classification["confidence"],
                "points_earned": points,
                "transaction_id": str(transaction.id)  # UUID as string
            }
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Error classifying trash: {str(e)}")
        raise

