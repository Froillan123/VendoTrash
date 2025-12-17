# ESP32-CAM Connectivity Setup Guide

This guide will help you test and configure ESP32-CAM connection to your VendoTrash server.

## Prerequisites

- ESP32-CAM module (AI-Thinker)
- Arduino IDE with ESP32 board support
- FastAPI server running (local or Cloud Run)
- WiFi network credentials
- JWT authentication token

## Step 1: Test Server Connectivity

Before connecting ESP32-CAM, verify your server is accessible:

```bash
# Run connectivity test script
cd Server
python test_connectivity.py
```

This will:
- Find your local IP address
- Test server health endpoint
- Test vendo endpoints
- Check CORS settings
- Provide the URL to use in ESP32 code

**Expected Output:**
```
📍 Local IP Address: 192.168.1.2

🔍 Testing: Local Network (192.168.1.2) (http://192.168.1.2:8000)
✅ Health check passed
✅ Vendo status check passed
✅ ESP32 test endpoint passed

✅ Use this URL for ESP32-CAM: http://192.168.1.2:8000
```

## Step 2: Get JWT Authentication Token

ESP32-CAM needs a JWT token to authenticate with the server:

### Option A: Get Token from Login (Recommended)

1. Login to your VendoTrash app (web or API)
2. Copy the `access_token` from the response
3. Use this token in ESP32 code

### Option B: Create Test User and Get Token

```bash
# Create a test user
cd Server
python create_admin.py

# Or login via API
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "test@vendotrash.com", "password": "test123"}'
```

Copy the `access_token` from the response.

## Step 3: Configure ESP32-CAM Code

1. Open `Arduino/esp32_cam/esp32_cam.ino` in Arduino IDE

2. Update these configuration values:

```cpp
// WiFi credentials
const char* ssid = "YOUR_WIFI_SSID";           // Your WiFi network name
const char* password = "YOUR_WIFI_PASSWORD";   // Your WiFi password

// Server URL (from Step 1)
const char* serverUrl = "http://192.168.1.2:8000/api/vendo/classify";

// JWT token (from Step 2)
const char* authToken = "YOUR_JWT_TOKEN";
```

3. **Important**: Replace all placeholder values with your actual credentials!

## Step 4: Install Required Arduino Libraries

In Arduino IDE, install these libraries via Library Manager:

1. **ArduinoJson** (by Benoit Blanchon) - Version 6.x
2. **base64** (by Densaugeo) - For image encoding

To install:
- Go to `Tools` → `Manage Libraries`
- Search for each library
- Click `Install`

## Step 5: Configure Arduino IDE for ESP32

1. Go to `File` → `Preferences`
2. Add this URL to "Additional Board Manager URLs":
   ```
   https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json
   ```
3. Go to `Tools` → `Board` → `Boards Manager`
4. Search for "ESP32" and install "esp32 by Espressif Systems"
5. Select board: `Tools` → `Board` → `ESP32 Arduino` → `AI Thinker ESP32-CAM`

## Step 6: Flash ESP32-CAM

1. Connect ESP32-CAM to computer via USB (use FTDI adapter if needed)
2. Select correct COM port: `Tools` → `Port`
3. Click `Upload` button
4. Wait for upload to complete
5. Open Serial Monitor: `Tools` → `Serial Monitor`
   - Set baud rate to **115200**
   - Set line ending to **Both NL & CR**

## Step 7: Verify Connection

After flashing, you should see in Serial Monitor:

```
========================================
ESP32-CAM VendoTrash System
========================================

✅ Serial2 initialized for Arduino communication
✅ Camera initialized successfully

📡 Connecting to WiFi...
   SSID: YourWiFiName
✅ WiFi connected!
   IP address: 192.168.1.XXX
   Signal strength (RSSI): -XX dBm

🌐 Testing server connection...
   Testing: http://192.168.1.2:8000/api/vendo/test
   ✅ Server is reachable!
   Response: {"status":"ok","message":"ESP32 can reach server",...}

========================================
System Ready!
Waiting for Arduino 'READY' signal...
========================================
```

## Step 8: Test Full Flow

1. **Ensure Arduino is connected** to ESP32 via Serial2:
   - ESP32 GPIO 4 (RX) → Arduino TX
   - ESP32 GPIO 2 (TX) → Arduino RX
   - Common GND connection

2. **Trigger detection**:
   - Place object in front of ultrasonic sensor
   - Arduino should send "READY" signal
   - ESP32 should capture image and send to server

3. **Monitor Serial output**:
   - ESP32 Serial Monitor: See image capture and classification
   - Arduino Serial Monitor: See sorting commands

## Troubleshooting

### WiFi Connection Failed

**Symptoms:**
```
❌ WiFi connection failed!
   Check SSID and password
```

**Solutions:**
- Verify SSID and password are correct
- Ensure WiFi is 2.4GHz (ESP32 doesn't support 5GHz)
- Check WiFi signal strength
- Try moving ESP32 closer to router

### Server Connection Failed

**Symptoms:**
```
❌ HTTP Error: -1
   Error message: connection refused
```

**Solutions:**
- Verify server is running: `python Server/main.py`
- Check server URL is correct (use IP from `test_connectivity.py`)
- Ensure firewall allows port 8000
- Test server manually: `curl http://192.168.1.2:8000/health`

### Camera Initialization Failed

**Symptoms:**
```
❌ Camera init failed with error 0xXXXX
```

**Solutions:**
- Check camera module is properly connected
- Verify pin definitions match your ESP32-CAM board
- Ensure adequate power supply (5V, 2A recommended)
- Try resetting ESP32-CAM

### Authentication Failed

**Symptoms:**
```
❌ HTTP Error: 401
   Error message: Unauthorized
```

**Solutions:**
- Verify JWT token is valid (not expired)
- Check token format: `Bearer YOUR_TOKEN`
- Get new token from login endpoint
- Ensure user account is active

### Image Upload Failed

**Symptoms:**
```
❌ HTTP Error: 413
   Error message: Request Entity Too Large
```

**Solutions:**
- Reduce image quality: Change `config.jpeg_quality = 10` (lower = smaller file)
- Reduce frame size: Change `config.frame_size = FRAMESIZE_QVGA` (320x240)
- Check server request size limits

## Connection Summary

After successful setup, your connection flow is:

```
Arduino (Ultrasonic) 
  → Serial2 "READY" 
  → ESP32-CAM (Capture Image) 
  → HTTP POST /api/vendo/classify 
  → FastAPI Server (Google Vision) 
  → Classification Result 
  → Serial2 "PLASTIC"/"NON_PLASTIC" 
  → Arduino (Servo Sort)
```

## Next Steps

1. ✅ Test connectivity: `python Server/test_connectivity.py`
2. ✅ Configure ESP32 code with WiFi and server URL
3. ✅ Flash ESP32-CAM and verify connection
4. ✅ Test image capture and classification
5. ✅ Integrate with Arduino for full sorting flow

## Support

For issues, check:
- `Server/test_connectivity.py` output
- ESP32 Serial Monitor logs
- Server logs (`python Server/main.py`)
- `ESP32_CAM_INTEGRATION.md` for detailed architecture


