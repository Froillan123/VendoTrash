"""
Webcam Service for capturing images from USB webcam
"""
import cv2
import base64
import logging
from typing import Optional, Tuple
import io
from PIL import Image

logger = logging.getLogger(__name__)


class WebcamService:
    """Service for capturing images from USB webcam"""
    
    def __init__(self, camera_index: int = 0):
        """
        Initialize webcam service
        
        Args:
            camera_index: Index of the camera (0 for default, 1 for second camera, etc.)
        """
        self.camera_index = camera_index
        self.camera = None
    
    def _open_camera(self) -> bool:
        """Open camera connection"""
        try:
            if self.camera is None:
                self.camera = cv2.VideoCapture(self.camera_index)
                if not self.camera.isOpened():
                    logger.error(f"Failed to open camera at index {self.camera_index}")
                    return False
                # Set camera resolution (optional, adjust as needed)
                self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            return True
        except Exception as e:
            logger.error(f"Error opening camera: {str(e)}")
            return False
    
    def _close_camera(self):
        """Close camera connection"""
        if self.camera is not None:
            self.camera.release()
            self.camera = None
    
    def capture_image(self, timeout: int = 3) -> Optional[str]:
        """
        Capture image from webcam and return as base64 string
        
        Args:
            timeout: Maximum number of attempts to capture a valid frame
            
        Returns:
            Base64 encoded JPEG image string, or None if capture failed
        """
        try:
            if not self._open_camera():
                return None
            
            # Try to capture a valid frame (sometimes first frame is black)
            for attempt in range(timeout):
                ret, frame = self.camera.read()
                
                if not ret:
                    logger.warning(f"Failed to read frame (attempt {attempt + 1}/{timeout})")
                    continue
                
                # Check if frame is not empty
                if frame is None or frame.size == 0:
                    logger.warning(f"Empty frame captured (attempt {attempt + 1}/{timeout})")
                    continue
                
                # Convert BGR to RGB (OpenCV uses BGR, PIL uses RGB)
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # Convert to PIL Image
                pil_image = Image.fromarray(frame_rgb)
                
                # Convert to JPEG bytes
                buffer = io.BytesIO()
                pil_image.save(buffer, format='JPEG', quality=85)
                image_bytes = buffer.getvalue()
                
                # Encode to base64
                image_base64 = base64.b64encode(image_bytes).decode('utf-8')
                
                logger.info(f"Successfully captured image: {len(image_bytes)} bytes")
                return image_base64
            
            logger.error("Failed to capture valid frame after all attempts")
            return None
            
        except Exception as e:
            logger.error(f"Error capturing image: {str(e)}")
            return None
        finally:
            # Don't close camera to keep it ready for next capture
            # Only close on service shutdown
            pass
    
    def capture_and_save(self, filepath: str) -> bool:
        """
        Capture image and save to file (for debugging)
        
        Args:
            filepath: Path to save the image
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if not self._open_camera():
                return False
            
            ret, frame = self.camera.read()
            if not ret:
                return False
            
            cv2.imwrite(filepath, frame)
            logger.info(f"Image saved to {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving image: {str(e)}")
            return False
    
    def __del__(self):
        """Cleanup on service destruction"""
        self._close_camera()


# Global instance (singleton pattern)
_webcam_service_instance: Optional[WebcamService] = None


def get_webcam_service(camera_index: int = 0) -> WebcamService:
    """
    Get or create webcam service instance
    
    Args:
        camera_index: Index of the camera
        
    Returns:
        WebcamService instance
    """
    global _webcam_service_instance
    if _webcam_service_instance is None:
        _webcam_service_instance = WebcamService(camera_index)
    return _webcam_service_instance

