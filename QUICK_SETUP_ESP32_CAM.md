# Quick Setup Guide: ESP32-CAM + Google Vision

> **⚠️ FUTURE IMPLEMENTATION**  
> This is a **future implementation** guide. The current system uses sensor-based detection.

## 🚀 Quick Start (5 Steps) - For Future Implementation

### Step 1: Google Cloud Setup (10 minutes)
1. Go to https://console.cloud.google.com/
2. Create project: `vendotrash-vision`
3. Enable **Cloud Vision API**
4. Create **Service Account** → Download JSON key
5. Save as `Server/google_vision_credentials.json`

### Step 2: Install Dependencies
```bash
cd Server
pip install google-cloud-vision Pillow
```

### Step 3: Update .env
```env
GOOGLE_APPLICATION_CREDENTIALS=./google_vision_credentials.json
```

### Step 4: Flash ESP32-CAM
1. Open `Arduino/esp32_cam/esp32_cam.ino`
2. Update WiFi credentials
3. Update server URL
4. Flash to ESP32-CAM

### Step 5: Test
1. Insert trash
2. ESP32 captures image
3. Server classifies via Google Vision
4. Arduino sorts trash

## 📋 File Checklist

- [ ] `ESP32_CAM_INTEGRATION.md` - Full plan (created ✅)
- [ ] `Server/services/vision_service.py` - Google Vision wrapper
- [ ] `Server/routes/vendo.py` - Add `/classify` endpoint
- [ ] `Server/controllers/vendo_controller.py` - Add classification logic
- [ ] `Arduino/esp32_cam/esp32_cam.ino` - ESP32-CAM code
- [ ] `Arduino/vendo/vendo.ino` - Update for Serial commands

## 💰 Cost Estimate

- **Free tier**: First 1,000 classifications/month = FREE
- **After free tier**: ~$1.50 per 1,000 classifications
- **Example**: 5,000/month = ~$6/month

## 🔧 Hardware Needed

- ESP32-CAM module (AI-Thinker)
- Arduino Uno/Nano (for sorting)
- Servo motors (2x)
- Ultrasonic sensor (HC-SR04)
- Power supply (5V, 2A for ESP32-CAM)

## 📝 Next Actions

1. **Today**: Set up Google Cloud Vision API
2. **Tomorrow**: Implement server-side code
3. **Day 3**: Flash ESP32-CAM and test
4. **Day 4**: Full integration testing

See `ESP32_CAM_INTEGRATION.md` for complete details!

