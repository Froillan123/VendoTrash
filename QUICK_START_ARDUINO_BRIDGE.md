# Quick Start: Arduino Bridge System

## What You Need (Hardware)

✅ Arduino Uno (naa na ninyo)  
✅ Ultrasonic Sensor HC-SR04 (naa na ninyo)  
✅ Servo Motor (naa na ninyo)  
✅ USB Webcam (naa na ninyo)  
✅ USB Cable (for Arduino)  

## Quick Setup (5 Steps)

### Step 1: Install Dependencies

```bash
cd Server
pip install -r requirements.txt
```

### Step 2: Upload Arduino Code

1. Open `Arduino/vendo/vendo.ino` in Arduino IDE
2. Select: `Tools` → `Board` → `Arduino Uno`
3. Select: `Tools` → `Port` → `COM3` (your Arduino port)
4. Click `Upload`
5. Open Serial Monitor (9600 baud) - should see: `"VendoTrash System Ready"`

### Step 3: Start FastAPI Server

```bash
cd Server
python main.py
```

Server runs on: `http://localhost:8000`

### Step 4: Run Bridge Script

```bash
cd Server
python arduino_bridge.py
```

Or specify port manually:
```bash
python arduino_bridge.py COM3
```

### Step 5: Test!

1. Place object in front of ultrasonic sensor
2. Watch logs:
   - Arduino detects → sends "READY"
   - Bridge captures webcam image
   - Server classifies
   - Arduino receives result → controls servo

## Wiring

**Ultrasonic Sensor:**
- TRIG → Pin 7
- ECHO → Pin 8
- VCC → 5V
- GND → GND

**Servo Motor:**
- Signal → Pin 10
- VCC → 5V
- GND → GND

## Sorting Direction

- **PLASTIC** → Servo moves **RIGHT** (135°)
- **CAN** → Servo moves **LEFT** (45°)

## Troubleshooting

**Arduino not found?**
- Check USB connection
- Manually specify port: `python arduino_bridge.py COM3`

**Webcam not working?**
- Close other apps using webcam
- Test in Windows Camera app

**Server connection failed?**
- Make sure server is running: `python Server/main.py`
- Check server URL in `arduino_bridge.py`

## Full Documentation

See `ARDUINO_BRIDGE_SETUP.md` for complete guide!

