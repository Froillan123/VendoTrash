#include <ESP32Servo.h>
#include <WiFi.h>
#include <WiFiManager.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>

// Pin definitions
#define IR_SENSOR_PIN 34        // IR sensor digital output
#define INDUCTIVE_SENSOR_PIN 35 // LJC18A3 inductive sensor output
#define SERVO_PIN 18            // Servo control pin
#define TRIG_PIN 25             // Ultrasonic sensor trigger pin
#define ECHO_PIN 26             // Ultrasonic sensor echo pin

Servo myServo;
WiFiManager wifiManager;

// Firebase configuration
const char* FIREBASE_HOST = "https://mabote-a3dc2-default-rtdb.firebaseio.com";
const char* FIREBASE_AUTH = "pYGwGH9oEIjICWlknA570Ze4gyA6cQetmw5EJKwa";
const char* BIN_ID = "bin_10";

// Servo positions
const int BOTTLE_POSITION = 180;
const int METAL_POSITION = 0;
const int CENTER_POSITION = 90;

// Ultrasonic sensor settings
const int BIN_FULL_DISTANCE = 10;
const int BIN_DEPTH = 50;

// FreeRTOS task handles
TaskHandle_t sensorTaskHandle = NULL;
TaskHandle_t servoTaskHandle = NULL;
TaskHandle_t firebaseTaskHandle = NULL;
TaskHandle_t binCheckTaskHandle = NULL;

// Shared variables (protected by semaphores/mutexes)
SemaphoreHandle_t xServoMutex;
SemaphoreHandle_t xFirebaseMutex;

// Servo control queue
QueueHandle_t servoQueue;

// Servo command structure
enum ServoCommand {
  SERVO_BOTTLE,
  SERVO_METAL,
  SERVO_CENTER
};

// Shared state variables
volatile bool sensorReady = false;
volatile bool binIsFull = false;
volatile bool sensorsLocked = false;
int currentPoints = 0;
int bottleCount = 0;  
int metalCount = 0;  
String userUid = "";

// Timing variables
unsigned long lastDetectionTime = 0;
const unsigned long DEBOUNCE_DELAY = 100;
const unsigned long STABILIZATION_DELAY = 1000; // 1 second wait before reading sensors

// Detection state tracking
bool objectPresent = false;
unsigned long objectDetectedTime = 0;

void setup() {
  // Initialize pins
  pinMode(IR_SENSOR_PIN, INPUT);
  pinMode(INDUCTIVE_SENSOR_PIN, INPUT);
  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);
  
  // Attach and initialize servo
  myServo.attach(SERVO_PIN);
  myServo.write(CENTER_POSITION);
  
  // WiFiManager setup
  wifiManager.setConfigPortalTimeout(180);
  String apName = "Mabote.ph";
  
  if (!wifiManager.autoConnect(apName.c_str())) {
    delay(3000);
    ESP.restart();
  }
  
  // Create mutexes
  xServoMutex = xSemaphoreCreateMutex();
  xFirebaseMutex = xSemaphoreCreateMutex();
  
  // Create servo command queue
  servoQueue = xQueueCreate(10, sizeof(ServoCommand));
  
  // Create FreeRTOS tasks
  xTaskCreatePinnedToCore(
    sensorTask,
    "SensorTask",
    4096,
    NULL,
    3,
    &sensorTaskHandle,
    0
  );
  
  xTaskCreatePinnedToCore(
    servoTask,
    "ServoTask",
    4096,
    NULL,
    3,
    &servoTaskHandle,
    0
  );
  
  xTaskCreatePinnedToCore(
    firebaseTask,
    "FirebaseTask",
    8192,
    NULL,
    2,
    &firebaseTaskHandle,
    1
  );
  
  xTaskCreatePinnedToCore(
    binCheckTask,
    "BinCheckTask",
    4096,
    NULL,
    1,
    &binCheckTaskHandle,
    1
  );
  
  delay(1000);
}

void loop() {
  // Empty - FreeRTOS tasks handle everything
  vTaskDelay(1000 / portTICK_PERIOD_MS);
}

// Task 1: Sensor Reading (High Priority, Core 0)
void sensorTask(void *parameter) {
  while (1) {
    if (sensorReady && !binIsFull && !sensorsLocked) {
      
      int irValue = digitalRead(IR_SENSOR_PIN);
      int inductiveValue = digitalRead(INDUCTIVE_SENSOR_PIN);
      
      bool anyObjectDetected = (irValue == LOW || inductiveValue == LOW);
      
      if (anyObjectDetected) {
        if (!objectPresent) {
          objectPresent = true;
          objectDetectedTime = millis();
        }
        
        if (millis() - objectDetectedTime >= STABILIZATION_DELAY) {
          
          irValue = digitalRead(IR_SENSOR_PIN);
          inductiveValue = digitalRead(INDUCTIVE_SENSOR_PIN);
          
          if (inductiveValue == LOW && irValue == LOW) {
            sensorsLocked = true;
            objectPresent = false;
            lastDetectionTime = millis();
            
            ServoCommand cmd = SERVO_METAL;
            xQueueSend(servoQueue, &cmd, portMAX_DELAY);
            
            metalCount++;
            
            xTaskNotify(firebaseTaskHandle, 2, eSetValueWithOverwrite);
          }
          else if (inductiveValue == LOW) {
            sensorsLocked = true;
            objectPresent = false;
            lastDetectionTime = millis();
            
            ServoCommand cmd = SERVO_METAL;
            xQueueSend(servoQueue, &cmd, portMAX_DELAY);
            
            metalCount++;
            
            xTaskNotify(firebaseTaskHandle, 2, eSetValueWithOverwrite);
          }
          else if (irValue == LOW) {
            sensorsLocked = true;
            objectPresent = false;
            lastDetectionTime = millis();
            
            ServoCommand cmd = SERVO_BOTTLE;
            xQueueSend(servoQueue, &cmd, portMAX_DELAY);
            
            bottleCount++;
            
            xTaskNotify(firebaseTaskHandle, 1, eSetValueWithOverwrite);
          }
          else {
            objectPresent = false;
          }
        }
      }
      else {
        if (objectPresent) {
          objectPresent = false;
        }
      }
    }
    else {
      objectPresent = false;
    }
    
    vTaskDelay(10 / portTICK_PERIOD_MS);
  }
}

// Task 2: Servo Control (High Priority, Core 0)
void servoTask(void *parameter) {
  ServoCommand cmd;
  
  while (1) {
    if (xQueueReceive(servoQueue, &cmd, portMAX_DELAY)) {
      
      if (xSemaphoreTake(xServoMutex, portMAX_DELAY)) {
        
        switch (cmd) {
          case SERVO_BOTTLE:
            myServo.write(BOTTLE_POSITION);
            vTaskDelay(500 / portTICK_PERIOD_MS);
            
            myServo.write(CENTER_POSITION);
            vTaskDelay(500 / portTICK_PERIOD_MS);
            
            sensorsLocked = false;
            break;
            
          case SERVO_METAL:
            myServo.write(METAL_POSITION);
            vTaskDelay(500 / portTICK_PERIOD_MS);
            
            myServo.write(CENTER_POSITION);
            vTaskDelay(500 / portTICK_PERIOD_MS);
            
            sensorsLocked = false;
            break;
            
          case SERVO_CENTER:
            myServo.write(CENTER_POSITION);
            sensorsLocked = false;
            break;
        }
        
        xSemaphoreGive(xServoMutex);
      }
    }
  }
}

// Task 3: Firebase Communication (Medium Priority, Core 1)
void firebaseTask(void *parameter) {
  uint32_t notificationValue;
  
  while (1) {
    if (xTaskNotifyWait(0, 0xFFFFFFFF, &notificationValue, 0)) {
      
      if (notificationValue == 1) {
        updateFirebaseTransaction();
      }
      else if (notificationValue == 2) {
        updateFirebaseNotBottle();
      }
    }
    
    checkFirebaseStatus();
    
    vTaskDelay(2000 / portTICK_PERIOD_MS);
  }
}

// Task 4: Bin Status Check (Low Priority, Core 1)
void binCheckTask(void *parameter) {
  bool previousBinFullStatus = false;
  
  while (1) {
    float distance = getDistance();
    
    // Update bin status
    binIsFull = (distance <= BIN_FULL_DISTANCE);
    
    // Only update Firebase if status has changed
    if (binIsFull != previousBinFullStatus) {
      updateFirebaseBinStatus(binIsFull);
      previousBinFullStatus = binIsFull;
    }
    
    vTaskDelay(5000 / portTICK_PERIOD_MS);
  }
}

// Firebase status check function
void checkFirebaseStatus() {
  if (WiFi.status() != WL_CONNECTED) {
    return;
  }
  
  HTTPClient http;
  
  // Check sensor-ready status
  String readyUrl = String(FIREBASE_HOST) + "/bins/" + BIN_ID + "/transaction/sensor-ready.json?auth=" + FIREBASE_AUTH;
  http.begin(readyUrl);
  int httpCodeReady = http.GET();
  
  if (httpCodeReady == 200) {
    String payload = http.getString();
    payload.trim();
    sensorReady = (payload == "true");
  }
  http.end();
  
  // Check points
  String pointsUrl = String(FIREBASE_HOST) + "/bins/" + BIN_ID + "/points.json?auth=" + FIREBASE_AUTH;
  http.begin(pointsUrl);
  int httpCodePoints = http.GET();
  
  if (httpCodePoints == 200) {
    String payload = http.getString();
    currentPoints = payload.toInt();
  }
  http.end();
  
  // Check user_uid
  String uidUrl = String(FIREBASE_HOST) + "/bins/" + BIN_ID + "/transaction/user_uid.json?auth=" + FIREBASE_AUTH;
  http.begin(uidUrl);
  int httpCodeUid = http.GET();
  
  if (httpCodeUid == 200) {
    String payload = http.getString();
    payload.replace("\"", "");
    
    if (payload != "" && payload != "null") {
      userUid = payload;
    }
  }
  http.end();
}

// Update Firebase for bottle transaction - READ, INCREMENT, WRITE
void updateFirebaseTransaction() {
  if (WiFi.status() != WL_CONNECTED) {
    return;
  }
  
  HTTPClient http;
  String countUrl = String(FIREBASE_HOST) + "/bins/" + BIN_ID + "/transaction/Count.json?auth=" + FIREBASE_AUTH;
  
  // Read current count from Firebase
  http.begin(countUrl);
  int httpCodeGet = http.GET();
  
  int currentCount = 0;
  if (httpCodeGet == 200) {
    String payload = http.getString();
    currentCount = payload.toInt();
  }
  http.end();
  
  // Increment the count
  currentCount++;
  
  // Write back to Firebase
  http.begin(countUrl);
  http.addHeader("Content-Type", "application/json");
  http.PUT(String(currentCount));
  http.end();
}

// Update Firebase for non-bottle - READ, INCREMENT, WRITE
void updateFirebaseNotBottle() {
  if (WiFi.status() != WL_CONNECTED) {
    return;
  }
  
  HTTPClient http;
  String notBottleUrl = String(FIREBASE_HOST) + "/bins/" + BIN_ID + "/transaction/not_bottle.json?auth=" + FIREBASE_AUTH;
  
  // Read current count from Firebase
  http.begin(notBottleUrl);
  int httpCodeGet = http.GET();
  
  int currentNotBottleCount = 0;
  if (httpCodeGet == 200) {
    String payload = http.getString();
    currentNotBottleCount = payload.toInt();
  }
  http.end();
  
  // Increment the count
  currentNotBottleCount++;
  
  // Write back to Firebase
  http.begin(notBottleUrl);
  http.addHeader("Content-Type", "application/json");
  http.PUT(String(currentNotBottleCount));
  http.end();
}

// Update Firebase for bin full status
void updateFirebaseBinStatus(bool isFull) {
  if (WiFi.status() != WL_CONNECTED) {
    return;
  }
  
  HTTPClient http;
  
  String binFullUrl = String(FIREBASE_HOST) + "/bins/" + BIN_ID + "/bin_full.json?auth=" + FIREBASE_AUTH;
  http.begin(binFullUrl);
  http.addHeader("Content-Type", "application/json");
  
  http.PUT(isFull ? "true" : "false");
  http.end();
}

// Measure distance using ultrasonic sensor
float getDistance() {
  digitalWrite(TRIG_PIN, LOW);
  delayMicroseconds(2);
  
  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);
  
  long duration = pulseIn(ECHO_PIN, HIGH, 30000);
  float distance = duration * 0.034 / 2;
  
  if (distance == 0 || distance > 400) {
    return BIN_DEPTH;
  }
  
  return distance;
}
