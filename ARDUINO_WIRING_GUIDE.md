# Arduino Uno Wiring Guide

Complete pin connection guide for VendoTrash Arduino system.

## Pin Assignments

| Component | Connection | Arduino Pin |
|-----------|------------|-------------|
| HC-SR04 VCC | Power | 5V |
| HC-SR04 GND | Ground | GND |
| HC-SR04 TRIG | Trigger | Pin 7 |
| HC-SR04 ECHO | Echo | Pin 8 |
| Servo VCC | Power | 5V |
| Servo GND | Ground | GND |
| Servo Signal | Control | Pin 10 |
| Arduino USB | Data | PC USB Port |

## Wiring Diagram (Mermaid)

```mermaid
graph TB
    subgraph "Arduino Uno"
        A[Arduino Uno]
        P7[Pin 7 - TRIG]
        P8[Pin 8 - ECHO]
        P10[Pin 10 - Servo Signal]
        V5V[5V Power]
        GND[GND Ground]
        USB[USB Port]
    end
    
    subgraph "HC-SR04 Ultrasonic Sensor"
        H1[VCC]
        H2[TRIG]
        H3[ECHO]
        H4[GND]
    end
    
    subgraph "Servo Motor"
        S1[Red - VCC]
        S2[Yellow/Orange - Signal]
        S3[Black - GND]
    end
    
    subgraph "PC"
        PC[Computer USB Port]
    end
    
    P7 -->|Digital Output| H2
    P8 -->|Digital Input| H3
    P10 -->|PWM Signal| S2
    V5V -->|Power| H1
    V5V -->|Power| S1
    GND -->|Ground| H4
    GND -->|Ground| S3
    USB -->|Serial Communication| PC
    
    style A fill:#4CAF50,stroke:#333,stroke-width:3px
    style H1 fill:#FF9800,stroke:#333,stroke-width:2px
    style H2 fill:#FF9800,stroke:#333,stroke-width:2px
    style H3 fill:#FF9800,stroke:#333,stroke-width:2px
    style H4 fill:#FF9800,stroke:#333,stroke-width:2px
    style S1 fill:#2196F3,stroke:#333,stroke-width:2px
    style S2 fill:#2196F3,stroke:#333,stroke-width:2px
    style S3 fill:#2196F3,stroke:#333,stroke-width:2px
    style PC fill:#9C27B0,stroke:#333,stroke-width:2px
```

## Connection Flow Diagram

```mermaid
flowchart LR
    subgraph "Hardware Layer"
        US[Ultrasonic Sensor<br/>HC-SR04]
        SM[Servo Motor]
        AU[Arduino Uno]
    end
    
    subgraph "Communication"
        USB[USB Serial<br/>9600 baud]
    end
    
    subgraph "PC Layer"
        PC[PC Bridge Script<br/>arduino_bridge.py]
        WC[USB Webcam]
    end
    
    subgraph "Server Layer"
        FS[FastAPI Server<br/>localhost:8000]
        GV[Google Vision API]
    end
    
    US -->|Detects Object| AU
    AU -->|Sends 'READY'| USB
    USB -->|Serial Data| PC
    PC -->|Captures Image| WC
    PC -->|HTTP POST| FS
    FS -->|Classify| GV
    GV -->|Result| FS
    FS -->|Response| PC
    PC -->|Sends 'PLASTIC' or 'CAN'| USB
    USB -->|Serial Data| AU
    AU -->|Controls| SM
    
    style US fill:#FF9800
    style SM fill:#2196F3
    style AU fill:#4CAF50
    style PC fill:#9C27B0
    style FS fill:#F44336
    style GV fill:#00BCD4
```

## Detailed Component Connections

### HC-SR04 Ultrasonic Sensor

```mermaid
graph LR
    subgraph "HC-SR04 Sensor"
        VCC[VCC - Pin 1]
        TRIG[TRIG - Pin 2]
        ECHO[ECHO - Pin 3]
        GND[GND - Pin 4]
    end
    
    subgraph "Arduino Uno"
        A5V[5V]
        A7[Pin 7]
        A8[Pin 8]
        AGND[GND]
    end
    
    VCC -->|Red Wire| A5V
    TRIG -->|Yellow Wire| A7
    ECHO -->|Green Wire| A8
    GND -->|Black Wire| AGND
    
    style VCC fill:#FF5722
    style TRIG fill:#FFC107
    style ECHO fill:#4CAF50
    style GND fill:#212121
```

### Servo Motor

```mermaid
graph LR
    subgraph "Servo Motor"
        SVCC[Red Wire - VCC]
        SSIG[Yellow/Orange - Signal]
        SGND[Black Wire - GND]
    end
    
    subgraph "Arduino Uno"
        A5V2[5V]
        A10[Pin 10]
        AGND2[GND]
    end
    
    SVCC -->|Power| A5V2
    SSIG -->|PWM Control| A10
    SGND -->|Ground| AGND2
    
    style SVCC fill:#F44336
    style SSIG fill:#FFC107
    style SGND fill:#212121
```

## System Architecture

```mermaid
sequenceDiagram
    participant User
    participant US as Ultrasonic Sensor
    participant AU as Arduino Uno
    participant PC as PC Bridge Script
    participant WC as USB Webcam
    participant FS as FastAPI Server
    participant GV as Google Vision API
    participant SM as Servo Motor
    
    User->>US: Places object
    US->>AU: Detects object (≤50cm)
    AU->>AU: Opens gate (5 seconds)
    AU->>PC: Serial: "READY\n"
    PC->>WC: Capture image
    WC-->>PC: Image data
    PC->>FS: HTTP POST /capture-and-classify
    FS->>GV: Classify image
    GV-->>FS: PLASTIC or CAN
    FS->>FS: Create transaction
    FS-->>PC: {"material_type": "PLASTIC"}
    PC->>AU: Serial: "PLASTIC\n"
    AU->>SM: Move RIGHT (135°)
    SM-->>AU: Position reached
    AU->>SM: Return to center (90°)
    AU->>PC: Ready for next detection
```

## Physical Layout

```mermaid
graph TB
    subgraph "Top View - Component Layout"
        direction TB
        US_POS[Ultrasonic Sensor<br/>Facing forward<br/>HC-SR04]
        GATE[Gate Servo<br/>Pin 9<br/>Opens/Closes gate]
        SORT[Sorting Servo<br/>Pin 10<br/>LEFT/RIGHT sorting]
    end
    
    subgraph "Side View - Object Flow"
        direction LR
        IN[Object Inserted]
        DETECT[Ultrasonic Detects]
        GATE_OPEN[Gate Opens]
        DROP[Object Drops]
        CAM[Webcam Captures]
        CLASSIFY[Server Classifies]
        SORT_LEFT[Sort LEFT - CAN]
        SORT_RIGHT[Sort RIGHT - PLASTIC]
    end
    
    IN --> DETECT
    DETECT --> GATE_OPEN
    GATE_OPEN --> DROP
    DROP --> CAM
    CAM --> CLASSIFY
    CLASSIFY -->|CAN| SORT_LEFT
    CLASSIFY -->|PLASTIC| SORT_RIGHT
```

## Power Distribution

```mermaid
graph TB
    subgraph "Power Source"
        USB_PWR[USB Power<br/>5V, 500mA]
    end
    
    subgraph "Arduino Uno"
        REG[5V Regulator]
        V5V[5V Pin]
        GND_PIN[GND Pin]
    end
    
    subgraph "Components"
        US_PWR[HC-SR04<br/>5V, ~15mA]
        SERVO_PWR[Servo Motor<br/>5V, ~100-500mA]
    end
    
    USB_PWR --> REG
    REG --> V5V
    V5V --> US_PWR
    V5V --> SERVO_PWR
    GND_PIN --> US_PWR
    GND_PIN --> SERVO_PWR
    
    style USB_PWR fill:#4CAF50
    style REG fill:#FF9800
    style V5V fill:#F44336
    style GND_PIN fill:#212121
```

## Sorting Logic

```mermaid
graph TD
    START[Object Detected] --> ULTRASONIC[Ultrasonic Sensor<br/>Distance ≤ 50cm]
    ULTRASONIC --> GATE[Open Gate<br/>5 seconds]
    GATE --> SERIAL[Send 'READY'<br/>via Serial]
    SERIAL --> WEBCAM[PC Captures<br/>Webcam Image]
    WEBCAM --> SERVER[Server Classifies<br/>Google Vision API]
    SERVER --> DECISION{Classification<br/>Result?}
    DECISION -->|PLASTIC| PLASTIC_CMD[Send 'PLASTIC'<br/>via Serial]
    DECISION -->|CAN| CAN_CMD[Send 'CAN'<br/>via Serial]
    DECISION -->|REJECTED| REJECT_CMD[Send 'REJECTED'<br/>via Serial]
    PLASTIC_CMD --> SERVO_RIGHT[Servo RIGHT<br/>135° - PLASTIC bin]
    CAN_CMD --> SERVO_LEFT[Servo LEFT<br/>45° - CAN bin]
    REJECT_CMD --> NO_ACTION[No Action]
    SERVO_RIGHT --> CENTER[Return to Center<br/>90°]
    SERVO_LEFT --> CENTER
    NO_ACTION --> CENTER
    CENTER --> WAIT[Wait for next<br/>detection]
    
    style START fill:#4CAF50
    style DECISION fill:#FF9800
    style PLASTIC_CMD fill:#2196F3
    style CAN_CMD fill:#FFC107
    style REJECT_CMD fill:#F44336
    style SERVO_RIGHT fill:#2196F3
    style SERVO_LEFT fill:#FFC107
```

## Pin Functions Summary

```mermaid
mindmap
  root((Arduino Uno<br/>Pin Functions))
    Digital Pins
      Pin 7
        TRIG Output
        HC-SR04 Trigger
      Pin 8
        ECHO Input
        HC-SR04 Echo
      Pin 9
        Gate Servo
        PWM Control
      Pin 10
        Sorting Servo
        PWM Control
    Power
      5V
        HC-SR04 VCC
        Servo VCC
      GND
        Common Ground
        All Components
    Communication
      USB
        Serial 9600
        PC Bridge
```

## Troubleshooting Flow

```mermaid
flowchart TD
    START[System Not Working?] --> CHECK1{Arduino<br/>Detected?}
    CHECK1 -->|No| USB_CHECK[Check USB Connection]
    USB_CHECK --> DRIVER[Install Arduino Drivers]
    DRIVER --> CHECK1
    CHECK1 -->|Yes| CHECK2{Serial<br/>Communication?}
    CHECK2 -->|No| BAUD[Check Baud Rate: 9600]
    BAUD --> PORT[Check COM Port]
    PORT --> CHECK2
    CHECK2 -->|Yes| CHECK3{Webcam<br/>Working?}
    CHECK3 -->|No| CLOSE_APPS[Close Other Apps]
    CLOSE_APPS --> TEST_CAM[Test in Camera App]
    TEST_CAM --> CHECK3
    CHECK3 -->|Yes| CHECK4{Server<br/>Running?}
    CHECK4 -->|No| START_SERVER[Start: python main.py]
    START_SERVER --> CHECK4
    CHECK4 -->|Yes| CHECK5{Servo<br/>Moving?}
    CHECK5 -->|No| SERVO_WIRING[Check Servo Wiring]
    SERVO_WIRING --> SERVO_POWER[Check Power Supply]
    SERVO_POWER --> CHECK5
    CHECK5 -->|Yes| WORKING[System Working!]
    
    style START fill:#F44336
    style WORKING fill:#4CAF50
```

## Quick Reference Card

### Pin Connections (One Page)

```
┌─────────────────────────────────────────┐
│         ARDUINO UNO PINOUT              │
├─────────────────────────────────────────┤
│                                         │
│  [5V] ──────► HC-SR04 VCC               │
│  [5V] ──────► Servo Red (VCC)          │
│                                         │
│  [GND] ─────► HC-SR04 GND               │
│  [GND] ─────► Servo Black (GND)        │
│                                         │
│  [Pin 7] ───► HC-SR04 TRIG             │
│  [Pin 8] ───► HC-SR04 ECHO             │
│  [Pin 10] ──► Servo Yellow (Signal)    │
│                                         │
│  [USB] ─────► PC (Serial Communication)│
│                                         │
└─────────────────────────────────────────┘
```

## Notes

- **Power**: Arduino USB provides 5V, 500mA. For high-torque servos, use external 5V power supply.
- **Ground**: Always connect all GND pins together (common ground).
- **Servo Signal**: Pin 10 uses PWM (Pulse Width Modulation) for servo control.
- **Serial**: USB connection uses 9600 baud rate for communication.
- **Detection Range**: Ultrasonic sensor detects objects within 50cm (configurable in code).

## Next Steps

1. ✅ Connect all wires according to diagram
2. ✅ Upload Arduino code
3. ✅ Test Serial communication
4. ✅ Run bridge script
5. ✅ Test full system

