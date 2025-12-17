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
const int RANGE_LIMIT      = 50;   // cm - detection distance

const int SERVO_CENTER_POS = 90;   // Idle / middle position
const int SERVO_LEFT_POS   = 45;   // CAN bin (LEFT)
const int SERVO_RIGHT_POS  = 135;  // PLASTIC bin (RIGHT)

// ---- VARIABLES ----
long duration;
int distance;
String serialInput = "";
bool waitingForClassification = false;

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

  // Start at center position
  sortingServo.write(SERVO_CENTER_POS);

  Serial.println("========================================");
  Serial.println("VendoTrash System Ready");
  Serial.println("Server-Side Camera Classification");
  Serial.println("Single Servo Version");
  Serial.println("========================================");
  Serial.println("Wiring:");
  Serial.println("  HC-SR04: TRIG→Pin 7, ECHO→Pin 8");
  Serial.println("  Servo: Signal→Pin 10");
  Serial.println("========================================");
  Serial.println("Waiting for object detection...");
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

  // ------- STEP 1: Object detected -> send READY to PC -------
  if (distance > 0 && distance <= RANGE_LIMIT && !waitingForClassification) {
    Serial.println("========================================");
    Serial.println("TRASH DETECTED!");
    Serial.print("Distance: ");
    Serial.print(distance);
    Serial.println(" cm");
    Serial.println("Sending READY to PC...");

    // Send trigger to PC bridge script
    Serial.println("READY");
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
      sortingServo.write(SERVO_RIGHT_POS);  // Move RIGHT (135°)
      delay(2000);  // Hold position for 2 seconds
      sortingServo.write(SERVO_CENTER_POS); // Return to center
      Serial.println("Sorting complete!");
      
    } else if (serialInput == "CAN" || serialInput == "NON_PLASTIC") {
      Serial.println(">>> CAN detected -> Moving to LEFT bin");
      sortingServo.write(SERVO_LEFT_POS);   // Move LEFT (45°)
      delay(2000);  // Hold position for 2 seconds
      sortingServo.write(SERVO_CENTER_POS); // Return to center
      Serial.println("Sorting complete!");
      
    } else if (serialInput == "REJECTED" || serialInput == "ERROR") {
      Serial.println(">>> Item REJECTED or ERROR occurred");
      Serial.println("No sorting action taken.");
      // Servo stays at center position
      
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

