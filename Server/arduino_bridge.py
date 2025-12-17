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
SERVER_URL = "http://localhost:8000/api/vendo/capture-and-classify"
CAMERA_INDEX = 0  # Change if you have multiple cameras


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


def classify_trash(image_base64: str, server_url: str) -> Optional[str]:
    """
    Send image to server for classification
    
    Args:
        image_base64: Base64 encoded image
        server_url: FastAPI server URL
        
    Returns:
        Classification result: "PLASTIC", "CAN", "REJECTED", or None
    """
    try:
        logger.info(f"Sending image to server: {server_url}")
        
        response = requests.post(
            server_url,
            json={
                "image_base64": image_base64,
                "machine_id": 1
            },
            timeout=10.0
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
            elif material_type in ["NON_PLASTIC", "CAN"]:
                return "CAN"
            else:
                return "REJECTED"
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
    
    # Open Serial connection
    try:
        ser = serial.Serial(arduino_port, SERIAL_BAUD, timeout=SERIAL_TIMEOUT)
        logger.info(f"Connected to Arduino at {arduino_port}")
        time.sleep(2)  # Wait for Arduino to initialize
    except serial.SerialException as e:
        logger.error(f"Failed to open serial port {arduino_port}: {str(e)}")
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
                    logger.info("--- Object detected! Starting classification ---")
                    
                    # Step 1: Capture webcam image
                    logger.info("Step 1: Capturing image from webcam...")
                    image_base64 = capture_webcam_image(CAMERA_INDEX)
                    
                    if not image_base64:
                        logger.error("Failed to capture image. Sending ERROR to Arduino.")
                        ser.write(b"ERROR\n")
                        continue
                    
                    # Step 2: Send to server for classification
                    logger.info("Step 2: Sending to server for classification...")
                    result = classify_trash(image_base64, SERVER_URL)
                    
                    if not result:
                        logger.error("Classification failed. Sending ERROR to Arduino.")
                        ser.write(b"ERROR\n")
                        continue
                    
                    # Step 3: Send result back to Arduino
                    logger.info(f"Step 3: Sending result to Arduino: {result}")
                    ser.write(f"{result}\n".encode('utf-8'))
                    
                    logger.info("--- Classification complete! ---")
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

