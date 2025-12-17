#include <Servo.h>

// ---- PIN ASSIGNMENTS ----
const int trigPin       = 7;   // Ultrasonic TRIG
const int echoPin       = 8;   // Ultrasonic ECHO
const int capacitivePin = 2;   // Plastic sensor (HIGH = plastic)

Servo gateServo;               // Gate servo
Servo pipeServo;               // Sorting servo

const int gateServoPin  = 9;
const int pipeServoPin  = 10;

// ---- CONFIG ----
const int RANGE_LIMIT      = 50;   // cm
const int GATE_OPEN        = 90;
const int GATE_CLOSE       = 0;

const int PIPE_CENTER_POS  = 90;   // Idle / middle
const int PIPE_LEFT_POS    = 45;   // Plastic bin
const int PIPE_RIGHT_POS   = 135;  // Non‑plastic bin

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

  gateServo.write(GATE_CLOSE);
  pipeServo.write(PIPE_CENTER_POS);

  Serial.println("SYSTEM READY - PLASTIC vs NON-PLASTIC");
}

void loop() {

  static bool sortingPending = false;

  // ---------------- ULTRASONIC TRIGGER ----------------
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);

  duration = pulseIn(echoPin, HIGH);
  distance = duration * 0.034 / 2;

  // ------- STEP 1: Object detected -> open gate -------
  if (distance > 0 && distance <= RANGE_LIMIT) {

    Serial.println("TRASH DETECTED: OPENING GATE");

    gateServo.write(GATE_OPEN);
    delay(5000);        // drop trash
    gateServo.write(GATE_CLOSE);
    delay(1000);        // allow trash to reach sensor

    sortingPending = true;
  }

  // ---------------- SENSOR STAGE ----------------
  if (sortingPending) {

    // NEW LOGIC → HIGH = plastic, LOW = non‑plastic
    bool plasticDetected = (digitalRead(capacitivePin) == HIGH);

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

    sortingPending = false;
  }

  delay(100);
}