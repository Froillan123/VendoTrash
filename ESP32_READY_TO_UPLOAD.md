# ✅ ESP32-CAM Ready to Upload!

## 🎉 What's Done

- ✅ **Server is running** on `http://0.0.0.0:8000`
- ✅ **Server IP found**: `192.168.1.2`
- ✅ **JWT Token obtained**: Already updated in code!
- ✅ **Server URL set**: `http://192.168.1.2:8000/api/vendo/classify`

## 📝 What You Need to Do Now

### STEP 1: Update WiFi Credentials

**Open:** `Arduino/esp32_cam/esp32_cam.ino`

**Find lines 18-19 and update:**

```cpp
const char* ssid = "YOUR_WIFI_NAME";           // ← Put your WiFi name here
const char* password = "YOUR_WIFI_PASSWORD";   // ← Put your WiFi password here
```

**Example:**
```cpp
const char* ssid = "HomeWiFi-2.4";
const char* password = "MyPassword123";
```

### STEP 2: Upload to ESP32-CAM

1. **Select Board**: `Tools` → `Board` → `ESP32 Arduino` → `AI Thinker ESP32-CAM`
2. **Select Port**: `Tools` → `Port` → Choose your COM port
3. **Click Upload** (→ button)
4. **If needed**: Hold BOOT button → Click Upload → Release when "Connecting..." appears

### STEP 3: Open Serial Monitor

1. Click **Serial Monitor** icon (top right)
2. Set **Baud Rate**: `115200`
3. Set **Line Ending**: `Both NL & CR`
4. Press **RESET** button on ESP32-CAM

### STEP 4: Check Connection

**Look for this in Serial Monitor:**

```
========================================
ESP32-CAM Standalone VendoTrash
========================================

✅ Ultrasonic sensor initialized
✅ Servo motor initialized
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
Waiting for object detection...
========================================
```

**🎉 If you see "✅ Server is reachable!" - YOU'RE CONNECTED!**

---

## 📋 Current Configuration

- **Server URL**: `http://192.168.1.2:8000/api/vendo/classify` ✅
- **JWT Token**: Already set in code ✅
- **WiFi SSID**: Need to fill in ⚠️
- **WiFi Password**: Need to fill in ⚠️

---

## 🔍 How to Get WiFi Credentials

### Option 1: From Your PC
1. Click WiFi icon in system tray
2. See your connected network name (that's SSID)
3. Right-click → Properties → Show characters (to see password)

### Option 2: Router Sticker
- Look on your router for Network Name and Password

### Option 3: Phone Hotspot
- Enable hotspot → Note name and password
- Connect PC to hotspot → Use same in ESP32

---

## ⚠️ Important Notes

- **WiFi must be 2.4GHz** (ESP32 doesn't support 5GHz)
- **Copy credentials EXACTLY** (case-sensitive!)
- **Server is already running** - keep it running!
- **ESP32 and PC must be on same WiFi network**

---

## ✅ Success Checklist

- [ ] WiFi SSID and password updated in code
- [ ] Code uploaded to ESP32-CAM
- [ ] Serial Monitor open (115200 baud)
- [ ] See "WiFi connected!" message
- [ ] See "Server is reachable!" message

**Once you see "Server is reachable!" - Your ESP32-CAM is connected to the backend!** 🎉


