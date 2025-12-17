# Arduino Bridge Setup Guide

Complete guide for setting up the Arduino Uno + Server-Side Camera system.

## Architecture

```
Arduino Uno
├── Ultrasonic Sensor (HC-SR04)
├── Servo Motor (sorting)
└── USB → PC (Serial communication)
    ↓
PC Python Bridge Script
├── Listens to Serial (Arduino)
├── Captures from USB Webcam
└── Sends HTTP POST to Server
    ↓
FastAPI Server
├── Receives image
├── Google Vision API (classification)
└── Returns: PLASTIC or CAN
    ↓
PC Bridge Script → Serial → Arduino
    ↓
Arduino → Controls Servo
- PLASTIC → RIGHT (135°)
- CAN → LEFT (45°)
```

## Hardware Setup

### Arduino Uno Connections

**Ultrasonic Sensor (HC-SR04):**
- VCC → 5V
- GND → GND
- TRIG → Pin 7
- ECHO → Pin 8

**Servo Motor:**
- Red (VCC) → 5V
- Black (GND) → GND
- Yellow/Orange (Signal) → Pin 10

**USB Cable:**
- Connect Arduino Uno to PC via USB

### PC Setup

**USB Webcam:**
- Connect USB webcam to PC
- Test webcam works (Windows Camera app)

## Software Setup

### Step 1: Install Python Dependencies

```bash
cd Server
pip install -r requirements.txt
```

This will install:
- `pyserial` - For Serial communication with Arduino
- `opencv-python` - For webcam capture
- `requests` - For HTTP requests
- All other FastAPI dependencies

### Step 2: Upload Arduino Code

1. Open `Arduino/vendo/vendo.ino` in Arduino IDE
2. Select board: `Tools` → `Board` → `Arduino Uno`
3. Select port: `Tools` → `Port` → `COM3` (or your Arduino port)
4. Click `Upload`
5. Open Serial Monitor: `Tools` → `Serial Monitor`
   - Set baud rate to **9600**
   - You should see: `"VendoTrash System Ready"`

### Step 3: Start FastAPI Server

```bash
cd Server
python main.py
```

Server should start on `http://localhost:8000`

### Step 4: Run Arduino Bridge Script

**Option A: Auto-detect Arduino port**
```bash
cd Server
python arduino_bridge.py
```

**Option B: Manually specify port**
```bash
cd Server
python arduino_bridge.py COM3
```

Replace `COM3` with your actual Arduino COM port.

## Testing

### Test 1: Arduino Connection

1. Upload Arduino code
2. Open Serial Monitor (9600 baud)
3. You should see: `"VendoTrash System Ready"`
4. Place object in front of ultrasonic sensor
5. You should see: `"TRASH DETECTED!"` and `"READY"`

### Test 2: Webcam

1. Run bridge script
2. Check logs for: `"Webcam is working!"`
3. If error, check webcam is connected and not used by another app

### Test 3: Server Connection

1. Start FastAPI server
2. Run bridge script
3. Check logs for: `"Server is reachable!"`
4. If error, make sure server is running on `http://localhost:8000`

### Test 4: Full Flow

1. Start FastAPI server
2. Run bridge script
3. Place object in front of ultrasonic sensor
4. Watch logs:
   - Arduino detects object
   - Bridge captures webcam image
   - Server classifies image
   - Arduino receives result and controls servo

## Troubleshooting

### Arduino Not Found

**Error:** `"Arduino not found! Please connect Arduino and try again."`

**Solutions:**
1. Check Arduino is connected via USB
2. Check Device Manager for COM port
3. Manually specify port: `python arduino_bridge.py COM3`
4. Install Arduino drivers if needed

### Webcam Not Working

**Error:** `"Failed to capture image from webcam"`

**Solutions:**
1. Check webcam is connected
2. Close other apps using webcam (Zoom, Teams, etc.)
3. Test webcam in Windows Camera app
4. Try different camera index: Change `CAMERA_INDEX = 1` in `arduino_bridge.py`

### Server Connection Failed

**Error:** `"Cannot connect to server. Is the FastAPI server running?"`

**Solutions:**
1. Make sure FastAPI server is running: `python Server/main.py`
2. Check server URL in `arduino_bridge.py`: `SERVER_URL = "http://localhost:8000/api/vendo/capture-and-classify"`
3. Test server manually: `curl http://localhost:8000/health`

### Classification Always Returns "REJECTED"

**Solutions:**
1. Check Google Vision API is enabled
2. Check credentials in `.env`: `GOOGLE_APPLICATION_CREDENTIALS`
3. Test with `test_computer_vision.py` script
4. Make sure object is clearly visible in webcam

### Servo Not Moving

**Solutions:**
1. Check servo wiring (signal pin 10)
2. Check servo power (5V and GND)
3. Test servo directly: `servo.write(90)` in Arduino code
4. Check Serial Monitor for received commands

## Configuration

### Change Camera Index

If you have multiple cameras, edit `arduino_bridge.py`:

```python
CAMERA_INDEX = 1  # Change to 1, 2, etc.
```

### Change Server URL

If server is on different machine, edit `arduino_bridge.py`:

```python
SERVER_URL = "http://192.168.1.2:8000/api/vendo/capture-and-classify"
```

### Change Detection Distance

Edit `Arduino/vendo/vendo.ino`:

```cpp
const int RANGE_LIMIT = 50;  // cm - change detection distance
```

### Change Servo Positions

Edit `Arduino/vendo/vendo.ino`:

```cpp
const int PIPE_LEFT_POS    = 45;   // CAN bin (LEFT)
const int PIPE_RIGHT_POS   = 135;  // PLASTIC bin (RIGHT)
```

## Flow Diagram

```
1. User places object
   ↓
2. Ultrasonic detects (≤50cm)
   ↓
3. Arduino opens gate (5 seconds)
   ↓
4. Arduino sends "READY" via Serial
   ↓
5. PC Bridge receives "READY"
   ↓
6. PC captures webcam image
   ↓
7. PC sends HTTP POST to server
   ↓
8. Server classifies (Google Vision)
   ↓
9. Server returns: PLASTIC or CAN
   ↓
10. PC sends result via Serial
   ↓
11. Arduino receives result
   ↓
12. Arduino controls servo:
    - PLASTIC → RIGHT (135°)
    - CAN → LEFT (45°)
```

## Next Steps

1. ✅ Upload Arduino code
2. ✅ Install dependencies
3. ✅ Start FastAPI server
4. ✅ Run bridge script
5. ✅ Test full flow
6. ✅ Adjust servo positions if needed
7. ✅ Adjust detection distance if needed

## Support

For issues:
- Check Serial Monitor (Arduino)
- Check bridge script logs
- Check server logs
- Test components individually

