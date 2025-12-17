# ESP32-CAM Connection Setup - Step by Step

## ✅ What I've Prepared For You

1. **Your Server IP**: `192.168.1.2` (already found!)
2. **Server URL**: `http://192.168.1.2:8000/api/vendo/classify` (ready to use)
3. **JWT Token Script**: `Server/get_jwt_token.py` (ready to run)

---

## 🚀 Step-by-Step Setup

### STEP 1: Start Your Server

**Open Terminal 1:**
```bash
cd Server
python main.py
```

**Keep this running!** You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

---

### STEP 2: Get JWT Token

**Open Terminal 2 (NEW terminal, keep server running):**
```bash
python Server/get_jwt_token.py
```

**Copy the token it shows!** It will look like:
```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

---

### STEP 3: Update ESP32 Code

**Open:** `Arduino/esp32_cam/esp32_cam.ino`

**Update these 3 lines (around line 18-29):**

```cpp
// 1. WiFi Credentials - YOU NEED TO FILL THESE!
const char* ssid = "YOUR_WIFI_NAME";        // ← Your WiFi name
const char* password = "YOUR_WIFI_PASSWORD"; // ← Your WiFi password

// 2. Server URL - ALREADY SET CORRECTLY!
const char* serverUrl = "http://192.168.1.2:8000/api/vendo/classify";

// 3. JWT Token - PASTE FROM STEP 2!
const char* authToken = "PASTE_YOUR_TOKEN_HERE";
```

**Example:**
```cpp
const char* ssid = "HomeWiFi-2.4";
const char* password = "MyPassword123";
const char* serverUrl = "http://192.168.1.2:8000/api/vendo/classify";
const char* authToken = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...";
```

---

### STEP 4: Upload to ESP32-CAM

1. **Select Board**: `Tools` → `Board` → `ESP32 Arduino` → `AI Thinker ESP32-CAM`
2. **Select Port**: `Tools` → `Port` → Choose your COM port
3. **Click Upload** (→ button)
4. **If needed**: Hold BOOT button → Click Upload → Release when "Connecting..." appears

---

### STEP 5: Open Serial Monitor

1. Click **Serial Monitor** icon (top right)
2. Set **Baud Rate**: `115200`
3. Set **Line Ending**: `Both NL & CR`
4. Press **RESET** button on ESP32-CAM

---

### STEP 6: Check Connection

**Look for this in Serial Monitor:**

```
========================================
ESP32-CAM Standalone VendoTrash
========================================

✅ Ultrasonic sensor initialized
✅ Servo motor initialized
✅ Camera initialized successfully

📡 Connecting to WiFi...
   SSID: HomeWiFi-2.4
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

**🎉 If you see "✅ Server is reachable!" - YOU'RE CONNECTED!**

---

## 📋 Quick Checklist

- [ ] Server is running (`python Server/main.py`)
- [ ] JWT token obtained (`python Server/get_jwt_token.py`)
- [ ] WiFi SSID and password ready
- [ ] ESP32 code updated (WiFi, server URL, token)
- [ ] Code uploaded to ESP32-CAM
- [ ] Serial Monitor open (115200 baud)
- [ ] See "Server is reachable!" message

---

## 🔧 What You Need to Provide

1. **WiFi SSID** - Your WiFi network name
   - Check: WiFi icon in system tray → See connected network name
   - Or: Router sticker

2. **WiFi Password** - Your WiFi password
   - Check: Router sticker
   - Or: Windows WiFi settings → Properties → Show characters

3. **JWT Token** - Run `python Server/get_jwt_token.py` to get it

---

## ❌ Troubleshooting

### Server Not Running
**Error**: "connection refused"
**Fix**: Start server: `python Server/main.py`

### WiFi Connection Failed
**Error**: "WiFi connection failed!"
**Fix**: 
- Check SSID and password (case-sensitive!)
- Ensure WiFi is 2.4GHz (not 5GHz)
- Move ESP32 closer to router

### Server Connection Failed
**Error**: "HTTP Error: -1"
**Fix**:
- Verify server is running
- Check server URL is correct: `http://192.168.1.2:8000`
- Check firewall allows port 8000

### Authentication Failed
**Error**: "HTTP Error: 401"
**Fix**:
- Get fresh JWT token (tokens expire)
- Run `python Server/get_jwt_token.py` again

---

## ✅ Success Indicators

- ✅ WiFi connected (IP address shown)
- ✅ Server is reachable
- ✅ Camera initialized
- ✅ System ready message

**Once you see all these, your ESP32-CAM is connected to the backend!**


