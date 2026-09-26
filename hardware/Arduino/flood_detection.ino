#include <SoftwareSerial.h>
#include <avr/pgmspace.h>

SoftwareSerial gsmSerial(7, 8);

// PINS
const int SENSOR_PIN = A0;
const int LED_GREEN  = 13;
const int LED_YELLOW = 12;
const int LED_RED    = 11;

// CONFIGURATION
const char RECIPIENT_PHONE[] PROGMEM = "+639077650549";
const char APN[] PROGMEM = "internet";

// PUBLIC NO-AUTH ENDPOINT NG DJANGO BACKEND
const char NGROK_URL[] PROGMEM = "http://pretense-landslide-gigahertz.ngrok-free.dev/api/water-level/public-ingest/";

// THRESHOLDS
const int THRESHOLD_WARNING  = 300;
const int THRESHOLD_CRITICAL = 450;

int currentAlertState = -1;
bool isGprsConnected = false;
bool hasSentSMS = false;
unsigned long lastSmsTime = 0;
const unsigned long SMS_COOLDOWN = 300000;

// TIMING CONTROL
unsigned long lastHttpPostTime = 0;
const unsigned long HTTP_POST_INTERVAL = 5000; // 5 seconds

void setup() {
  Serial.begin(9600);
  gsmSerial.begin(9600);

  pinMode(LED_GREEN, OUTPUT);
  pinMode(LED_YELLOW, OUTPUT);
  pinMode(LED_RED, OUTPUT);

  digitalWrite(LED_GREEN, HIGH);
  digitalWrite(LED_YELLOW, LOW);
  digitalWrite(LED_RED, LOW);

  Serial.println(F("========================================="));
  Serial.println(F(" AHON-FloodWatch-3 Initializing...     "));
  Serial.println(F("========================================="));

  delay(2000);
  initGSM();
}

void loop() {
  int waterValue = analogRead(SENSOR_PIN);

  Serial.print(F("Current Sensor Value: "));
  Serial.println(waterValue);

  const char *currentStatus = "Normal";

  // ==========================================
  // 1. LED LOGIC & SMS ALERTS
  // ==========================================
  if (waterValue < THRESHOLD_WARNING) {
    digitalWrite(LED_GREEN, HIGH);
    digitalWrite(LED_YELLOW, LOW);
    digitalWrite(LED_RED, LOW);
    currentStatus = "Normal";

    if (currentAlertState != 0) {
      currentAlertState = 0;
      Serial.println(F("[STATUS] Normal Level - GREEN LED"));
    }
  }
  else if (waterValue >= THRESHOLD_WARNING && waterValue < THRESHOLD_CRITICAL) {
    digitalWrite(LED_GREEN, LOW);
    digitalWrite(LED_YELLOW, HIGH);
    digitalWrite(LED_RED, LOW);
    currentStatus = "Warning";

    if (currentAlertState != 1) {
      currentAlertState = 1;
      Serial.println(F("[STATUS] Warning Level - YELLOW LED"));
      if (!hasSentSMS || millis() - lastSmsTime >= SMS_COOLDOWN) {
        sendSMS(F("FLOOD WARNING: Water level reached the warning threshold. Monitor the situation and prepare to evacuate if instructed."));
        lastSmsTime = millis();
        hasSentSMS = true;
      } else {
        Serial.println(F("[SMS] Warning alert skipped during cooldown."));
      }
    }
  }
  else if (waterValue >= THRESHOLD_CRITICAL) {
    digitalWrite(LED_GREEN, LOW);
    digitalWrite(LED_YELLOW, LOW);
    digitalWrite(LED_RED, HIGH);
    currentStatus = "Danger";

    if (currentAlertState != 2) {
      currentAlertState = 2;
      Serial.println(F("[STATUS] CRITICAL LEVEL - RED LED! Sending Emergency SMS..."));
      sendSMS(F("EMERGENCY FLOOD ALERT: High water level detected! Evacuate immediately!"));
      lastSmsTime = millis();
      hasSentSMS = true;
    }
  }

  // ==========================================
  // 2. HTTP POST TO DJANGO BACKEND
  // ==========================================
  if (millis() - lastHttpPostTime >= HTTP_POST_INTERVAL) {
    lastHttpPostTime = millis();
    
    // Dynamic GSM Status base sa aktwal na GPRS status
    const char *gsmStatusStr = isGprsConnected ? "connected" : "disconnected";

    String jsonPayload = F("{\"water_level_cm\":");
    jsonPayload += String(waterValue);
    jsonPayload += F(",\"status\":\"");
    jsonPayload += currentStatus;
    jsonPayload += F("\",\"sensor_status\":\"online\",\"gsm_status\":\"");
    jsonPayload += gsmStatusStr;
    jsonPayload += F("\"}");

    Serial.println(F(">>> Sending Live Reading to Django Backend..."));
    bool uploadSuccess = sendHttpPost(jsonPayload);
    
    if (uploadSuccess) {
      Serial.println(F("[HTTP] Ingest successfully recorded in Django (201/200 OK)!"));
    } else {
      Serial.println(F("[HTTP] Upload failed or timed out. Re-checking GPRS connection..."));
      // Re-check o retry connection kung naputol ang GPRS
      if (!isGprsConnected) {
        startGPRS();
      }
    }
  }

  delay(1000);
}

// ==========================================
// GSM & GPRS FUNCTIONS
// ==========================================
void initGSM() {
  Serial.println(F("Initializing GSM Module..."));
  if (!sendATCommand(F("AT"), F("OK"), 2000)) {
    Serial.println(F("[GSM] Modem did not respond to AT."));
    return;
  }
  if (!sendATCommand(F("AT+CMGF=1"), F("OK"), 2000)) {
    Serial.println(F("[GSM] Could not set SMS text mode."));
  }

  if (!startGPRS()) {
    Serial.println(F("[GPRS] Setup failed; check SIM registration and TNT APN."));
  }
  Serial.println(F("GSM System Initialization Complete."));
}

bool startGPRS() {
  sendATCommand(F("AT+HTTPTERM"), F("OK"), 1000);
  sendATCommand(F("AT+SAPBR=0,1"), F("OK"), 2000);

  if (!sendATCommand(F("AT+SAPBR=3,1,\"Contype\",\"GPRS\""), F("OK"), 3000)) {
    Serial.println(F("[GPRS] Failed to set bearer type."));
    isGprsConnected = false;
    return false;
  }
  String apnCommand = F("AT+SAPBR=3,1,\"APN\",\"");
  apnCommand += (const __FlashStringHelper *)APN;
  apnCommand += '"';
  if (!sendATCommand(apnCommand, F("OK"), 3000)) {
    Serial.println(F("[GPRS] Failed to set APN."));
    isGprsConnected = false;
    return false;
  }

  Serial.println(F("Opening GPRS Context..."));
  if (!sendATCommand(F("AT+SAPBR=1,1"), F("OK"), 8000)) {
    Serial.println(F("GPRS Connection Failed!"));
    isGprsConnected = false;
    return false;
  }

  Serial.println(F("GPRS Connected!"));
  isGprsConnected = true;
  return true;
}

void sendSMS(String message) {
  if (!sendATCommand(F("AT+CMGF=1"), F("OK"), 2000)) {
    Serial.println(F("[SMS] Could not set text mode."));
    return;
  }

  gsmSerial.print("AT+CMGS=\"");
  gsmSerial.print((const __FlashStringHelper *)RECIPIENT_PHONE);
  gsmSerial.println(F("\""));
  String prompt = waitForResponse(F(">"), 10000);
  if (prompt.indexOf(F(">")) == -1) {
    Serial.print(F("[SMS] No message prompt from modem: "));
    Serial.println(prompt);
    return;
  }

  gsmSerial.print(message);
  gsmSerial.write(26); // CTRL+Z
  String result = waitForResponse(F("OK"), 30000);
  if (result.indexOf(F("+CMGS:")) != -1 && result.indexOf(F("OK")) != -1) {
    Serial.println(F(">>> SMS accepted by modem. <<<"));
  } else {
    Serial.print(F("[SMS] Send failed: "));
    Serial.println(result);
  }
}

bool sendHttpPost(String payload) {
  if (!sendATCommand(F("AT+HTTPINIT"), F("OK"), 5000)) {
    Serial.println(F("[HTTP] HTTPINIT failed."));
    return false;
  }

  String urlCommand = F("AT+HTTPPARA=\"URL\",\"");
  urlCommand += (const __FlashStringHelper *)NGROK_URL;
  urlCommand += '"';
  if (!sendATCommand(F("AT+HTTPPARA=\"CID\",1"), F("OK"), 3000) ||
      !sendATCommand(urlCommand, F("OK"), 3000) ||
      !sendATCommand(F("AT+HTTPPARA=\"CONTENT\",\"application/json\""), F("OK"), 3000) ||
      !sendATCommand(F("AT+HTTPPARA=\"USERDATA\",\"ngrok-skip-browser-warning: true\""), F("OK"), 3000)) {
    Serial.println(F("[HTTP] Failed to configure request parameters."));
    sendATCommand(F("AT+HTTPTERM"), F("OK"), 2000);
    return false;
  }

  String dataCmd = String(F("AT+HTTPDATA=")) + String(payload.length()) + F(",5000");
  if (!sendATCommand(dataCmd, F("DOWNLOAD"), 5000)) {
    Serial.println(F("[HTTP] Modem did not accept HTTPDATA."));
    sendATCommand(F("AT+HTTPTERM"), F("OK"), 1000);
    return false;
  }
  gsmSerial.print(payload);
  String dataResponse = waitForResponse(F("OK"), 10000);
  if (dataResponse.indexOf(F("OK")) == -1 || dataResponse.indexOf(F("ERROR")) != -1) {
    Serial.print(F("[HTTP] Payload was not accepted: "));
    Serial.println(dataResponse);
    sendATCommand(F("AT+HTTPTERM"), F("OK"), 1000);
    return false;
  }

  // HTTPACTION returns its status asynchronously after the immediate OK.
  gsmSerial.println("AT+HTTPACTION=1");
  String actionResponse = waitForResponse(F("+HTTPACTION:"), 30000);
  sendATCommand(F("AT+HTTPTERM"), F("OK"), 2000);

  if (actionResponse.indexOf(F(",200,")) != -1 || actionResponse.indexOf(F(",201,")) != -1) {
    isGprsConnected = true;
    return true;
  } else {
    Serial.print(F("[HTTP ERROR] No successful HTTP result: "));
    Serial.println(actionResponse);
    if (actionResponse.indexOf(F("+HTTPACTION:")) == -1 ||
      actionResponse.indexOf(F(",601,")) != -1 ||
      actionResponse.indexOf(F(",602,")) != -1) {
      isGprsConnected = false;
    }
    return false;
  }
}

bool sendATCommand(String command, String expectedResponse, unsigned long timeout) {
  gsmSerial.println(command);
  String resp = waitForResponse(expectedResponse, timeout);
  bool succeeded = resp.indexOf(expectedResponse) != -1 && resp.indexOf("ERROR") == -1;
  if (!succeeded) {
    Serial.print(F("[MODEM] Command failed: "));
    Serial.print(command);
    Serial.print(F(" | response: "));
    Serial.println(resp);
  }
  return succeeded;
}

String waitForResponse(String expectedResponse, unsigned long timeout) {
  String response;
  unsigned long startTime = millis();

  while (millis() - startTime < timeout) {
    while (gsmSerial.available()) {
      char c = gsmSerial.read();
      response += c;
    }
    if (expectedResponse.length() > 0 && response.indexOf(expectedResponse) != -1) {
      break;
    }
    if (response.indexOf(F("ERROR")) != -1) {
      break;
    }
    delay(1);
  }
  return response;
}