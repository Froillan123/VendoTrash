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

## Next Steps

- [ ] Add event logging to database
- [ ] Add event replay capability
- [ ] Add event statistics dashboard
- [ ] Optimize event processing time


