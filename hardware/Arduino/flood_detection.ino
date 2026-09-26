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
// NOTE: I-verify muli gamit ang Serial Monitor ang aktwal na max reading ng sensor
// bago tanggapin ang mga values na ito. Sa lumang working code, 550 ang CRITICAL
// (base sa max reading na ~600-602). Baguhin kung iba na ang kalibrasyon ngayon.
const int THRESHOLD_WARNING  = 300;
const int THRESHOLD_CRITICAL = 500;

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
  bool isCritical = false;

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
    isCritical = true;

    if (currentAlertState != 2) {
      currentAlertState = 2;
      Serial.println(F("[STATUS] CRITICAL LEVEL - RED LED! Sending Emergency SMS..."));
      // FIX: flush any stray bytes sitting in the GSM serial buffer (e.g. leftover
      // HTTP response data) before issuing the SMS command sequence.
      flushGsmSerial();
      sendSMS(F("EMERGENCY FLOOD ALERT: High water level detected! Evacuate immediately!"));
      lastSmsTime = millis();
      hasSentSMS = true;
    }
  }

  // ==========================================
  // 2. HTTP POST TO DJANGO BACKEND
  // ==========================================
  // FIX: skip the HTTP POST this cycle if we just handled a fresh CRITICAL
  // transition above, so the SMS command isn't delayed/blocked by an HTTP
  // transaction that can take several seconds to complete.
  if (!isCritical && (millis() - lastHttpPostTime >= HTTP_POST_INTERVAL)) {
    lastHttpPostTime = millis();

    const char *gsmStatusStr = isGprsConnected ? "connected" : "disconnected";

    // FIX: reserve buffer up front to reduce heap fragmentation risk on the
    // limited RAM of an Uno/Nano when doing repeated String concatenation.
    String jsonPayload;
    jsonPayload.reserve(160);

    // FIX: removed the stray leading "{" that was producing invalid JSON
    // like {{"water_level_cm":...}  (double open-brace, single close-brace).
    jsonPayload += F("{\"water_level_cm\":");
    jsonPayload += String(waterValue);
    jsonPayload += F(",\"status\":\"");
    jsonPayload += currentStatus;
    jsonPayload += F("\",\"sensor_status\":\"online\",\"gsm_status\":\"");
    jsonPayload += gsmStatusStr;
    jsonPayload += F("\"}");

    Serial.println(F(">>> Sending Live Reading to Django Backend..."));
    Serial.print(F("[DEBUG] Payload: "));
    Serial.println(jsonPayload);

    bool uploadSuccess = sendHttpPost(jsonPayload);

    if (uploadSuccess) {
      Serial.println(F("[HTTP] Ingest successfully recorded in Django (201/200 OK)!"));
    } else {
      Serial.println(F("[HTTP] Upload failed or timed out. Re-checking GPRS connection..."));
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
void flushGsmSerial() {
  while (gsmSerial.available()) {
    gsmSerial.read();
  }
}

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
  String apnCommand;
  apnCommand.reserve(48);
  apnCommand = F("AT+SAPBR=3,1,\"APN\",\"");
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

void sendSMS(const __FlashStringHelper *message) {
  flushGsmSerial();

  if (!sendATCommand(F("AT+CMGF=1"), F("OK"), 2000)) {
    Serial.println(F("[SMS] Could not set text mode."));
    return;
  }

  gsmSerial.print(F("AT+CMGS=\""));
  gsmSerial.print((const __FlashStringHelper *)RECIPIENT_PHONE);
  gsmSerial.println(F("\""));
  String prompt = waitForResponse(F(">"), 10000);
  if (prompt.indexOf('>') == -1) {
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

bool sendHttpPost(const String &payload) {
  if (!sendATCommand(F("AT+HTTPINIT"), F("OK"), 5000)) {
    Serial.println(F("[HTTP] HTTPINIT failed."));
    return false;
  }

  String urlCommand;
  urlCommand.reserve(140);
  urlCommand = F("AT+HTTPPARA=\"URL\",\"");
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

  String dataCmd;
  dataCmd.reserve(32);
  dataCmd = String(F("AT+HTTPDATA=")) + String(payload.length()) + F(",5000");
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
  gsmSerial.println(F("AT+HTTPACTION=1"));
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

bool sendATCommand(const String &command, const String &expectedResponse, unsigned long timeout) {
  // FIX: drain any leftover/stale bytes still sitting in the buffer from the
  // previous exchange BEFORE sending a new command. Without this, trailing
  // bytes from the last response bleed into the next read and corrupt/garble
  // the text (e.g. "operation not ؽݕRh%I<0,1" — a mix of old + new data).
  flushGsmSerial();
  delay(50); // small settle time so the module is ready for a new command

  gsmSerial.println(command);
  String resp = waitForResponse(expectedResponse, timeout);
  bool succeeded = resp.indexOf(expectedResponse) != -1 && resp.indexOf(F("ERROR")) == -1;
  if (!succeeded) {
    Serial.print(F("[MODEM] Command failed: "));
    Serial.print(command);
    Serial.print(F(" | response: "));
    Serial.println(resp);
  }
  return succeeded;
}

String waitForResponse(const String &expectedResponse, unsigned long timeout) {
  String response;
  response.reserve(96); // FIX: cap growth tendency on repeated appends
  unsigned long startTime = millis();
  unsigned long lastByteTime = millis();
  bool foundToken = false;

  while (millis() - startTime < timeout) {
    while (gsmSerial.available()) {
      char c = gsmSerial.read();
      response += c;
      lastByteTime = millis();
    }
    if (!foundToken) {
      if (expectedResponse.length() > 0 && response.indexOf(expectedResponse) != -1) {
        foundToken = true;
      }
      if (response.indexOf(F("ERROR")) != -1) {
        foundToken = true;
      }
    }
    // FIX: once the expected token/ERROR is seen, don't return immediately —
    // keep draining for a short "settle" window (30ms of silence) so any
    // trailing bytes (extra CR/LF, etc.) are fully consumed now instead of
    // leaking into the NEXT command's response and corrupting it.
    if (foundToken && (millis() - lastByteTime > 30)) {
      break;
    }
    delay(1);
  }
  return response;
}
