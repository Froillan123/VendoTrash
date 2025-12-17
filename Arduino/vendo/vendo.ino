/*
 * VendoTrash Arduino Code
 * Server-Side Camera Classification System
 * 
 * Flow:
 * 1. Ultrasonic sensor detects object
 * 2. Arduino sends "READY" via Serial to PC
 * 3. PC captures webcam image and sends to server
 * 4. Server classifies using Google Vision API
 * 5. PC sends result back via Serial: "PLASTIC" or "CAN"
 * 6. Arduino controls servo motor
 */

#include <Servo.h>

// ---- PIN ASSIGNMENTS ----
const int trigPin       = 7;   // Ultrasonic TRIG
const int echoPin       = 8;   // Ultrasonic ECHO

Servo gateServo;               // Gate servo
Servo pipeServo;               // Sorting servo

const int gateServoPin  = 9;
const int pipeServoPin  = 10;

// ---- CONFIG ----
const int RANGE_LIMIT      = 50;   // cm - detection distance
const int GATE_OPEN        = 90;
const int GATE_CLOSE       = 0;

const int PIPE_CENTER_POS  = 90;   // Idle / middle position
const int PIPE_LEFT_POS    = 45;   // CAN bin (LEFT)
const int PIPE_RIGHT_POS   = 135;  // PLASTIC bin (RIGHT)

// ---- VARIABLES ----
long duration;
int distance;
String serialInput = "";
bool waitingForClassification = false;

void setup() {
  Serial.begin(9600);
  while (!Serial) {
    ; // Wait for serial port to connect
  }

  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);

  gateServo.attach(gateServoPin);
  pipeServo.attach(pipeServoPin);

  gateServo.write(GATE_CLOSE);
  pipeServo.write(PIPE_CENTER_POS);

  Serial.println("========================================");
  Serial.println("VendoTrash System Ready");
  Serial.println("Server-Side Camera Classification");
  Serial.println("========================================");
  Serial.println("Waiting for object detection...");
}

void loop() {
  // ---------------- ULTRASONIC TRIGGER ----------------
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);

  duration = pulseIn(echoPin, HIGH);
  distance = duration * 0.034 / 2;

  // ------- STEP 1: Object detected -> open gate -------
  if (distance > 0 && distance <= RANGE_LIMIT && !waitingForClassification) {
    Serial.println("========================================");
    Serial.println("TRASH DETECTED!");
    Serial.print("Distance: ");
    Serial.print(distance);
    Serial.println(" cm");
    Serial.println("Opening gate...");

    gateServo.write(GATE_OPEN);
    delay(5000);        // Drop trash (5 seconds)
    gateServo.write(GATE_CLOSE);
    delay(1000);        // Allow trash to settle

    Serial.println("Gate closed. Sending READY to PC...");
    Serial.println("READY");  // Send trigger to PC bridge script
    Serial.println("Waiting for classification result...");
    
    waitingForClassification = true;
  }

  // ---------------- CHECK FOR SERIAL RESPONSE FROM PC ----------------
  if (Serial.available() > 0 && waitingForClassification) {
    serialInput = Serial.readStringUntil('\n');
    serialInput.trim();
    serialInput.toUpperCase();

    Serial.print("Received from PC: ");
    Serial.println(serialInput);

    // ------- STEP 2: Receive classification and sort -------
    if (serialInput == "PLASTIC") {
      Serial.println(">>> PLASTIC detected -> Moving to RIGHT bin");
      pipeServo.write(PIPE_RIGHT_POS);
      delay(2000);  // Hold position for 2 seconds
      pipeServo.write(PIPE_CENTER_POS);
      Serial.println("Sorting complete!");
      
    } else if (serialInput == "CAN" || serialInput == "NON_PLASTIC") {
      Serial.println(">>> CAN detected -> Moving to LEFT bin");
      pipeServo.write(PIPE_LEFT_POS);
      delay(2000);  // Hold position for 2 seconds
      pipeServo.write(PIPE_CENTER_POS);
      Serial.println("Sorting complete!");
      
    } else if (serialInput == "REJECTED" || serialInput == "ERROR") {
      Serial.println(">>> Item REJECTED or ERROR occurred");
      Serial.println("No sorting action taken.");
      
    } else {
      Serial.print(">>> Unknown response: ");
      Serial.println(serialInput);
    }

    Serial.println("========================================");
    Serial.println("Ready for next detection...");
    Serial.println();
    
    waitingForClassification = false;
    serialInput = "";
  }

  delay(100);  // Small delay to prevent CPU spinning
}