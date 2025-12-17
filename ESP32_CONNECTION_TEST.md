# ESP32-CAM Backend Connection Test - Step by Step

Quick guide to test if ESP32-CAM can connect to your deployed backend.

## Prerequisites Checklist

- [ ] ESP32-CAM is powered on (via step-down converter)
- [ ] ESP32-CAM code is uploaded (or ready to upload)
- [ ] FastAPI server is running
- [ ] WiFi network is available
- [ ] You have WiFi credentials (SSID and password)

---

## Step 1: Start Your FastAPI Server

Open a terminal/command prompt:

```bash
cd Server
python main.py
```

**Expected Output:**
```
INFO:     Started server process
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

**✅ Server is running if you see "Uvicorn running"**

---

## Step 2: Find Your Server IP Address

In a **new terminal/command prompt** (keep server running):

```bash
cd Server
python test_connectivity.py
```

**Expected Output:**
```
📍 Local IP Address: 192.168.1.2

✅ Health check passed
✅ Vendo status check passed
✅ ESP32 test endpoint passed

✅ Use this URL for ESP32-CAM: http://192.168.1.2:8000
```

**📝 Note the IP address** (e.g., `192.168.1.2`) - you'll need this!

---

## Step 3: Get JWT Authentication Token

You need a token to authenticate with the server.

### Option A: Via Web App (Easiest)

1. Open your browser: `http://localhost:5175`
2. Login with your credentials
3. Open Developer Tools: Press `F12`
4. Go to **Network** tab
5. Refresh the page or click any button
6. Click on any API request (e.g., `/api/users/me`)
7. Go to **Headers** tab
8. Find `Authorization: Bearer YOUR_TOKEN_HERE`
9. Copy the token (the long string after "Bearer ")

### Option B: Via API (Command Line)

```bash
curl -X POST http://localhost:8000/api/auth/login ^
  -H "Content-Type: application/json" ^
  -d "{\"email\":\"admin@vendotrash.com\",\"password\":\"admin123\"}"
```

**📝 Copy the `access_token` from the response**

---

## Step 4: Update ESP32-CAM Code

Open your ESP32-CAM code in Arduino IDE and update these 3 values:

```cpp
// 1. WiFi Credentials
const char* ssid = "YOUR_WIFI_SSID";           // Your WiFi name
const char* password = "YOUR_WIFI_PASSWORD";   // Your WiFi password

// 2. Server URL (use IP from Step 2)
const char* serverUrl = "http://192.168.1.2:8000/api/vendo/classify";

// 3. JWT Token (from Step 3)
const char* authToken = "YOUR_JWT_TOKEN_HERE";
```

**Example:**
```cpp
const char* ssid = "MyWiFiNetwork";
const char* password = "mypassword123";
const char* serverUrl = "http://192.168.1.2:8000/api/vendo/classify";
const char* authToken = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...";
```

---

## Step 5: Upload Code to ESP32-CAM

1. **Select Board**: `Tools` → `Board` → `ESP32 Arduino` → `AI Thinker ESP32-CAM`
2. **Select Port**: `Tools` → `Port` → Choose your COM port
3. **Click Upload** (→ button)
4. **If upload fails**: Hold BOOT button → Click Upload → Release BOOT when "Connecting..." appears

**✅ Wait for "Hard resetting via RTS pin..." message**

---

## Step 6: Open Serial Monitor

1. Click **Serial Monitor** icon (top right) or `Tools` → `Serial Monitor`
2. Set **Baud Rate**: `115200`
3. Set **Line Ending**: `Both NL & CR`
4. Press **RESET** button on ESP32-CAM

---

## Step 7: Check Connection Status

Look for this output in Serial Monitor:

### ✅ SUCCESS - Connected!

```
========================================
ESP32-CAM Standalone VendoTrash
========================================

✅ Ultrasonic sensor initialized
✅ Servo motor initialized
✅ Camera initialized successfully

📡 Connecting to WiFi...
   SSID: MyWiFiNetwork
✅ WiFi connected!
   IP address: 192.168.1.105
   Signal strength (RSSI): -45 dBm

🌐 Testing server connection...
   Testing: http://192.168.1.2:8000/api/vendo/test
   ✅ Server is reachable!
   Response: {"status":"ok","message":"ESP32 can reach server",...}

========================================
System Ready!
Waiting for object detection...
========================================
```

**🎉 If you see "Server is reachable!" - Your ESP32-CAM is connected to backend!**

---

## Step 8: Test Full Classification Flow

1. **Place an object** in front of ultrasonic sensor (within 10cm)
2. **Watch Serial Monitor** - you should see:

```
📦 Object detected! Distance: 8 cm
📸 Capturing image...
✅ Image captured: 12345 bytes
🌐 Sending to server...

📊 Classification Results:
   Material: PLASTIC
   Points: 2
   Confidence: 85.5%
♻️ PLASTIC -> Moving to LEFT bin
```

3. **Check Server Logs** - you should see:
```
INFO: POST /api/vendo/classify
INFO: Classification: PLASTIC, Confidence: 0.85
```

---

## Troubleshooting

### ❌ WiFi Connection Failed

**Symptoms:**
```
❌ WiFi connection failed!
   Check SSID and password
```

**Fix:**
- Double-check WiFi SSID and password (case-sensitive)
- Ensure WiFi is 2.4GHz (ESP32 doesn't support 5GHz)
- Move ESP32 closer to router

### ❌ Server Connection Failed

**Symptoms:**
```
❌ HTTP Error: -1
   Error message: connection refused
```

**Fix:**
1. Verify server is running: `python Server/main.py`
2. Check server URL is correct (use IP from `test_connectivity.py`)
3. Check firewall allows port 8000
4. Test manually: `curl http://192.168.1.2:8000/health`

### ❌ Authentication Failed (401)

**Symptoms:**
```
❌ HTTP Error: 401
```

**Fix:**
- Get a fresh JWT token (tokens expire)
- Verify token format (should start with "eyJ...")
- Login again and copy new token

### ❌ No Serial Output

**Symptoms:**
- Serial Monitor is blank

**Fix:**
- Check baud rate is 115200
- Press RESET button on ESP32-CAM
- Check Serial Monitor is open
- Verify USB/FTDI connection

---

## Quick Test Checklist

- [ ] Server is running (`python Server/main.py`)
- [ ] Server IP address found (`python Server/test_connectivity.py`)
- [ ] JWT token obtained (from login)
- [ ] ESP32 code updated (WiFi, server URL, token)
- [ ] Code uploaded to ESP32-CAM
- [ ] Serial Monitor open (115200 baud)
- [ ] ESP32-CAM shows "Server is reachable!"

---

## Next Steps After Connection Works

1. ✅ Test with different objects (plastic bottles, metal cans)
2. ✅ Verify classification accuracy
3. ✅ Check server logs for transaction creation
4. ✅ Test servo motor movement
5. ✅ Monitor Serial output for errors

---

## Summary

**Connection Flow:**
```
ESP32-CAM → WiFi → FastAPI Server → Google Vision API → Response → ESP32-CAM → Servo
```

**Key Requirements:**
- Server running on local network
- WiFi credentials correct
- Server URL correct (with IP address)
- JWT token valid
- All components powered (step-down converter)

**Success Indicator:**
- Serial Monitor shows: "✅ Server is reachable!"

