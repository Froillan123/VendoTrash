# ESP32-CAM Configuration Helper

## Your Configuration Values

### 1. Server IP Address
```
192.168.1.2
```

### 2. Server URL for ESP32
```
http://192.168.1.2:8000/api/vendo/classify
```

### 3. WiFi Credentials
**You need to provide these:**
- SSID (WiFi name): _________________
- Password: _________________

### 4. JWT Token
**Get it by running:**
```bash
python Server/get_jwt_token.py
```

---

## Quick Setup Steps

### Step 1: Start Your Server
```bash
cd Server
python main.py
```
Keep this running in a terminal.

### Step 2: Get JWT Token
In a **new terminal**:
```bash
python Server/get_jwt_token.py
```
Copy the token it shows.

### Step 3: Update ESP32 Code

Open `Arduino/esp32_cam/esp32_cam.ino` and update:

```cpp
// WiFi credentials - FILL THESE IN!
const char* ssid = "YOUR_WIFI_NAME_HERE";
const char* password = "YOUR_WIFI_PASSWORD_HERE";

// Server URL - ALREADY SET!
const char* serverUrl = "http://192.168.1.2:8000/api/vendo/classify";

// JWT Token - PASTE FROM get_jwt_token.py
const char* authToken = "PASTE_TOKEN_HERE";
```

### Step 4: Upload to ESP32
1. Select board: `AI Thinker ESP32-CAM`
2. Select port: Your COM port
3. Click Upload
4. Open Serial Monitor (115200 baud)

### Step 5: Check Connection
Look for:
```
✅ WiFi connected!
✅ Server is reachable!
```

---

## What You Need to Provide

1. **WiFi SSID** - Your WiFi network name
2. **WiFi Password** - Your WiFi password
3. **JWT Token** - Run `python Server/get_jwt_token.py` to get it


