#!/usr/bin/env python3
"""
Arduino Bridge Script
Bridges communication between Arduino Uno and FastAPI Server

Flow:
1. Listens to Serial port for "READY" from Arduino
2. Captures image from USB webcam
3. Sends HTTP POST to FastAPI server for classification
4. Sends result back to Arduino via Serial: "PLASTIC" or "CAN"
"""

import serial
import serial.tools.list_ports
import requests
import base64
import cv2
import time
import logging
import sys
from typing import Optional
from services.webcam_service import get_webcam_service

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
SERIAL_BAUD = 9600
SERIAL_TIMEOUT = 1.0
SERVER_BASE_URL = "http://localhost:8000"
SERVER_URL = f"{SERVER_BASE_URL}/api/vendo/capture-and-classify"
SESSION_STATUS_URL = f"{SERVER_BASE_URL}/api/vendo/session-status"
CAMERA_INDEX = 0  # Change if you have multiple cameras

# Token cache to reduce HTTP calls
_cached_token = None
_token_cache_time = 0
_TOKEN_CACHE_TTL = 300  # Cache token for 5 minutes


def find_arduino_port() -> Optional[str]:
    """
    Find Arduino COM port automatically
    
    Returns:
        COM port string (e.g., "COM3") or None if not found
    """
    ports = serial.tools.list_ports.comports()
    
    for port in ports:
        # Common Arduino identifiers
        if any(keyword in port.description.upper() for keyword in [
            'ARDUINO', 'USB SERIAL', 'CH340', 'CP210', 'FTDI'
        ]):
            logger.info(f"Found Arduino at: {port.device} ({port.description})")
            return port.device
    
    logger.warning("Arduino not found automatically. Available ports:")
    for port in ports:
        logger.warning(f"  - {port.device}: {port.description}")
    
    return None


def capture_webcam_image(camera_index: int = 0) -> Optional[str]:
    """
    Capture image from USB webcam and return as base64
    
    Args:
        camera_index: Index of the camera
        
    Returns:
        Base64 encoded JPEG image string, or None if failed
    """
    try:
        webcam_service = get_webcam_service(camera_index)
        image_base64 = webcam_service.capture_image()
        
        if image_base64:
            logger.info("Webcam image captured successfully")
            return image_base64
        else:
            logger.error("Failed to capture webcam image")
            return None
            
    except Exception as e:
        logger.error(f"Error capturing webcam image: {str(e)}")
        return None


def get_active_token(server_base_url: str) -> Optional[str]:
    """
    Get active customer JWT token from server (with caching to reduce HTTP calls)
    
    Args:
        server_base_url: Base URL of FastAPI server (e.g., "http://localhost:8000")
        
    Returns:
        JWT token string or None if not available
    """
    global _cached_token, _token_cache_time
    
    # Check cache first
    current_time = time.time()
    if _cached_token and (current_time - _token_cache_time) < _TOKEN_CACHE_TTL:
        logger.debug("Using cached token (reduces HTTP latency)")
        return _cached_token
    
    try:
        token_url = f"{server_base_url}/api/vendo/active-token"
        logger.info(f"Retrieving active token from: {token_url}")
        
        response = requests.get(token_url, timeout=1.5)  # Reduced timeout for faster response
        
        if response.status_code == 200:
            result = response.json()
            if result.get("status") == "success":
                token = result.get("token")
                # Cache the token
                _cached_token = token
                _token_cache_time = current_time
                logger.info("Active token retrieved and cached successfully")
                return token
            else:
                logger.warning(f"No active token available: {result.get('message', 'Unknown error')}")
                # Clear cache on failure
                _cached_token = None
                return None
        else:
            logger.error(f"Failed to get token: {response.status_code}")
            _cached_token = None
            return None
            
    except requests.exceptions.ConnectionError:
        logger.error("Cannot connect to server to get token. Is the FastAPI server running?")
        _cached_token = None
        return None
    except Exception as e:
        logger.error(f"Error retrieving token: {str(e)}")
        _cached_token = None
        return None


def check_session_status(server_base_url: str) -> bool:
    """
    Check if there's an active session before processing READY signal
    
    Args:
        server_base_url: Base URL of FastAPI server
        
    Returns:
        True if session is active, False otherwise
    """
    try:
        logger.info(f"Checking session status: {SESSION_STATUS_URL}")
        response = requests.get(SESSION_STATUS_URL, timeout=1.5)  # Reduced timeout for faster response
        
        if response.status_code == 200:
            result = response.json()
            has_session = result.get("has_session", False)
            
            if has_session:
                logger.info("✅ Active session found - proceeding with classification")
                return True
            else:
                logger.warning("⚠️  No active session - ignoring READY signal")
                logger.info("💡 User must click 'Insert Trash' button first")
                return False
        else:
            logger.warning(f"Session status check returned {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        logger.error("Cannot connect to server to check session status")
        return False
    except Exception as e:
        logger.error(f"Error checking session status: {str(e)}")
        return False


def classify_trash(image_base64: str, server_url: str, jwt_token: Optional[str] = None) -> Optional[str]:
    """
    Send image to server for classification
    
    Args:
        image_base64: Base64 encoded image
        server_url: FastAPI server URL
        jwt_token: Optional JWT token for authentication
        
    Returns:
        Classification result: "PLASTIC", "CAN", "REJECTED", or None
    """
    try:
        logger.info(f"Sending image to server: {server_url}")
        
        headers = {}
        if jwt_token:
            headers["Authorization"] = f"Bearer {jwt_token}"
            logger.info("Including JWT token in request")
        
        response = requests.post(
            server_url,
            json={
                "image_base64": image_base64,
                "machine_id": 1
            },
            headers=headers,
            timeout=5.0  # Reduced timeout - Vision API should respond faster
        )
        
        if response.status_code == 200:
            result = response.json()
            material_type = result.get("material_type", "").upper()
            
            logger.info(f"Classification result: {material_type}")
            logger.info(f"Confidence: {result.get('confidence', 0):.2f}")
            logger.info(f"Points earned: {result.get('points_earned', 0)}")
            
            # Map server response to Arduino commands
            if material_type == "PLASTIC":
                return "PLASTIC"
            elif material_type == "NON_PLASTIC":
                return "CAN"
            elif material_type == "REJECTED":
                return "REJECTED"
            else:
                return "REJECTED"  # Unknown types are rejected
        elif response.status_code == 401:
            logger.error("Authentication failed: Token expired or invalid")
            return "ERROR"
        elif response.status_code == 403:
            logger.error("Access forbidden: Only customers can perform this action")
            return "ERROR"
        else:
            logger.error(f"Server returned error: {response.status_code}")
            logger.error(f"Response: {response.text}")
            return "ERROR"
            
    except requests.exceptions.ConnectionError:
        logger.error("Cannot connect to server. Is the FastAPI server running?")
        return "ERROR"
    except requests.exceptions.Timeout:
        logger.error("Server request timeout")
        return "ERROR"
    except Exception as e:
        logger.error(f"Error classifying trash: {str(e)}")
        return "ERROR"


def main():
    """Main bridge loop"""
    logger.info("=" * 50)
    logger.info("VendoTrash Arduino Bridge")
    logger.info("Server-Side Camera Classification")
    logger.info("=" * 50)
    
    # Find Arduino port
    arduino_port = find_arduino_port()
    if not arduino_port:
        logger.error("Arduino not found! Please connect Arduino and try again.")
        logger.error("Or manually specify port: python arduino_bridge.py COM3")
        sys.exit(1)
    
    # Allow manual port specification
    if len(sys.argv) > 1:
        arduino_port = sys.argv[1]
        logger.info(f"Using manually specified port: {arduino_port}")
    
    # Open Serial connection with better error handling
    ser = None
    max_retries = 3
    for attempt in range(max_retries):
        try:
            ser = serial.Serial(arduino_port, SERIAL_BAUD, timeout=SERIAL_TIMEOUT)
            logger.info(f"✅ Connected to Arduino at {arduino_port}")
            time.sleep(2)  # Wait for Arduino to initialize
            break
        except serial.SerialException as e:
            error_msg = str(e)
            if "Access is denied" in error_msg or "PermissionError" in error_msg:
                logger.error("=" * 60)
                logger.error("❌ COM PORT IS LOCKED!")
                logger.error("=" * 60)
                logger.error(f"Port {arduino_port} is being used by another program.")
                logger.error("")
                logger.error("SOLUTION:")
                logger.error("1. Close Arduino IDE Serial Monitor (if open)")
                logger.error("2. Close any other programs using COM6")
                logger.error("3. Unplug and replug Arduino USB cable")
                logger.error("4. Try again")
                logger.error("")
                if attempt < max_retries - 1:
                    logger.info(f"Retrying in 2 seconds... (attempt {attempt + 1}/{max_retries})")
                    time.sleep(2)
                else:
                    logger.error("=" * 60)
                    sys.exit(1)
            else:
                logger.error(f"Failed to open serial port {arduino_port}: {error_msg}")
                if attempt < max_retries - 1:
                    logger.info(f"Retrying in 2 seconds... (attempt {attempt + 1}/{max_retries})")
                    time.sleep(2)
                else:
                    sys.exit(1)
    
    if ser is None:
        logger.error("Failed to connect to Arduino after all retries")
        sys.exit(1)
    
    # Test webcam
    logger.info("Testing webcam...")
    webcam_service = get_webcam_service(CAMERA_INDEX)
    test_image = webcam_service.capture_image()
    if test_image:
        logger.info("Webcam is working!")
    else:
        logger.warning("Webcam test failed, but continuing anyway...")
    
    # Test server connection
    logger.info(f"Testing server connection: {SERVER_URL}")
    try:
        response = requests.get(SERVER_URL.replace("/capture-and-classify", "/test"), timeout=5.0)
        if response.status_code == 200:
            logger.info("Server is reachable!")
        else:
            logger.warning(f"Server returned status {response.status_code}")
    except Exception as e:
        logger.warning(f"Server connection test failed: {str(e)}")
        logger.warning("Make sure FastAPI server is running!")
    
    logger.info("=" * 50)
    logger.info("Bridge is ready! Waiting for Arduino 'READY' signal...")
    logger.info("=" * 50)
    logger.info("")
    
    # Main loop
    try:
        while True:
            if ser.in_waiting > 0:
                line = ser.readline().decode('utf-8').strip()
                logger.info(f"Received from Arduino: {line}")
                
                if line == "READY":
                    # EVENT-DRIVEN FLOW: Ultrasonic sensor triggered → Process event
                    logger.info("=" * 50)
                    logger.info("EVENT: Object detected by ultrasonic sensor!")
                    logger.info("=" * 50)
                    
                    # Step 0: Check if session is active before processing
                    logger.info("Step 0: [EVENT] Checking for active session...")
                    if not check_session_status(SERVER_BASE_URL):
                        logger.warning("=" * 50)
                        logger.warning("⚠️  NO ACTIVE SESSION - Ignoring READY signal")
                        logger.warning("=" * 50)
                        logger.info("User must click 'Insert Trash' button in the web app first.")
                        logger.info("Sending NO_SESSION to Arduino to reset state...")
                        # Send response to Arduino so it doesn't get stuck waiting
                        ser.write(b"NO_SESSION\n")
                        logger.info("Waiting for next READY signal...")
                        logger.info("")
                        continue
                    
                    # Step 1: EVENT → Capture webcam image
                    logger.info("Step 1: [EVENT] Capturing image from webcam...")
                    image_base64 = capture_webcam_image(CAMERA_INDEX)
                    
                    if not image_base64:
                        logger.error("Failed to capture image. Sending ERROR to Arduino.")
                        ser.write(b"ERROR\n")
                        continue
                    
                    # Step 2: EVENT → Get active customer token and send to server for classification
                    logger.info("Step 2: [EVENT] Retrieving active customer token...")
                    jwt_token = get_active_token(SERVER_BASE_URL)
                    
                    if not jwt_token:
                        logger.warning("No active customer token found. Requesting classification without token (may fail if auth required)...")
                    
                    logger.info("Step 2: [EVENT] Sending to server for computer vision classification...")
                    result = classify_trash(image_base64, SERVER_URL, jwt_token)
                    
                    if not result:
                        logger.error("Classification failed. Sending ERROR to Arduino.")
                        ser.write(b"ERROR\n")
                        continue
                    
                    # Step 3: EVENT → Send result back to Arduino (feedback loop)
                    logger.info(f"Step 3: [EVENT] Sending classification result to Arduino: {result}")
                    ser.write(f"{result}\n".encode('utf-8'))
                    
                    logger.info("=" * 50)
                    logger.info("EVENT PROCESSING COMPLETE!")
                    logger.info("=" * 50)
                    logger.info("")
                
                elif line.startswith("TRASH DETECTED") or line.startswith("SYSTEM READY"):
                    # Just log Arduino status messages
                    pass
                else:
                    logger.debug(f"Arduino message: {line}")
            
            time.sleep(0.1)  # Small delay to prevent CPU spinning
            
    except KeyboardInterrupt:
        logger.info("")
        logger.info("Shutting down bridge...")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
    finally:
        ser.close()
        logger.info("Serial port closed. Goodbye!")


if __name__ == "__main__":
    main()

