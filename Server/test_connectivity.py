"""
Connectivity Test Script for ESP32-CAM
Tests server accessibility and network reachability
"""
import requests
import socket
import sys
import logging
from typing import Optional, Tuple

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_local_ip() -> Optional[str]:
    """Get the local IP address of this machine"""
    try:
        # Connect to a remote address to determine local IP
        # This doesn't actually send data, just determines the route
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))  # Google DNS
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception as e:
        logger.error(f"Error getting local IP: {str(e)}")
        return None


def test_server_health(base_url: str) -> bool:
    """Test if server health endpoint is accessible"""
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            logger.info(f"✅ Health check passed: {response.json()}")
            return True
        else:
            logger.error(f"❌ Health check failed: Status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Health check failed: {str(e)}")
        return False


def test_vendo_status(base_url: str) -> bool:
    """Test if vendo status endpoint is accessible"""
    try:
        response = requests.get(f"{base_url}/api/vendo/status", timeout=5)
        if response.status_code == 200:
            logger.info(f"✅ Vendo status check passed: {response.json()}")
            return True
        else:
            logger.warning(f"⚠️  Vendo status check returned: Status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Vendo status check failed: {str(e)}")
        return False


def test_vendo_test_endpoint(base_url: str) -> bool:
    """Test the ESP32 test endpoint"""
    try:
        response = requests.get(f"{base_url}/api/vendo/test", timeout=5)
        if response.status_code == 200:
            logger.info(f"✅ ESP32 test endpoint passed: {response.json()}")
            return True
        else:
            logger.warning(f"⚠️  ESP32 test endpoint returned: Status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ ESP32 test endpoint failed: {str(e)}")
        return False


def test_cors_headers(base_url: str) -> bool:
    """Test if CORS headers are properly set"""
    try:
        # Make an OPTIONS request to check CORS
        response = requests.options(
            f"{base_url}/api/vendo/test",
            headers={"Origin": "http://192.168.1.100"},
            timeout=5
        )
        
        cors_headers = {
            "access-control-allow-origin": response.headers.get("Access-Control-Allow-Origin"),
            "access-control-allow-methods": response.headers.get("Access-Control-Allow-Methods"),
            "access-control-allow-headers": response.headers.get("Access-Control-Allow-Headers"),
        }
        
        logger.info(f"CORS Headers: {cors_headers}")
        
        if cors_headers["access-control-allow-origin"]:
            logger.info("✅ CORS headers detected")
            return True
        else:
            logger.warning("⚠️  CORS headers not found")
            return False
    except Exception as e:
        logger.error(f"❌ CORS test failed: {str(e)}")
        return False


def main():
    """Run all connectivity tests"""
    print("=" * 60)
    print("ESP32-CAM Connectivity Test")
    print("=" * 60)
    
    # Get local IP
    local_ip = get_local_ip()
    if local_ip:
        print(f"\n📍 Local IP Address: {local_ip}")
    else:
        print("\n⚠️  Could not determine local IP address")
    
    # Test URLs
    test_urls = [
        ("http://localhost:8000", "Localhost"),
        ("http://127.0.0.1:8000", "127.0.0.1"),
    ]
    
    if local_ip:
        test_urls.append((f"http://{local_ip}:8000", f"Local Network ({local_ip})"))
    
    print("\n" + "=" * 60)
    print("Testing Server Connectivity")
    print("=" * 60)
    
    results = {}
    
    for base_url, name in test_urls:
        print(f"\n🔍 Testing: {name} ({base_url})")
        print("-" * 60)
        
        url_results = {
            "health": test_server_health(base_url),
            "vendo_status": test_vendo_status(base_url),
            "vendo_test": test_vendo_test_endpoint(base_url),
            "cors": test_cors_headers(base_url),
        }
        
        results[name] = url_results
        
        # Summary
        passed = sum(1 for v in url_results.values() if v)
        total = len(url_results)
        print(f"\n📊 Results: {passed}/{total} tests passed")
    
    # Final summary
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    
    if local_ip:
        print(f"\n✅ Use this URL for ESP32-CAM: http://{local_ip}:8000")
        print(f"   Update ESP32 code with: const char* serverUrl = \"http://{local_ip}:8000/api/vendo/classify\";")
    else:
        print("\n⚠️  Could not determine local IP. Use 'ipconfig' (Windows) or 'ifconfig' (Linux/Mac) to find it.")
    
    print("\n📝 Next Steps:")
    print("1. Ensure server is running: python Server/main.py")
    print("2. Check firewall allows port 8000")
    print("3. Update ESP32-CAM code with server URL")
    print("4. Flash ESP32-CAM and test connection")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())


