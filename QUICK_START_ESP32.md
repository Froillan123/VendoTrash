# 🚀 Quick Start: Connect ESP32-CAM to Backend

## ✅ What's Already Done

- ✅ Server IP found: `192.168.1.2`
- ✅ Server URL ready: `http://192.168.1.2:8000/api/vendo/classify`
- ✅ ESP32 code file ready: `Arduino/esp32_cam/esp32_cam.ino`
- ✅ JWT token script ready: `Server/get_jwt_token.py`

---

## 📝 What You Need to Do (3 Simple Steps)

### STEP 1: Start Your Server ⚡

**Open a terminal and run:**
```bash
cd Server
python main.py
```

**Keep this terminal open!** You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**✅ Server is running when you see "Uvicorn running"**

---

### STEP 2: Get JWT Token 🔑

**Open a NEW terminal (keep server running in first terminal):**
```bash
python Server/get_jwt_token.py
```

**Copy the token it shows!** Example:
```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiZXhwIjoxNzM0...
```

---

### STEP 3: Update ESP32 Code 📝

**Open:** `Arduino/esp32_cam/esp32_cam.ino`

**Find these lines (around line 18-29) and update:**

```cpp
// 1. YOUR WIFI CREDENTIALS - FILL THESE!
const char* ssid = "YOUR_WIFI_NAME";           // ← Put your WiFi name here
const char* password = "YOUR_WIFI_PASSWORD";   // ← Put your WiFi password here

// 2. SERVER URL - ALREADY CORRECT! ✅
const char* serverUrl = "http://192.168.1.2:8000/api/vendo/classify";

// 3. JWT TOKEN - PASTE FROM STEP 2!
const char* authToken = "PASTE_TOKEN_HERE";    // ← Paste token from Step 2
```

**Example (replace with YOUR values):**
```cpp
const char* ssid = "HomeWiFi-2.4";
const char* password = "MyPassword123";
const char* serverUrl = "http://192.168.1.2:8000/api/vendo/classify";
const char* authToken = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...";
```

---

### STEP 4: Upload & Test 🚀

1. **Upload to ESP32:**
   - Select board: `AI Thinker ESP32-CAM`
   - Select port: Your COM port
   - Click Upload

2. **Open Serial Monitor:**
   - Baud rate: `115200`
   - Press RESET on ESP32

3. **Look for:**
   ```
   ✅ WiFi connected!
   ✅ Server is reachable!
   ```

**🎉 If you see "Server is reachable!" - YOU'RE CONNECTED!**

---

## 🔍 How to Get WiFi Credentials

### Option 1: From Your PC
1. Click WiFi icon in system tray
2. See your connected network name (that's SSID)
3. Right-click → Properties → Show characters (to see password)

### Option 2: Router Sticker
- Look on your router for:
  - Network Name (SSID)
  - Password/Key

### Option 3: Phone Hotspot
- Enable hotspot on phone
- Note the hotspot name and password
- Connect PC to hotspot
- Use same credentials in ESP32

---

## ⚠️ Important Notes

- **WiFi must be 2.4GHz** (ESP32 doesn't support 5GHz)
- **Copy credentials EXACTLY** (case-sensitive!)
- **Server must be running** before testing connection
- **ESP32 and PC must be on same WiFi network**

---

## ✅ Success Checklist

- [ ] Server running (`python Server/main.py`)
- [ ] JWT token copied (from `get_jwt_token.py`)
- [ ] WiFi SSID and password ready
- [ ] ESP32 code updated (3 values changed)
- [ ] Code uploaded to ESP32
- [ ] Serial Monitor shows "Server is reachable!"

---

## 🆘 Quick Troubleshooting

**Server not running?**
→ Start it: `python Server/main.py`

**WiFi connection failed?**
→ Check SSID/password (case-sensitive!)

**Server connection failed?**
→ Make sure server is running and URL is correct

**No token?**
→ Run: `python Server/get_jwt_token.py`

---

## 📞 Ready to Test?

1. Start server (Step 1)
2. Get token (Step 2)  
3. Update code (Step 3)
4. Upload & check Serial Monitor (Step 4)

**That's it!** 🎉


