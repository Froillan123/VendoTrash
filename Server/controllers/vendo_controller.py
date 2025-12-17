import httpx
import logging
from config import settings
from typing import Optional

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
                return {"status": "error", "message": "Failed to get status"}
                
    except Exception as e:
        logger.error(f"Error getting ESP32 status: {str(e)}")
        return {"status": "error", "message": str(e)}

