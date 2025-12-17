#include <Servo.h>

// ---- PIN ASSIGNMENTS ----
const int trigPin       = 7;  // Ultrasonic TRIG
const int echoPin       = 8;  // Ultrasonic ECHO
const int capacitivePin = 2;  // Plastic sensor (digital)

Servo gateServo;              // Gate servo: opens/closes to drop trash
Servo pipeServo;              // Pipe servo: sorts LEFT (plastic) or RIGHT (non-plastic)

const int gateServoPin = 9;
const int pipeServoPin = 10;

// ---- CONFIG ----
const int RANGE_LIMIT      = 50;   // cm – distance to detect trash at gate
const int GATE_OPEN        = 90;
const int GATE_CLOSE       = 0;
// Sorting servo positions (tune these for your bins)
const int PIPE_CENTER_POS  = 90;   // Idle / middle
const int PIPE_LEFT_POS    = 45;   // Plastic bin (LEFT)
const int PIPE_RIGHT_POS   = 135;  // Non-plastic bin (RIGHT)

// ---- VARIABLES ----
long duration;
int distance;

void setup() {
  Serial.begin(9600);

  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);
  pinMode(capacitivePin, INPUT);

  gateServo.attach(gateServoPin);
  pipeServo.attach(pipeServoPin);

  gateServo.write(GATE_CLOSE);    // Start closed
  pipeServo.write(PIPE_CENTER_POS);  // Start in center

  Serial.println("SYSTEM READY - PLASTIC vs NON-PLASTIC");
}

void loop() {
  static bool sortingPending = false;   // TRUE when one trash item has just fallen
  // ---------------- GATE TRIGGER (ULTRASONIC) ----------------
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);

  duration = pulseIn(echoPin, HIGH);
  distance = duration * 0.034 / 2;

  // STEP 1: Ultrasonic detects trash -> open gate
  if (distance > 0 && distance <= RANGE_LIMIT) {
    Serial.println("TRASH DETECTED: OPENING GATE");
    gateServo.write(GATE_OPEN);
    delay(5000);              // Wait for trash to fall
    gateServo.write(GATE_CLOSE);
    delay(1000);              // Small delay before sensor stage

    // One trash item has just passed to the sensor stage
    sortingPending = true;
  }

  // ---------------- SENSOR STAGE (PLASTIC vs NON-PLASTIC) ----------------
  // Only run once per detected trash item
  if (sortingPending) {
    // Take multiple samples from capacitive sensor for stability
    const int samples = 5;
    int highCount = 0;
    for (int i = 0; i < samples; i++) {
      if (digitalRead(capacitivePin) == HIGH) {
        highCount++;
      }
      delay(50);
    }

    bool plasticDetected = (highCount >= 3);  // majority of samples HIGH

    if (plasticDetected) {
      Serial.println("PLASTIC DETECTED -> LEFT");
      pipeServo.write(PIPE_LEFT_POS);
      delay(1000);
      pipeServo.write(PIPE_CENTER_POS);
    } else {
      Serial.println("NON-PLASTIC DETECTED -> RIGHT");
      pipeServo.write(PIPE_RIGHT_POS);
      delay(1000);
      pipeServo.write(PIPE_CENTER_POS);
    }

    // Finish this sorting cycle
    sortingPending = false;
  }

  // Small loop delay
  delay(100);
}