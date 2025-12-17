from fastapi import APIRouter, HTTPException
from schemas import VendoCommandRequest, VendoCommandResponse
from controllers.vendo_controller import send_command_to_esp32, get_esp32_status
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
    """Get status from ESP32"""
    try:
        status = await get_esp32_status()
        return status
    except Exception as e:
        logger.error(f"Error getting ESP32 status: {str(e)}")
        return {"status": "error", "message": str(e)}

