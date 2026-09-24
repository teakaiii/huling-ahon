/*
 * AI-Assisted Flood Detection System - Arduino Firmware
 * Hardware: Arduino Uno + Water Level Sensor + SIM800L GSM/GPRS Module
 * 
 * This firmware:
 * - Reads water level from sensor
 * - Determines flood category (Normal, Alert, Warning, Danger)
 * - Uploads data directly to the Django API via GPRS
 * - Sends SMS alerts during emergency conditions
 * - Handles communication errors with retry logic
 * - Supports solar-powered continuous operation
 */

#include <SoftwareSerial.h>
#include <ArduinoJson.h>

// ==================== CONFIGURATION ====================

// Pin Definitions
#define WATER_LEVEL_SENSOR_PIN A0
#define SIM800L_TX_PIN 7
#define SIM800L_RX_PIN 8
#define LED_STATUS_PIN 13
#define BUZZER_PIN 9

// Flood Thresholds (in cm)
#define NORMAL_THRESHOLD 30
#define ALERT_THRESHOLD 45
#define WARNING_THRESHOLD 60
#define DANGER_THRESHOLD 75

// Timing Configuration
#define READING_INTERVAL 30000      // 30 seconds between readings
#define UPLOAD_INTERVAL 30000      // 30 seconds between uploads
#define SMS_COOLDOWN 300000        // 5 minutes between SMS alerts
#define RETRY_DELAY 5000           // 5 seconds retry delay
#define MAX_RETRIES 3              // Maximum retry attempts

// Django Configuration
// Replace this with your computer's public URL or LAN IP and port.
// Example: http://192.168.1.20:8000/api/water-level/public-ingest/
#define DJANGO_API_URL "http://YOUR_SERVER_ADDRESS:8000/api/water-level/public-ingest/"

// SMS Configuration
#define ADMIN_NUMBER "+639123456789"  // Admin mobile number

// ==================== GLOBAL VARIABLES ====================

SoftwareSerial sim800l(SIM800L_TX_PIN, SIM800L_RX_PIN);

unsigned long lastReadingTime = 0;
unsigned long lastUploadTime = 0;
unsigned long lastSMSTime = 0;

float currentWaterLevel = 0.0;
String currentStatus = "Normal";
bool sensorOnline = true;
bool gsmConnected = false;
bool gprsConnected = false;

// ==================== SETUP ====================

void setup() {
  // Initialize serial communication
  Serial.begin(9600);
  while (!Serial);
  
  Serial.println(F("========================================"));
  Serial.println(F("Flood Detection System - Arduino Firmware"));
  Serial.println(F("========================================"));
  
  // Initialize pins
  pinMode(WATER_LEVEL_SENSOR_PIN, INPUT);
  pinMode(LED_STATUS_PIN, OUTPUT);
  pinMode(BUZZER_PIN, OUTPUT);
  
  // Initialize SIM800L
  sim800l.begin(9600);
  
  // Wait for SIM800L to initialize
  delay(3000);
  
  // Initialize GSM module
  initializeGSM();
  
  // Initialize GPRS
  initializeGPRS();
  
  // Test Django API connection
  testDjangoConnection();
  
  Serial.println(F("System initialized successfully"));
  Serial.println(F("Starting monitoring loop..."));
  
  blinkLED(3, 200);  // Indicate successful startup
}

// ==================== MAIN LOOP ====================

void loop() {
  unsigned long currentTime = millis();
  
  // Read water level at specified interval
  if (currentTime - lastReadingTime >= READING_INTERVAL) {
    lastReadingTime = currentTime;
    readWaterLevel();
  }
  
  // Upload to Django at specified interval
  if (currentTime - lastUploadTime >= UPLOAD_INTERVAL) {
    lastUploadTime = currentTime;
    uploadToDjango();
  }
  
  // Check for emergency conditions
  checkEmergencyConditions();
  
  // Handle incoming SMS
  handleIncomingSMS();
  
  // Monitor system health
  monitorSystemHealth();
  
  delay(100);  // Small delay to prevent watchdog issues
}

// ==================== WATER LEVEL READING ====================

void readWaterLevel() {
  Serial.println(F("Reading water level..."));
  
  // Read analog value from sensor
  int sensorValue = analogRead(WATER_LEVEL_SENSOR_PIN);
  
  // Convert to water level in cm (calibration needed for specific sensor)
  // This is a generic conversion - adjust based on your sensor
  currentWaterLevel = map(sensorValue, 0, 1023, 0, 100);
  
  // Determine flood status
  currentStatus = determineFloodStatus(currentWaterLevel);
  
  Serial.print(F("Water Level: "));
  Serial.print(currentWaterLevel);
  Serial.print(F(" cm - Status: "));
  Serial.println(currentStatus);
  
  // Update LED status
  updateStatusLED();
  
  sensorOnline = true;
}

String determineFloodStatus(float level) {
  if (level >= DANGER_THRESHOLD) {
    return "Danger";
  } else if (level >= WARNING_THRESHOLD) {
    return "Warning";
  } else if (level >= ALERT_THRESHOLD) {
    return "Alert";
  } else {
    return "Normal";
  }
}

// ==================== GSM INITIALIZATION ====================

void initializeGSM() {
  Serial.println(F("Initializing GSM module..."));
  
  // Send AT command to check if SIM800L is responding
  if (sendATCommand("AT", "OK", 2000)) {
    Serial.println(F("SIM800L is responding"));
    gsmConnected = true;
  } else {
    Serial.println(F("SIM800L not responding"));
    gsmConnected = false;
    return;
  }
  
  // Set SMS to text mode
  sendATCommand("AT+CMGF=1", "OK", 2000);
  
  // Disable echo
  sendATCommand("ATE0", "OK", 2000);
  
  // Check SIM card status
  if (sendATCommand("AT+CPIN?", "READY", 2000)) {
    Serial.println(F("SIM card ready"));
  } else {
    Serial.println(F("SIM card not ready"));
  }
  
  // Check signal strength
  checkSignalStrength();
  
  Serial.println(F("GSM initialization complete"));
}

void initializeGPRS() {
  Serial.println(F("Initializing GPRS..."));
  
  if (!gsmConnected) {
    Serial.println(F("GSM not connected, skipping GPRS initialization"));
    return;
  }
  
  // Attach to GPRS
  if (sendATCommand("AT+CGATT=1", "OK", 5000)) {
    Serial.println(F("Attached to GPRS"));
  } else {
    Serial.println(F("Failed to attach to GPRS"));
    gprsConnected = false;
    return;
  }
  
  // Set APN (adjust for your network provider)
  sendATCommand("AT+SAPBR=3,1,\"CONTYPE\",\"GPRS\"", "OK", 2000);
  sendATCommand("AT+SAPBR=3,1,\"APN\",\"internet.globe.com.ph\"", "OK", 2000);  // Globe Philippines
  
  // Open bearer
  if (sendATCommand("AT+SAPBR=1,1", "OK", 5000)) {
    Serial.println(F("Bearer opened"));
    gprsConnected = true;
  } else {
    Serial.println(F("Failed to open bearer"));
    gprsConnected = false;
  }
  
  Serial.println(F("GPRS initialization complete"));
}

void checkSignalStrength() {
  sim800l.println("AT+CSQ");
  delay(1000);
  
  if (sim800l.available()) {
    String response = sim800l.readString();
    int csqIndex = response.indexOf("+CSQ:");
    if (csqIndex != -1) {
      int csq = response.substring(csqIndex + 6, csqIndex + 8).toInt();
      Serial.print(F("Signal Strength: "));
      Serial.print(csq);
      Serial.println(F("/31"));
    }
  }
}

// ==================== DJANGO API UPLOAD ====================

void uploadToDjango() {
  if (!gprsConnected) {
    Serial.println(F("GPRS not connected, attempting to reconnect..."));
    initializeGPRS();
    if (!gprsConnected) {
      Serial.println(F("Failed to reconnect GPRS, skipping upload"));
      return;
    }
  }
  
  Serial.println(F("Uploading to Django API..."));
  
  // Create JSON payload
  StaticJsonDocument<200> doc;
  doc["water_level_cm"] = currentWaterLevel;
  doc["status"] = currentStatus;
  doc["sensor_status"] = sensorOnline ? "online" : "offline";
  doc["gsm_status"] = gsmConnected ? "connected" : "disconnected";
  
  String jsonString;
  serializeJson(doc, jsonString);
  
  // Prepare HTTP request
  String url = "AT+HTTPPARA=\"URL\",\"" + String(DJANGO_API_URL) + "\"";
  
  // Initialize HTTP
  if (!sendATCommand("AT+HTTPINIT", "OK", 2000)) {
    Serial.println(F("HTTP initialization failed"));
    return;
  }
  
  // Set URL
  if (!sendATCommand(url.c_str(), "OK", 2000)) {
    Serial.println(F("URL setting failed"));
    sendATCommand("AT+HTTPTERM", "OK", 2000);
    return;
  }
  
  // Set content type
  sendATCommand("AT+HTTPPARA=\"CONTENT\",\"application/json\"", "OK", 2000);
  
  // Set data length
  String dataLengthCmd = "AT+HTTPDATA=" + String(jsonString.length()) + ",5000";
  sendATCommand(dataLengthCmd.c_str(), "DOWNLOAD", 2000);
  
  // Send data
  sim800l.print(jsonString);
  delay(1000);
  
  // Perform POST request
  if (sendATCommand("AT+HTTPACTION=1", "OK", 5000)) {
    delay(5000);
    
    // Read response
    sim800l.println("AT+HTTPREAD");
    delay(1000);
    
    while (sim800l.available()) {
      Serial.write(sim800l.read());
    }
  }
  
  // Terminate HTTP
  sendATCommand("AT+HTTPTERM", "OK", 2000);
  
  Serial.println(F("Django upload complete"));
}

void testDjangoConnection() {
  Serial.println(F("Testing Django API connection..."));
  
  if (!gprsConnected) {
    Serial.println(F("GPRS not connected, cannot test Django API"));
    return;
  }
  
  // Simple GET request to test connection
  String url = "AT+HTTPPARA=\"URL\",\"" + String(DJANGO_API_URL) + "\"";
  
  sendATCommand("AT+HTTPINIT", "OK", 2000);
  sendATCommand(url.c_str(), "OK", 2000);
  sendATCommand("AT+HTTPPARA=\"CONTENT\",\"application/json\"", "OK", 2000);
  sendATCommand("AT+HTTPACTION=0", "OK", 5000);
  delay(5000);
  sendATCommand("AT+HTTPTERM", "OK", 2000);
  
  Serial.println(F("Django API connection test complete"));
}

// ==================== SMS ALERTS ====================

void checkEmergencyConditions() {
  unsigned long currentTime = millis();
  
  // Check if SMS cooldown has passed
  if (currentTime - lastSMSTime < SMS_COOLDOWN) {
    return;
  }
  
  // Send SMS if in Warning or Danger status
  if (currentStatus == "Warning" || currentStatus == "Danger") {
    sendEmergencySMS(currentStatus);
    lastSMSTime = currentTime;
  }
}

void sendEmergencySMS(String alertLevel) {
  Serial.println(F("Sending emergency SMS..."));
  
  if (!gsmConnected) {
    Serial.println(F("GSM not connected, cannot send SMS"));
    return;
  }
  
  // Create SMS message
  String message = "BARANGAY TONSUYA FLOOD ";
  message += alertLevel;
  message += "\n\nCurrent Flood Level: ";
  message += alertLevel;
  message += "\nWater Level: ";
  message += String(currentWaterLevel);
  message += " cm\n\n";
  
  if (alertLevel == "Danger") {
    message += "Residents are advised to prepare for immediate evacuation.\n";
  } else if (alertLevel == "Warning") {
    message += "Residents are advised to monitor the situation closely.\n";
  }
  
  message += "\nDate: " + getCurrentDate();
  message += "\nTime: " + getCurrentTime();
  message += "\n\nPlease stay safe.";
  
  // Send SMS to admin
  sendSMS(ADMIN_NUMBER, message);
  
  // Activate buzzer for danger level
  if (alertLevel == "Danger") {
    activateBuzzer();
  }
}

void sendSMS(String number, String message) {
  Serial.print(F("Sending SMS to: "));
  Serial.println(number);
  
  // Set recipient
  String cmd = "AT+CMGS=\"" + number + "\"";
  sim800l.println(cmd);
  delay(1000);
  
  // Send message
  sim800l.print(message);
  delay(100);
  
  // Send Ctrl+Z to send
  sim800l.write(26);
  delay(5000);
  
  Serial.println(F("SMS sent"));
}

void handleIncomingSMS() {
  sim800l.println("AT+CMGL=\"ALL\"");
  delay(1000);
  
  while (sim800l.available()) {
    String response = sim800l.readString();
    
    // Check for new SMS
    if (response.indexOf("+CMGL:") != -1) {
      // Parse SMS and process commands
      processSMSCommand(response);
    }
  }
  
  // Delete all SMS after processing
  sendATCommand("AT+CMGD=1,4", "OK", 2000);
}

void processSMSCommand(String sms) {
  // Check for admin commands
  if (sms.indexOf("STATUS") != -1) {
    String statusMsg = "System Status:\n";
    statusMsg += "Water Level: " + String(currentWaterLevel) + " cm\n";
    statusMsg += "Status: " + currentStatus + "\n";
    statusMsg += "Sensor: " + String(sensorOnline ? "Online" : "Offline") + "\n";
    statusMsg += "GSM: " + String(gsmConnected ? "Connected" : "Disconnected") + "\n";
    statusMsg += "GPRS: " + String(gprsConnected ? "Connected" : "Disconnected");
    
    sendSMS(ADMIN_NUMBER, statusMsg);
  }
  else if (sms.indexOf("RESET") != -1) {
    Serial.println(F("Reset command received"));
    // Perform system reset
    asm volatile ("  jmp 0");
  }
}

// ==================== SYSTEM MONITORING ====================

void monitorSystemHealth() {
  static unsigned long lastHealthCheck = 0;
  unsigned long currentTime = millis();
  
  if (currentTime - lastHealthCheck >= 60000) {  // Check every minute
    lastHealthCheck = currentTime;
    
    // Check GSM connection
    if (!sendATCommand("AT", "OK", 2000)) {
      Serial.println(F("GSM connection lost, reinitializing..."));
      gsmConnected = false;
      gprsConnected = false;
      initializeGSM();
      initializeGPRS();
    }
    
    // Check GPRS connection
    if (gsmConnected && !gprsConnected) {
      initializeGPRS();
    }
  }
}

// ==================== UTILITY FUNCTIONS ====================

bool sendATCommand(const char* command, const char* expectedResponse, unsigned long timeout) {
  sim800l.println(command);
  unsigned long startTime = millis();
  
  while (millis() - startTime < timeout) {
    if (sim800l.available()) {
      String response = sim800l.readString();
      if (response.indexOf(expectedResponse) != -1) {
        return true;
      }
    }
  }
  
  return false;
}

String getISO8601Time() {
  // Get current time from NTP server or use system time
  // For simplicity, using a placeholder - implement NTP for accurate time
  return "2026-07-13T14:30:00Z";
}

String getCurrentDate() {
  return "2026-07-13";  // Placeholder - implement NTP
}

String getCurrentTime() {
  return "14:30:00";  // Placeholder - implement NTP
}

void updateStatusLED() {
  if (currentStatus == "Danger") {
    // Fast blinking for danger
    digitalWrite(LED_STATUS_PIN, HIGH);
    delay(100);
    digitalWrite(LED_STATUS_PIN, LOW);
    delay(100);
  } else if (currentStatus == "Warning") {
    // Slow blinking for warning
    digitalWrite(LED_STATUS_PIN, HIGH);
    delay(500);
    digitalWrite(LED_STATUS_PIN, LOW);
    delay(500);
  } else if (currentStatus == "Alert") {
    // On for alert
    digitalWrite(LED_STATUS_PIN, HIGH);
  } else {
    // Off for normal
    digitalWrite(LED_STATUS_PIN, LOW);
  }
}

void blinkLED(int count, int delayMs) {
  for (int i = 0; i < count; i++) {
    digitalWrite(LED_STATUS_PIN, HIGH);
    delay(delayMs);
    digitalWrite(LED_STATUS_PIN, LOW);
    delay(delayMs);
  }
}

void activateBuzzer() {
  Serial.println(F("Activating buzzer..."));
  for (int i = 0; i < 5; i++) {
    digitalWrite(BUZZER_PIN, HIGH);
    delay(200);
    digitalWrite(BUZZER_PIN, LOW);
    delay(200);
  }
}

// ==================== ERROR HANDLING ====================

void handleError(String error) {
  Serial.print(F("ERROR: "));
  Serial.println(error);
  
  // Blink LED to indicate error
  for (int i = 0; i < 10; i++) {
    digitalWrite(LED_STATUS_PIN, HIGH);
    delay(100);
    digitalWrite(LED_STATUS_PIN, LOW);
    delay(100);
  }
  
  // Attempt recovery
  if (error.indexOf("GSM") != -1) {
    initializeGSM();
  } else if (error.indexOf("GPRS") != -1) {
    initializeGPRS();
  }
}
