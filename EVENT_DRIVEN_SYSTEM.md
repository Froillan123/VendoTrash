# VendoTrash Event-Driven System Architecture

## Overview
The VendoTrash system uses an **event-driven architecture** where the ultrasonic sensor triggers the entire classification and sorting pipeline.

## Event Flow Diagram

```
┌─────────────────┐
│  Ultrasonic     │
│  Sensor (HC-SR04)│
│  Detects Object │
└────────┬────────┘
         │
         │ EVENT: Object detected (< 50cm)
         ▼
┌─────────────────┐
│   Arduino Uno    │
│   - Reads sensor │
│   - Sends "READY"│
└────────┬────────┘
         │
         │ Serial: "READY"
         ▼
┌─────────────────┐
│  PC Bridge      │
│  (arduino_bridge)│
│  - Receives event│
│  - Captures webcam│
└────────┬────────┘
         │
         │ HTTP POST (image_base64)
         ▼
┌─────────────────┐
│  FastAPI Server │
│  - Receives image│
│  - Google Vision │
│  - Classifies    │
└────────┬────────┘
         │
         │ Response: {material_type, confidence}
         ▼
┌─────────────────┐
│  PC Bridge      │
│  - Gets result  │
│  - Maps to command│
└────────┬────────┘
         │
         │ Serial: "PLASTIC" or "CAN"
         ▼
┌─────────────────┐
│   Arduino Uno   │
│   - Receives cmd │
│   - Controls servo│
│   - Sorts trash │
└─────────────────┘
```

## Event-Driven Steps

### 1. **Sensor Event** (Arduino)
- Ultrasonic sensor continuously monitors distance
- When object detected (< 50cm):
  - **Event Triggered**: `distance <= RANGE_LIMIT`
  - **Debounce**: 2-second delay prevents multiple triggers
  - **State**: `waitingForClassification = true`

### 2. **Serial Event** (Arduino → PC Bridge)
- Arduino sends: `"READY"` via Serial (9600 baud)
- PC Bridge receives event and processes it

### 3. **Camera Event** (PC Bridge)
- Bridge captures image from USB webcam
- Converts to base64 JPEG
- **Event-driven capture**: Only when "READY" received

### 4. **Vision API Event** (FastAPI Server)
- Receives HTTP POST with `image_base64`
- Calls Google Cloud Vision API
- Classifies: PLASTIC, NON_PLASTIC, or REJECTED
- Creates transaction in database
- Returns result with confidence

### 5. **Feedback Event** (PC Bridge → Arduino)
- Bridge maps result to Arduino command:
  - `PLASTIC` → `"PLASTIC"`
  - `NON_PLASTIC` → `"CAN"`
  - `REJECTED` → `"REJECTED"`
- Sends via Serial to Arduino

### 6. **Servo Control Event** (Arduino)
- Arduino receives command
- Controls servo motor:
  - `PLASTIC` → Move RIGHT (135°) → Return to center
  - `CAN` → Move LEFT (45°) → Return to center
  - `REJECTED` → No action (stay center)

## Key Features

### ✅ Event-Driven Benefits
- **No polling**: System only acts when object detected
- **Efficient**: Camera only captures when needed
- **Real-time**: Fast response to sensor events
- **Debounced**: Prevents duplicate triggers

### ✅ State Management
- Arduino tracks: `waitingForClassification`
- Prevents new detection while processing
- Resets after servo completes

### ✅ Error Handling
- Timeout protection (10 seconds for API calls)
- Error feedback to Arduino ("ERROR")
- Graceful degradation if webcam/server unavailable

## Code Locations

### Arduino Event Handler
```cpp
// Arduino/vendo/vendo_single_servo.ino
// Lines 80-94: Ultrasonic detection event
// Lines 97-136: Serial response event handler
```

### PC Bridge Event Handler
```python
# Server/arduino_bridge.py
# Lines 203-229: "READY" event processing
```

### Server Event Handler
```python
# Server/routes/vendo.py
# Lines 108-140: /capture-and-classify endpoint
# Server/controllers/vendo_controller.py
# Lines 130-163: capture_and_classify_trash function
```

## Troubleshooting

### COM Port Locked
```
Error: Access is denied
```
**Solution:**
1. Close Arduino IDE Serial Monitor
2. Close any other programs using COM6
3. Unplug and replug Arduino USB
4. Restart bridge script

### Webcam Not Available
```
Error: Failed to capture image
```
**Solution:**
1. Check webcam is connected
2. Close other apps using webcam (Camera, Zoom, Teams)
3. Check camera permissions in Windows

### Server Not Responding
```
Error: Server request timeout
```
**Solution:**
1. Check FastAPI server is running (`python main.py`)
2. Verify server URL: `http://localhost:8000`
3. Check network connectivity

## Testing the Event Flow

1. **Start FastAPI Server:**
   ```bash
   cd Server
   python main.py
   ```

2. **Start Arduino Bridge:**
   ```bash
   cd Server
   python arduino_bridge.py COM6
   ```

3. **Upload Arduino Code:**
   - Open `Arduino/vendo/vendo_single_servo.ino`
   - Upload to Arduino Uno
   - Close Serial Monitor (important!)

4. **Test Event:**
   - Place object in front of ultrasonic sensor
   - Watch logs for event flow:
     - `TRASH DETECTED!` (Arduino)
     - `EVENT: Object detected` (Bridge)
     - `Classification result: PLASTIC/CAN` (Server)
     - `Sorting complete!` (Arduino)

## Event Timing

- **Sensor Detection**: ~100ms (continuous loop)
- **Serial Communication**: ~10ms
- **Webcam Capture**: ~100-500ms
- **Vision API**: ~2-5 seconds
- **Servo Movement**: ~2 seconds
- **Total Event Cycle**: ~3-8 seconds

## Deployment Architecture

### MVP Deployment Strategy (Local)

For MVP, **local deployment is recommended** because the Arduino bridge requires direct hardware access.

```
┌─────────────────┐
│  Client (React) │ → Local dev server (localhost:5175)
└────────┬────────┘
         │ HTTP/WebSocket
         │
┌────────▼─────────────────┐
│  FastAPI (main.py)        │ → Local server (localhost:8000)
│  - Vision API             │
│  - Database (PostgreSQL)  │
│  - WebSocket              │
└────────┬──────────────────┘
         │ HTTPS
         │
┌────────▼──────────────────┐
│  arduino_bridge.py        │ → MUST STAY LOCAL ⚠️
│  - Serial (COM port)      │   Requires:
│  - USB Webcam             │   • Serial port access
│  - Local hardware         │   • USB webcam access
└────────┬──────────────────┘   • Persistent connection
         │ Serial (USB)
         │
┌────────▼────────┐
│  Arduino Uno    │ → Physical hardware
└─────────────────┘
```

### Why Bridge Cannot Deploy to Cloud Run

**❌ Cannot Deploy:**
- `arduino_bridge.py` requires:
  - Serial port access (COM port) - **local hardware only**
  - USB webcam access - **local hardware only**
  - Persistent connection - **not compatible with serverless**

**✅ Can Deploy:**
- `main.py` (FastAPI Server) → **Google Cloud Run** ✅
- Client (React) → **Vercel** ✅

### Cloud Deployment Options

#### Option 1: Hybrid Deployment (Recommended for Production)
```
Client → Vercel
FastAPI → Google Cloud Run
Bridge → Local (Raspberry Pi, PC, or Edge Device)
```

**Configuration:**
```python
# arduino_bridge.py - Update SERVER_BASE_URL
SERVER_BASE_URL = "https://your-app.run.app"  # Cloud Run URL
```

```typescript
// Client - Update API URL
VITE_API_URL=https://your-app.run.app
```

#### Option 2: Full Local Deployment (MVP)
```
Client → Local dev server (localhost:5175)
FastAPI → Local (localhost:8000)
Bridge → Same machine
```

**Best for:**
- MVP development
- Testing and prototyping
- Hardware integration

#### Option 3: IoT Platform (Advanced)
- Replace bridge with ESP32-CAM
- ESP32-CAM → Direct HTTP to Cloud Run
- No bridge script needed

## Servo Motor Power Troubleshooting

### Problem: Servo Not Moving

**Symptoms:**
- Arduino code sends commands correctly
- Serial Monitor shows: `>>> PLASTIC -> RIGHT` or `>>> CAN -> LEFT`
- Servo test sequence doesn't move on startup
- Servo physically doesn't move

### Root Cause: Insufficient Power

```
USB Power: 5V, 500mA (INSUFFICIENT!)
Servo Needs: 5V, 100-500mA+ (especially when moving)
```

**Why it happens:**
- USB port provides only 500mA
- Servo needs more current when moving (especially under load)
- Arduino + sensors also consume power
- Total power demand exceeds USB capacity

### Solutions

#### Option 1: External 5V Power Supply (Recommended)

**Setup:**
```
External 5V adapter (1A or higher)
  → Connect to Arduino VIN pin
  → Share GND with Arduino
  → Servo will get enough power!
```

**Wiring:**
- External adapter positive (+) → Arduino VIN pin
- External adapter negative (-) → Arduino GND (share with servo GND)
- Servo Red → Arduino 5V pin (stays connected)
- Servo Black → Arduino GND (shared)
- Servo Yellow → Pin 10 (stays connected)

**Benefits:**
- Provides sufficient current (1A+)
- Arduino regulates voltage automatically
- Simple setup

#### Option 2: Separate Servo Power Supply

**Setup:**
```
External 5V supply
  → Red wire → 5V+ (servo only)
  → Black wire → GND (share with Arduino GND!)
  → Yellow wire → Pin 10 (stay connected)
```

**Wiring:**
- External 5V+ → Servo Red wire (ONLY)
- External GND → Servo Black wire
- Arduino GND → Servo Black wire (SHARED GND - CRITICAL!)
- Arduino Pin 10 → Servo Yellow wire (signal)

**⚠️ IMPORTANT:** Always share GND between Arduino and external power supply!

#### Option 3: Arduino Barrel Jack (If Available)

**Setup:**
- Use Arduino with barrel jack connector
- Connect 7-12V adapter to barrel jack
- Arduino regulates to 5V internally
- Provides more power than USB

### Quick Diagnostic Test

1. **Upload Code:**
   - Upload `vendo_single_servo.ino` to Arduino
   - Open Serial Monitor (9600 baud)

2. **Check Servo Test Sequence:**
   - On startup, you should see:
     ```
     === SERVO TEST ===
     Servo test done!
     System Ready - Waiting for detection...
     ```
   - **If servo moves during test:** ✅ Power is sufficient
   - **If servo doesn't move:** ❌ Power issue - use external supply

3. **Check Serial Output:**
   - When object detected, Serial Monitor shows:
     ```
     >>> PLASTIC -> RIGHT
     Done!
     ```
   - **If commands appear but servo doesn't move:** Power issue

### Power Requirements by Component

| Component | Voltage | Current | Notes |
|-----------|---------|---------|-------|
| Arduino Uno | 5V | ~50mA | Base consumption |
| HC-SR04 Sensor | 5V | ~15mA | Low power |
| Servo Motor (idle) | 5V | ~100mA | Waiting |
| Servo Motor (moving) | 5V | 200-500mA+ | **Peak demand** |
| **Total (peak)** | 5V | **~565mA+** | **Exceeds USB 500mA!** |

### Voltage vs Current

**Common Misconception:**
- ❌ "Servo needs 7V" (usually not true)
- ✅ "Servo needs more current" (usually the issue)

**Standard Servos (SG90, MG90S):**
- Voltage: 4.8V-6V (5V typical) ✅
- Current: 100-500mA+ (depends on load) ⚠️

**High-Torque Servos:**
- Voltage: 6V-7.4V
- Current: 500mA-2A+
- Requires external power supply

### Troubleshooting Checklist

- [ ] Check servo wiring (Red→5V, Yellow→Pin 10, Black→GND)
- [ ] Verify servo test sequence runs on startup
- [ ] Check Serial Monitor for commands being sent
- [ ] Try external 5V power supply (1A+)
- [ ] Verify shared GND between Arduino and external supply
- [ ] Check servo model specifications (voltage/current requirements)
- [ ] Test servo with simple code (move to 90°, wait, return)

## Next Steps

- [ ] Add event logging to database
- [ ] Add event replay capability
- [ ] Add event statistics dashboard
- [ ] Optimize event processing time
- [ ] Set up Cloud Run deployment for FastAPI
- [ ] Set up Vercel deployment for Client
- [ ] Document external power supply setup


