"""
Webcam Service for capturing images from USB webcam
"""
import cv2
import base64
import logging
import time
import sys
from typing import Optional, Tuple
import io
from PIL import Image

logger = logging.getLogger(__name__)


class WebcamService:
    """Service for capturing images from USB webcam - Event-driven for Arduino bridge"""
    
    def __init__(self, camera_index: int = 0):
        """
        Initialize webcam service
        
        Args:
            camera_index: Index of the camera (0 for default, 1 for second camera, etc.)
        """
        self.camera_index = camera_index
        self.camera = None
        self._lock_count = 0  # Track how many times camera is opened
        self._max_retries = 3
    
    def _open_camera(self) -> bool:
        """Open camera connection with retry logic"""
        try:
            # If camera is already open, check if it's still working
            if self.camera is not None:
                if self.camera.isOpened():
                    return True
                else:
                    # Camera was closed externally, reset
                    self.camera = None
            
            # Try to open camera with retries
            for attempt in range(self._max_retries):
                try:
                    # Use DirectShow on Windows for better compatibility
                    backend = cv2.CAP_DSHOW if sys.platform == "win32" else cv2.CAP_ANY
                    self.camera = cv2.VideoCapture(self.camera_index, backend)
                    if self.camera.isOpened():
                        # Set camera resolution
                        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                        # Set buffer size to 1 to get latest frame
                        self.camera.set(cv2.CAP_PROP_BUFFERSIZE, 1)
                        logger.info(f"Camera opened successfully at index {self.camera_index}")
                        return True
                    else:
                        self.camera.release()
                        self.camera = None
                except Exception as e:
                    logger.warning(f"Camera open attempt {attempt + 1} failed: {str(e)}")
                    if self.camera:
                        self.camera.release()
                        self.camera = None
                    time.sleep(0.1)  # Small delay before retry
            
            logger.error(f"Failed to open camera at index {self.camera_index} after {self._max_retries} attempts")
            # Try to provide helpful error message
            if sys.platform == "win32":
                logger.error("On Windows: Make sure webcam is not used by another app (Camera, Zoom, Teams, etc.)")
            return False
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
        Event-driven: Called when Arduino bridge receives "READY" signal
        
        Args:
            timeout: Maximum number of attempts to capture a valid frame
            
        Returns:
            Base64 encoded JPEG image string, or None if capture failed
        """
        try:
            if not self._open_camera():
                logger.error("Camera not available for capture")
                return None
            
            # Flush buffer to get latest frame (important for event-driven capture)
            for _ in range(2):
                self.camera.read()  # Discard old frames
            
            # Try to capture a valid frame
            for attempt in range(timeout):
                ret, frame = self.camera.read()
                
                if not ret:
                    logger.warning(f"Failed to read frame (attempt {attempt + 1}/{timeout})")
                    time.sleep(0.1)
                    continue
                
                # Check if frame is not empty
                if frame is None or frame.size == 0:
                    logger.warning(f"Empty frame captured (attempt {attempt + 1}/{timeout})")
                    time.sleep(0.1)
                    continue
                
                # Validate frame has content (not all black)
                if frame.mean() < 5:  # Very dark frame, might be invalid
                    logger.warning(f"Frame too dark (attempt {attempt + 1}/{timeout})")
                    time.sleep(0.1)
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

