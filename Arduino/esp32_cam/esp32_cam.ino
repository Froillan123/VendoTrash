/*
 * ESP32-CAM Integration for VendoTrash
 * Captures images and sends to FastAPI server for classification
 * Event-driven: Only captures when Arduino sends "READY" signal
 */

#include "esp_camera.h"
#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>
#include <base64.h>

// ============================================
// CONFIGURATION - UPDATE THESE VALUES
// ============================================

// WiFi credentials
const char* ssid = "PLDTWIFI5G";           // Change this!
const char* password = "Kimperor123@";   // Change this!

// FastAPI server URL
// For local network: http://192.168.1.2:8000/api/vendo/classify
// For Cloud Run: https://vendotrash-server-xxx.run.app/api/vendo/classify
const char* serverUrl = "http://192.168.1.2:8000/api/vendo/classify";

// JWT authentication token (get from login endpoint)
// For testing, you can hardcode a token here
// For production, implement token refresh mechanism
// Token obtained: 2025-12-18 (run: python Server/get_jwt_token.py to refresh)
const char* authToken = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI0IiwiZXhwIjoxNzY4NTg3ODA5fQ.OTaNzQ9BB5h9xKh55uRP4NxUYa7dISbf43tAtbyEDvw";

// Machine ID (default machine)
const int machineId = 1;

// ============================================
// CAMERA PIN DEFINITIONS (ESP32-CAM AI-Thinker)
// ============================================

#define PWDN_GPIO_NUM     32
#define RESET_GPIO_NUM    -1
#define XCLK_GPIO_NUM      0
#define SIOD_GPIO_NUM     26
#define SIOC_GPIO_NUM     27
#define Y9_GPIO_NUM       35
#define Y8_GPIO_NUM       34
#define Y7_GPIO_NUM       39
#define Y6_GPIO_NUM       36
#define Y5_GPIO_NUM       21
#define Y4_GPIO_NUM       19
#define Y3_GPIO_NUM       18
#define Y2_GPIO_NUM        5
#define VSYNC_GPIO_NUM    25
#define HREF_GPIO_NUM     23
#define PCLK_GPIO_NUM     22

// ============================================
// SERIAL COMMUNICATION WITH ARDUINO
// ============================================

#define ARDUINO_RX 4  // ESP32 RX pin (connects to Arduino TX)
#define ARDUINO_TX 2  // ESP32 TX pin (connects to Arduino RX)

// Create HardwareSerial instance for Arduino communication
// UART2 on ESP32 (pins can be remapped)
HardwareSerial arduinoSerial(2);

// ============================================
// SETUP
// ============================================

void setup() {
  // Initialize Serial for debugging (USB)
  Serial.begin(115200);
  delay(1000);
  
  Serial.println("\n\n========================================");
  Serial.println("ESP32-CAM VendoTrash System");
  Serial.println("========================================\n");
  
  // Initialize Serial2 for Arduino communication
  arduinoSerial.begin(9600, SERIAL_8N1, ARDUINO_RX, ARDUINO_TX);
  delay(100);
  Serial.println("✅ Serial2 initialized for Arduino communication");
  
  // Initialize camera
  Serial.println("📷 Initializing camera...");
  if (!initCamera()) {
    Serial.println("❌ Camera initialization failed!");
    return;
  }
  Serial.println("✅ Camera initialized successfully");
  
  // Connect to WiFi
  Serial.println("\n📡 Connecting to WiFi...");
  Serial.print("   SSID: ");
  Serial.println(ssid);
  
  WiFi.begin(ssid, password);
  
  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 30) {
    delay(500);
    Serial.print(".");
    attempts++;
  }
  
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\n✅ WiFi connected!");
    Serial.print("   IP address: ");
    Serial.println(WiFi.localIP());
    Serial.print("   Signal strength (RSSI): ");
    Serial.print(WiFi.RSSI());
    Serial.println(" dBm");
  } else {
    Serial.println("\n❌ WiFi connection failed!");
    Serial.println("   Check SSID and password");
    return;
  }
  
  // Test server connection
  Serial.println("\n🌐 Testing server connection...");
  testServerConnection();
  
  Serial.println("\n========================================");
  Serial.println("System Ready!");
  Serial.println("Waiting for Arduino 'READY' signal...");
  Serial.println("========================================\n");
}

// ============================================
// MAIN LOOP
// ============================================

void loop() {
  // ⚡ EVENT-DRIVEN: Wait for "READY" signal from Arduino (ultrasonic trigger)
  if (arduinoSerial.available() > 0) {
    String msg = arduinoSerial.readStringUntil('\n');
    msg.trim();
    
    Serial.print("📥 Received from Arduino: ");
    Serial.println(msg);
    
    if (msg == "READY") {
      Serial.println("\n📸 Object detected! Capturing image...");
      
      // Capture image
      camera_fb_t * fb = esp_camera_fb_get();
      if (!fb) {
        Serial.println("❌ Camera capture failed");
        arduinoSerial.println("ERROR"); // Notify Arduino of failure
        return;
      }

      Serial.printf("✅ Image captured: %d bytes\n", fb->len);
      
      // Encode image to base64
      String imageBase64 = base64::encode((uint8_t*)fb->buf, fb->len);
      Serial.printf("📦 Base64 encoded: %d characters\n", imageBase64.length());
      
      // Send to FastAPI server
      Serial.println("🌐 Sending to server...");
      bool success = sendImageToServer(imageBase64);
      
      if (success) {
        Serial.println("✅ Classification successful!");
      } else {
        Serial.println("❌ Classification failed!");
        arduinoSerial.println("ERROR"); // Notify Arduino of failure
      }
      
      // Return frame buffer
      esp_camera_fb_return(fb);
    } else {
      Serial.print("⚠️  Unknown message from Arduino: ");
      Serial.println(msg);
    }
  }
  
  delay(50); // Small delay to prevent CPU spinning
}

// ============================================
// CAMERA INITIALIZATION
// ============================================

bool initCamera() {
  camera_config_t config;
  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_timer = LEDC_TIMER_0;
  config.pin_d0 = Y2_GPIO_NUM;
  config.pin_d1 = Y3_GPIO_NUM;
  config.pin_d2 = Y4_GPIO_NUM;
  config.pin_d3 = Y5_GPIO_NUM;
  config.pin_d4 = Y6_GPIO_NUM;
  config.pin_d5 = Y7_GPIO_NUM;
  config.pin_d6 = Y8_GPIO_NUM;
  config.pin_d7 = Y9_GPIO_NUM;
  config.pin_xclk = XCLK_GPIO_NUM;
  config.pin_pclk = PCLK_GPIO_NUM;
  config.pin_vsync = VSYNC_GPIO_NUM;
  config.pin_href = HREF_GPIO_NUM;
  config.pin_sscb_sda = SIOD_GPIO_NUM;
  config.pin_sscb_scl = SIOC_GPIO_NUM;
  config.pin_pwdn = PWDN_GPIO_NUM;
  config.pin_reset = RESET_GPIO_NUM;
  config.xclk_freq_hz = 20000000;
  config.pixel_format = PIXFORMAT_JPEG;
  
  // Image quality settings
  // FRAMESIZE_VGA = 640x480 (good balance)
  // FRAMESIZE_QVGA = 320x240 (smaller, faster)
  config.frame_size = FRAMESIZE_VGA;
  config.jpeg_quality = 12;  // 0-63, lower = better quality but larger file
  config.fb_count = 1;

  // Initialize camera
  esp_err_t err = esp_camera_init(&config);
  if (err != ESP_OK) {
    Serial.printf("❌ Camera init failed with error 0x%x\n", err);
    return false;
  }
  
  return true;
}

// ============================================
// SERVER COMMUNICATION
// ============================================

bool sendImageToServer(String imageBase64) {
  HTTPClient http;
  
  // Begin HTTP connection
  http.begin(serverUrl);
  http.setTimeout(10000); // 10 second timeout
  
  // Set headers
  http.addHeader("Content-Type", "application/json");
  http.addHeader("Authorization", "Bearer " + String(authToken));
  
  // Create JSON payload
  DynamicJsonDocument doc(8192); // Larger for base64 image
  doc["image_base64"] = imageBase64;
  doc["machine_id"] = machineId;
  
  String jsonPayload;
  serializeJson(doc, jsonPayload);
  
  Serial.print("📤 Sending POST request...");
  int httpResponseCode = http.POST(jsonPayload);
  
  if (httpResponseCode == 200) {
    String response = http.getString();
    Serial.println(" ✅");
    
    // Parse response
    DynamicJsonDocument responseDoc(1024);
    DeserializationError error = deserializeJson(responseDoc, response);
    
    if (error) {
      Serial.print("❌ JSON parse error: ");
      Serial.println(error.c_str());
      http.end();
      return false;
    }
    
    String status = responseDoc["status"];
    String materialType = responseDoc["material_type"];
    int points = responseDoc["points_earned"];
    float confidence = responseDoc["confidence"];
    
    Serial.println("\n📊 Classification Results:");
    Serial.print("   Status: ");
    Serial.println(status);
    Serial.print("   Material: ");
    Serial.println(materialType);
    Serial.print("   Points: ");
    Serial.println(points);
    Serial.print("   Confidence: ");
    Serial.print(confidence * 100);
    Serial.println("%");
    
    // Send result back to Arduino (PLASTIC or NON_PLASTIC)
    if (status == "success") {
      arduinoSerial.println(materialType); // Send PLASTIC or NON_PLASTIC
      Serial.print("📤 Sent to Arduino: ");
      Serial.println(materialType);
      http.end();
      return true;
    } else {
      arduinoSerial.println("REJECTED"); // Item not accepted
      Serial.println("📤 Sent to Arduino: REJECTED");
      http.end();
      return false;
    }
    
  } else {
    Serial.print(" ❌ HTTP Error: ");
    Serial.println(httpResponseCode);
    String error = http.getString();
    Serial.print("   Error message: ");
    Serial.println(error);
    http.end();
    return false;
  }
}

// ============================================
// SERVER CONNECTION TEST
// ============================================

void testServerConnection() {
  HTTPClient http;
  
  // Test with /api/vendo/test endpoint
  String testUrl = String(serverUrl);
  testUrl.replace("/classify", "/test");
  
  Serial.print("   Testing: ");
  Serial.println(testUrl);
  
  http.begin(testUrl);
  http.setTimeout(5000);
  
  int httpResponseCode = http.GET();
  
  if (httpResponseCode == 200) {
    String response = http.getString();
    Serial.println("   ✅ Server is reachable!");
    Serial.print("   Response: ");
    Serial.println(response);
  } else {
    Serial.print("   ⚠️  Server test returned: ");
    Serial.println(httpResponseCode);
    Serial.println("   Check if server is running and URL is correct");
  }
  
  http.end();
}

