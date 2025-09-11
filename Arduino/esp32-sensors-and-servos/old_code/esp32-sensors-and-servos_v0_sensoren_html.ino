
/*
  ESP32 Servo Steuerung über Weboberfläche

  Dieser Sketch realisiert eine drahtlose Steuerung von 9 RC-Servos über WLAN.
  Der ESP32 fungiert dabei sowohl als Access Point als auch als WLAN-Client
  und stellt eine einfache Weboberfläche zur Verfügung.

  Hauptfunktionen:
  - Steuerung von 9 Servos über Slider in der Weboberfläche
  - 3 LEDS über Slider in der Weboberfläche
  - Umschaltbar auf Poti-Steuerung (ein Poti kontrolliert alle Servos + LEDs)
  - Einstellbarer Low-Pass-Filter für sanfte Bewegungen
  - Auslesen und Anzeigen von:
    * 4 Potentiometern (analog)
    * 3 Touch-Pins (kapazitiv)
    * 1 Schalter (mit internem Pull-Up)
  - Soundausgabe über einen Piezo-Buzzer mit konfigurierbarer Tonfolge:
    * Eingabeformat über Web: "frequenz,lautstärke,dauer;..."
    * Beispiel: "1000,80,200;800,60,300;"
    * Nicht-blockierende Wiedergabe im loop()
  - Schalter löst (bei aktivierter Poti-Steuerung) automatisches Abspielen    einer vorgegebenen Tonfolge aus
  - Speicherung von WLAN-Zugangsdaten im EEPROM
  - Verbindung zu bekanntem WLAN + fallback Access Point
  - Anzeige von WLAN-Status, IP-Adresse und ESP-ID
  - WebSocket-Kommunikation für sofortige Reaktion auf Nutzerinteraktionen
  - MDNS-Unterstützung: Zugriff über http://esp-xxxx.local möglich

  Hinweise:
  - PWM-Ausgabe für Buzzer erfolgt für espressif systems version 3.x via 
    ledcAttach(buzzerPin, 1000, BUZZER_RES); // // Ton-Setup mit neuer API, Start mit 1 kHz, 8 Bit
    ledcWrite(buzzerPin, vol);  // Lautstärke (Duty Cycle)
    ledcChangeFrequency(buzzerPin, freq, BUZZER_RES);    

 ToDo:
 - Verknüpfung der eingabe mit leds und servos
 - 3 potis mit 3 servos
 - 3 touch mit 3 servos
 - schalter mit sound (x)
 - 1 poti mit rest der servos und leds
 - matrix ?
 
*/

#include <WiFi.h>
#include <ESPAsyncWebServer.h>
#include <ESP32Servo.h>
#include <Preferences.h>
#include <ESPmDNS.h>

const int servoPins[] = {23, 22, 21, 19, 18, 5}; //, 17, 16, 4};
const int potiPins[] = {36, 39, 34, 35};
const int schalterPins[] = {25};
const int touchPins[] = {32, 33, 27};
const int ledPins[] = {14, 12, 13};
const int buzzerPin = 26;

#define BUZZER_RES 8
#define BUZZER_DUTY 128 // 50% bei 8 Bit
#define BUZZER_CHANNEL 7

#define NUM_SERVOS (sizeof(servoPins) / sizeof(servoPins[0]))
#define NUM_POTIS (sizeof(potiPins) / sizeof(potiPins[0]))
#define NUM_SCHALTER (sizeof(schalterPins) / sizeof(schalterPins[0]))
#define NUM_TOUCH (sizeof(touchPins) / sizeof(touchPins[0]))
#define NUM_LEDS (sizeof(ledPins) / sizeof(ledPins[0]))

Servo servos[NUM_SERVOS];
int servoTargets[NUM_SERVOS] = {90};
float currentAngles[NUM_SERVOS] = {90};
int potiValues[NUM_POTIS];
int schalterValues[NUM_SCHALTER];
int touchValues[NUM_TOUCH];
bool ledStates[NUM_LEDS] = {false};
String soundSequence = "";
bool playSound = false;

bool potiControl = true;
float filter = 0.9;

AsyncWebServer server(80);
AsyncWebSocket ws("/ws");
Preferences preferences;

String chipID = "";
String currentSSID = "";
String currentPASS = "";
bool wifiConnected = false;
IPAddress wifiIP;

unsigned long nextToneTime = 0;
int toneIndex = 0;

void generateChipID() {
  uint64_t mac = ESP.getEfuseMac();
  chipID = String((uint32_t)(mac >> 32), HEX) + String((uint32_t)(mac & 0xFFFFFFFF), HEX);
  chipID.toUpperCase();
}

void saveWiFiCredentials(const String &ssid, const String &pass) {
  preferences.begin("wifi", false);
  preferences.putString("ssid", ssid);
  preferences.putString("pass", pass);
  preferences.end();
}

bool loadWiFiCredentials(String &ssid, String &pass) {
  preferences.begin("wifi", true);
  ssid = preferences.getString("ssid", "");
  pass = preferences.getString("pass", "");
  preferences.end();
  return ssid.length() > 0;
}

void tryConnectToWiFi() {
  if (!loadWiFiCredentials(currentSSID, currentPASS)) return;
  WiFi.begin(currentSSID.c_str(), currentPASS.c_str());
  Serial.print("Verbinde mit WLAN: ");
  Serial.println(currentSSID);
  unsigned long start = millis();
  while (WiFi.status() != WL_CONNECTED && millis() - start < 8000) {
    delay(500);
    Serial.print(".");
  }
  Serial.println();

  if (WiFi.status() == WL_CONNECTED) {
    wifiConnected = true;
    wifiIP = WiFi.localIP();
    Serial.println("Verbunden! IP: " + wifiIP.toString());
  } else {
    Serial.println("Verbindung fehlgeschlagen.");
  }
}

void setupDualWiFi() {
  generateChipID();
  String apName = "ESP32_Servo_" + chipID.substring(chipID.length() - 4);

  WiFi.mode(WIFI_AP_STA);
  WiFi.softAP(apName.c_str());
  Serial.println("Access Point gestartet: " + WiFi.softAPIP().toString());

  tryConnectToWiFi();

  if (wifiConnected) {
    String hostName = "esp-" + chipID.substring(chipID.length() - 4);
    if (MDNS.begin(hostName.c_str())) {
      Serial.println("mDNS aktiv unter: http://" + hostName + ".local");
    } else {
      Serial.println("mDNS konnte nicht gestartet werden");
    }
  }
}

void updateToneSequence() {
  if (!playSound || millis() < nextToneTime) return;

  if (toneIndex >= soundSequence.length()) {
    //ledcWrite(buzzerPin, 0);
    ledcWriteChannel(BUZZER_CHANNEL,0);
    playSound = false;
    toneIndex = 0;
    return;
  }

  int sep1 = soundSequence.indexOf(',', toneIndex);
  int sep2 = soundSequence.indexOf(',', sep1 + 1);
  int sep3 = soundSequence.indexOf(';', sep2 + 1);

  if (sep1 == -1 || sep2 == -1) {
    playSound = false;
    return;
  }

  int freq = soundSequence.substring(toneIndex, sep1).toInt();
  int vol = soundSequence.substring(sep1 + 1, sep2).toInt();
  int dur = soundSequence.substring(sep2 + 1, sep3 == -1 ? soundSequence.length() : sep3).toInt();

  ledcChangeFrequency(buzzerPin, freq, BUZZER_RES);
  //ledcWrite(buzzerPin, vol);
  ledcWriteChannel(BUZZER_CHANNEL,vol);

  nextToneTime = millis() + dur;
  toneIndex = (sep3 == -1) ? soundSequence.length() : sep3 + 1;
}


void setup() {
  Serial.begin(115200);

  //sound laden
  preferences.begin("sound", true);
  soundSequence = preferences.getString("sequence", "");
  preferences.end();
  
  // beim ersten start leer, das soll nicht sein:
  if (soundSequence == "") { soundSequence = "440,100,300;0,0,100;660,100,300;";  }

  for (int i = 0; i < NUM_SERVOS; i++) {
    servos[i].attach(servoPins[i]);
    servos[i].write(servoTargets[i]);
    currentAngles[i] = servoTargets[i];
  }

  for (int i = 0; i < NUM_SCHALTER; i++) {
    pinMode(schalterPins[i], INPUT_PULLUP);
  }

  for (int i = 0; i < NUM_LEDS; i++) {
    pinMode(ledPins[i], OUTPUT);
    digitalWrite(ledPins[i], LOW);
  }

  //ledcAttach(buzzerPin, 1000, BUZZER_RES);
  ledcAttachChannel(buzzerPin, 1000, BUZZER_RES,BUZZER_CHANNEL); //direkt auf anderem kanal um konflikte mit servos zu vermeiden
  //ledcWrite(buzzerPin, 0);
  ledcWriteChannel(BUZZER_CHANNEL,0);

  setupDualWiFi();
  
  server.on("/", HTTP_GET, [](AsyncWebServerRequest *request) {
  String html = "<!DOCTYPE html><html><head><meta charset='UTF-8'><title>ESP32</title></head><body>";
  html += "<h1>ESP32 Steuerung</h1>";
  html += "<p><strong>IP:</strong> " + wifiIP.toString() + "</p>";
  html += "<p><strong>Name:</strong> esp-" + chipID.substring(chipID.length() - 4) + ".local</p>";
  html += "<p><a href='/wlan'>WLAN-Einstellungen</a></p>";

  html += "<label><input type='checkbox' id='potiToggle' onchange='togglePoti(this.checked)'> Poti-Steuerung aktivieren</label><br>";
  html += "Filter: <input type='range' min='0' max='1' step='0.01' value='0.9' id='filterSlider' oninput='sendFilter(this.value)'><br><br>";

  html += "<h2>Servo Steuerung</h2>";
  for (int i = 0; i < NUM_SERVOS; i++) {
    html += "<label>Servo " + String(i) + " (Pin " + String(servoPins[i]) + "):</label> ";
    html += "<input type='range' min='0' max='180' value='" + String(servoTargets[i]) +
            "' id='servo" + i + "' oninput='send(this)'><br>";
  }

  html += "<h2>LED Steuerung</h2>";
  for (int i = 0; i < NUM_LEDS; i++) {
    html += "<label>LED " + String(i) + " (Pin " + String(ledPins[i]) + "):</label> ";
    html += "<input type='range' min='0' max='1' value='" + String(ledStates[i] ? 1 : 0) +
            "' id='led" + i + "' oninput='sendLed(this)'><br>";
  }

  html += "<h2>Tonfolge</h2>";
  html += "<form action='/sound' method='get'>Tonfolge (freq,vol,dur;...):<br>";
  html += "<input name='seq' size='60'><br><input type='submit' value='Abspielen'></form>";

  html += "<h2>Sensorwerte</h2><ul>";
  for (int i = 0; i < NUM_POTIS; i++) {
    html += "<li>Poti " + String(i) + " (Pin " + String(potiPins[i]) + "): " + String(potiValues[i]) + "</li>";
  }
  for (int i = 0; i < NUM_TOUCH; i++) {
    html += "<li>Touch " + String(i) + " (Pin " + String(touchPins[i]) + "): " + String(touchValues[i]) + "</li>";
  }
  for (int i = 0; i < NUM_SCHALTER; i++) {
    html += "<li>Schalter " + String(i) + " (Pin " + String(schalterPins[i]) + "): " + String(schalterValues[i]) + "</li>";
  }
  html += "</ul>";

  html += R"rawliteral(
    <script>
    var socket = new WebSocket("ws://" + location.host + "/ws");
    function send(el) {
      let id = el.id.replace("servo", "");
      socket.send("servo:" + id + ":" + el.value);
    }
    function sendLed(el) {
      let id = el.id.replace("led", "");
      socket.send("led:" + id + ":" + el.value);
    }
    function togglePoti(state) {
      socket.send("poti:" + (state ? "on" : "off"));
    }
    function sendFilter(val) {
      socket.send("filter:" + val);
    }
    </script>
  )rawliteral";

  html += "</body></html>";
  request->send(200, "text/html", html);
});

server.on("/wlan", HTTP_GET, [](AsyncWebServerRequest *request) {
  request->send(200, "text/html", R"rawliteral(
    <h2>WLAN verbinden</h2>
    <form action="/join" method="get">
      SSID: <input name="ssid"><br>
      Passwort: <input name="pass" type="password"><br>
      <input type="submit" value="Verbinden">
    </form>
  )rawliteral");
});

server.on("/join", HTTP_GET, [](AsyncWebServerRequest *request) {
  if (request->hasParam("ssid") && request->hasParam("pass")) {
    String ssid = request->getParam("ssid")->value();
    String pass = request->getParam("pass")->value();
    saveWiFiCredentials(ssid, pass);
    request->send(200, "text/html", "<p>WLAN gespeichert. Starte neu...</p>");
    delay(1000);
    ESP.restart();
  } else {
    request->send(400, "text/plain", "Fehlende Parameter");
  }
});

server.on("/sound", HTTP_GET, [](AsyncWebServerRequest *request) {
  if (request->hasParam("seq")) {
    soundSequence = request->getParam("seq")->value();
    playSound = true;
    toneIndex = 0;

    //sequenz speichern
    preferences.begin("sound", false);
    preferences.putString("sequence", soundSequence);
    preferences.end();
    
    request->send(200, "text/html", "<p>Tonfolge wird abgespielt. <a href='/'>Zur&uuml;ck</a></p>");
  } else {
    request->send(400, "text/plain", "Fehlender Parameter");
  }
});

server.on("/test", HTTP_GET, [](AsyncWebServerRequest *request) {
  request->send(200, "text/plain", "Test OK");
});

ws.onEvent([](AsyncWebSocket *server, AsyncWebSocketClient *client, AwsEventType type, void *arg, uint8_t *data, size_t len) {
  if (type == WS_EVT_CONNECT) {
      Serial.println("WebSocket verbunden → Poti aus");
      potiControl = false;
  }              
  else if (type == WS_EVT_DATA) {
    AwsFrameInfo *info = (AwsFrameInfo *)arg;
    if (info->final && info->index == 0 && info->len == len && info->opcode == WS_TEXT) {
      String msg = "";
      for (size_t i = 0; i < len; i++) msg += (char)data[i];

      if (msg == "poti:on") potiControl = true;
      else if (msg == "poti:off") potiControl = false;
      else if (msg.startsWith("filter:")) {
        float f = msg.substring(7).toFloat();
        if (f >= 0 && f <= 1) filter = f;
      } else if (msg.startsWith("servo:")) {
        int idx = msg.substring(6, msg.indexOf(':', 6)).toInt();
        int val = msg.substring(msg.lastIndexOf(':') + 1).toInt();
        if (idx >= 0 && idx < NUM_SERVOS) {
          servoTargets[idx] = constrain(val, 0, 180);
        }
      } else if (msg.startsWith("led:")) {
        int idx = msg.substring(4, msg.indexOf(':', 4)).toInt();
        int val = msg.substring(msg.lastIndexOf(':') + 1).toInt();
        if (idx >= 0 && idx < NUM_LEDS) {
          ledStates[idx] = val > 0;
        }
      }
    }
  }
});


server.addHandler(&ws);

server.begin();

}

void loop() {
  ws.cleanupClients();

  for (int i = 0; i < NUM_POTIS; i++) {
    potiValues[i] = analogRead(potiPins[i]);
  }
  for (int i = 0; i < NUM_TOUCH; i++) {
    touchValues[i] = touchRead(touchPins[i]);
  }
  for (int i = 0; i < NUM_SCHALTER; i++) {
    schalterValues[i] = digitalRead(schalterPins[i]);
  }

  if (potiControl) {
      // Potis 0–3 → Servos 0–3
      for (int i = 0; i < 4 && i < NUM_POTIS && i < NUM_SERVOS; i++) {
        int mapped = map(potiValues[i], 0, 4095, 0, 180);
        servoTargets[i] = mapped;
      }
    
      // Touch → Servos 4 und 5
      int threshold = 40;
    
      // Touch 0 → Servo 4
      if (NUM_TOUCH > 0 && NUM_SERVOS > 4) {
        servoTargets[4] = (touchValues[0] > threshold) ? 0 : 90;
      }
    
      // Touch 1 → Servo 5
      if (NUM_TOUCH > 1 && NUM_SERVOS > 5) {
        servoTargets[5] = (touchValues[1] > threshold) ? 90 : 0;
      }
    
      // Touch 2 → LED 0
      if (NUM_TOUCH > 2 && NUM_LEDS > 0) {
        ledStates[0] = (touchValues[2] > threshold);
        ledStates[1]=ledStates[0];
        ledStates[2]=ledStates[0];
      }
    
      // Restliche Servos kopieren Servo 0 (falls mehr als 6 vorhanden)
      for (int i = 6; i < NUM_SERVOS; i++) {
        servoTargets[i] = servoTargets[0];
      }
    
      // Wenn Schalter gedrückt → Sound abspielen
      if (schalterValues[0] == LOW && !playSound) {
        
        //soundSequence = "1000,100,200;1200,80,200;800,50,300;";
        //astronomia soundSequence = "146.83, 79, 112; 0.0, 0, 188; 146.83, 79, 112; 0.0, 0, 38; 220.0, 79, 112; 0.0, 0, 38; 196.0, 79, 112; 0.0, 0, 188; 174.61, 79, 112; 0.0, 0, 188; 164.81, 79, 112; 0.0, 0, 188; 164.81, 79, 112; 0.0, 0, 38; 174.61, 79, 112; 0.0, 0, 38; 196.0, 79, 112; 0.0, 0, 188; 174.61, 79, 112; 0.0, 0, 38; 164.81, 79, 112; 0.0, 0, 38; 146.83, 79, 112; 0.0, 0, 188; 146.83, 79, 112; 0.0, 0, 38; 349.23, 79, 112; 0.0, 0, 38; 329.63, 79, 112; 0.0, 0, 38; 349.23, 79, 112; 0.0, 0, 38; 329.63, 79, 112; 0.0, 0, 38; 349.23, 79, 112; 0.0, 0, 38; 146.83, 79, 112; 0.0, 0, 188; 146.83, 79, 112; 0.0, 0, 38; 349.23, 79, 112; 0.0, 0, 38; 329.63, 79, 112; 0.0, 0, 38; 349.23, 79, 112; 0.0, 0, 38; 329.63, 79, 112; 0.0, 0, 38; 349.23, 79, 112; 0.0, 0, 38; 146.83, 79, 112; 0.0, 0, 188; 146.83, 79, 112; 0.0, 0, 38; 220.0, 79, 112; 0.0, 0, 38; 196.0, 79, 112; 0.0, 0, 188; 174.61, 79, 112; 0.0, 0, 188; 164.81, 79, 112; 0.0, 0, 188; 164.81, 79, 112; 0.0, 0, 38; 174.61, 79, 112; 0.0, 0, 38; 196.0, 79, 112; 0.0, 0, 188; 174.61, 79, 112; 0.0, 0, 38; 164.81, 79, 112; 0.0, 0, 38; 146.83, 79, 112; 0.0, 0, 188; 146.83, 79, 112; 0.0, 0, 38; 349.23, 79, 112; 0.0, 0, 38; 329.63, 79, 112; 0.0, 0, 38; 349.23, 79, 112; 0.0, 0, 38; 329.63, 79, 112; 0.0, 0, 38; 349.23, 79, 112; 0.0, 0, 38; 146.83, 79, 112; 0.0, 0, 188; 146.83, 79, 112; 0.0, 0, 38; 349.23, 79, 112; 0.0, 0, 38; 329.63, 79, 112; 0.0, 0, 38; 349.23, 79, 112; 0.0, 0, 38; 329.63, 79, 112; 0.0, 0, 38; 349.23, 79, 112; 0.0, 0, 38; 174.61, 79, 112; 0.0, 0, 38; 174.61, 79, 56; 0.0, 0, 94; 174.61, 79, 112; 0.0, 0, 38; 174.61, 79, 56; 0.0, 0, 94; 220.0, 79, 112; 0.0, 0, 38; 220.0, 79, 56; 0.0, 0, 94; 220.0, 79, 131; 0.0, 0, 19; 220.0, 79, 56; 0.0, 0, 94; 196.0, 79, 112; 0.0, 0, 38; 196.0, 79, 56; 0.0, 0, 94; 196.0, 79, 112; 0.0, 0, 38; 196.0, 79, 56; 0.0, 0, 94; 261.63, 79, 112; 0.0, 0, 38; 261.63, 79, 56; 0.0, 0, 94; 261.63, 79, 112; 0.0, 0, 38; 261.63, 79, 56; 0.0, 0, 94; 293.66, 79, 112; 0.0, 0, 38; 293.66, 79, 56; 0.0, 0, 94; 293.66, 79, 112; 0.0, 0, 38; 293.66, 79, 56; 0.0, 0, 94; 293.66, 79, 112; 0.0, 0, 38; 293.66, 79, 56; 0.0, 0, 94; 293.66, 79, 112; 0.0, 0, 38; 293.66, 79, 56; 0.0, 0, 94; 293.66, 79, 112; 0.0, 0, 38; 293.66, 79, 56; 0.0, 0, 94; 293.66, 79, 112; 0.0, 0, 38; 293.66, 79, 56; 0.0, 0, 94; 196.0, 79, 112; 0.0, 0, 38; 174.61, 79, 112; 0.0, 0, 38; 164.81, 79, 112; 0.0, 0, 38; 130.81, 79, 112;";
        playSound = true;
        toneIndex = 0;
      }
    }

  for (int i = 0; i < NUM_SERVOS; i++) {
    currentAngles[i] = filter * currentAngles[i] + (1.0 - filter) * servoTargets[i];
    servos[i].write((int)currentAngles[i]);
  }

  for (int i = 0; i < NUM_LEDS; i++) {
    digitalWrite(ledPins[i], ledStates[i]);
  }

  updateToneSequence();

  delay(10);
}
