/*
 * VendoTrash Arduino Code - Single Servo Version
 * Server-Side Camera Classification System
 * 
 * Wiring:
 * - HC-SR04: VCC→5V, TRIG→Pin 7, ECHO→Pin 8, GND→GND
 * - Servo: Red→5V, Yellow→Pin 10, Black→GND
 * 
 * Flow:
 * 1. Ultrasonic sensor detects object
 * 2. Arduino sends "READY" via Serial to PC
 * 3. PC captures webcam image and sends to server
 * 4. Server classifies using Google Vision API
 * 5. PC sends result back via Serial: "PLASTIC" or "CAN"
 * 6. Arduino controls servo motor (sorting only)
 */

#include <Servo.h>

// ---- PIN ASSIGNMENTS (Matches your wiring diagram) ----
const int trigPin       = 7;   // HC-SR04 TRIG → Pin 7
const int echoPin       = 8;   // HC-SR04 ECHO → Pin 8

Servo sortingServo;            // Sorting servo (only one servo)

const int sortingServoPin = 10; // Servo Signal → Pin 10

// ---- CONFIG ----
const int RANGE_LIMIT      = 30;   // cm - detection distance (reduced from 50 to avoid false triggers)
const int MIN_DISTANCE     = 5;    // cm - minimum distance to ignore noise

const int SERVO_CENTER_POS = 90;   // Idle / middle position
const int SERVO_LEFT_POS   = 45;   // CAN bin (LEFT)
const int SERVO_RIGHT_POS  = 135;  // PLASTIC bin (RIGHT)

// ---- VARIABLES ----
long duration;
int distance;
char serialInput[20] = "";  // Use char array instead of String to save memory
bool waitingForClassification = false;

// Event-driven debouncing - IMPROVED
unsigned long lastDetectionTime = 0;
const unsigned long DEBOUNCE_DELAY = 5000;  // 5 seconds between detections (increased)
int consecutiveDetections = 0;  // Count consecutive detections to avoid false triggers
const int REQUIRED_DETECTIONS = 3;  // Need 3 consecutive detections to trigger

// Timeout for waiting for classification response
unsigned long classificationStartTime = 0;
const unsigned long CLASSIFICATION_TIMEOUT = 30000;  // 30 seconds timeout

void setup() {
  Serial.begin(9600);
  while (!Serial) {
    ; // Wait for serial port to connect (only needed for some boards)
  }

  // Configure ultrasonic sensor pins
  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);

  // Attach servo to pin 10
  sortingServo.attach(sortingServoPin);
  delay(500);  // Give servo time to initialize

  // SERVO TEST SEQUENCE - Verify servo is working (reduced output to save memory)
  Serial.println(F("=== SERVO TEST ==="));
  sortingServo.write(SERVO_CENTER_POS);
  delay(1000);
  sortingServo.write(SERVO_LEFT_POS);
  delay(2000);
  sortingServo.write(SERVO_CENTER_POS);
  delay(1000);
  sortingServo.write(SERVO_RIGHT_POS);
  delay(2000);
  sortingServo.write(SERVO_CENTER_POS);
  delay(1000);
  Serial.println(F("Servo test done!"));
  Serial.println(F("System Ready - Waiting for detection..."));
}

void loop() {
  // ---------------- ULTRASONIC SENSOR READING ----------------
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);

  duration = pulseIn(echoPin, HIGH);
  distance = duration * 0.034 / 2;

  // ------- STEP 1: Event-driven detection -> send READY to PC -------
  // IMPROVED: Better debouncing to avoid false triggers
  unsigned long currentTime = millis();
  bool debounceOk = (currentTime - lastDetectionTime) >= DEBOUNCE_DELAY;
  
  // Check if object is in valid range (not too close, not too far)
  bool validDistance = (distance >= MIN_DISTANCE && distance <= RANGE_LIMIT);
  
  if (validDistance && !waitingForClassification && debounceOk) {
    consecutiveDetections++;
    
    // Only trigger after multiple consecutive detections (avoid false positives)
    if (consecutiveDetections >= REQUIRED_DETECTIONS) {
      Serial.print(F("TRASH DETECTED! Distance: "));
      Serial.print(distance);
      Serial.println(F(" cm"));
      Serial.println(F("READY"));
      
      waitingForClassification = true;
      classificationStartTime = currentTime;  // Record when we started waiting
      lastDetectionTime = currentTime;  // Update debounce timer
      consecutiveDetections = 0;  // Reset counter
    } else {
      // Log detection but don't trigger yet (reduced output to save memory)
      // Serial.print(F("Det #")); Serial.print(consecutiveDetections); Serial.print(F("/")); Serial.print(REQUIRED_DETECTIONS); Serial.print(F(" - ")); Serial.print(distance); Serial.println(F("cm"));
    }
  } else {
    // Reset counter if no valid detection
    if (!validDistance || !debounceOk) {
      consecutiveDetections = 0;
    }
  }

  // ---------------- CHECK FOR TIMEOUT ----------------
  if (waitingForClassification) {
    unsigned long currentTime = millis();
    if (currentTime - classificationStartTime > CLASSIFICATION_TIMEOUT) {
      Serial.println(F("TIMEOUT - Resetting..."));
      waitingForClassification = false;
      serialInput[0] = '\0';  // Clear string
    }
  }

  // ---------------- CHECK FOR SERIAL RESPONSE FROM PC ----------------
  if (Serial.available() > 0 && waitingForClassification) {
    int len = Serial.readBytesUntil('\n', serialInput, sizeof(serialInput) - 1);
    serialInput[len] = '\0';  // Null terminate
    
    // Convert to uppercase and trim whitespace
    for (int i = 0; i < len; i++) {
      if (serialInput[i] >= 'a' && serialInput[i] <= 'z') {
        serialInput[i] = serialInput[i] - 32;  // Convert to uppercase
      }
      if (serialInput[i] == '\r' || serialInput[i] == '\n') {
        serialInput[i] = '\0';
        len = i;
        break;
      }
    }
    // Trim trailing spaces
    while (len > 0 && serialInput[len-1] == ' ') {
      serialInput[--len] = '\0';
    }

    Serial.print(F("Received: "));
    Serial.println(serialInput);

    // ------- STEP 2: Receive classification and sort -------
    if (strcmp(serialInput, "PLASTIC") == 0) {
      Serial.println(F(">>> PLASTIC -> RIGHT"));
      sortingServo.write(SERVO_RIGHT_POS);  // Move RIGHT (135°)
      delay(2000);  // Hold position for 2 seconds
      sortingServo.write(SERVO_CENTER_POS); // Return to center
      delay(500);  // Give servo time to return
      Serial.println(F("Done!"));
      
    } else if (strcmp(serialInput, "CAN") == 0 || strcmp(serialInput, "NON_PLASTIC") == 0) {
      Serial.println(F(">>> CAN -> LEFT"));
      sortingServo.write(SERVO_LEFT_POS);   // Move LEFT (45°)
      delay(2000);  // Hold position for 2 seconds
      sortingServo.write(SERVO_CENTER_POS); // Return to center
      delay(500);  // Give servo time to return
      Serial.println(F("Done!"));
      
    } else if (strcmp(serialInput, "REJECTED") == 0 || strcmp(serialInput, "ERROR") == 0) {
      Serial.println(F(">>> REJECTED - No action"));
      // Servo stays at center position
      
    } else if (strcmp(serialInput, "NO_SESSION") == 0) {
      Serial.println(F(">>> NO_SESSION - Click Insert Trash first"));
      // Servo stays at center position
      
    } else {
      Serial.print(F(">>> Unknown: "));
      Serial.println(serialInput);
    }

    Serial.println(F("Ready for next..."));
    
    waitingForClassification = false;
    serialInput[0] = '\0';  // Clear string
  }

  delay(100);  // Small delay to prevent CPU spinning
}

