#include <DynamixelShield.h>
#define DEBUG_SERIAL Serial    

DynamixelShield dxl;

const uint8_t DXL_ID = 5; // Die ID des Dynamixel-Servos (anpassen falls nötig)
const float DXL_PROTOCOL_VERSION = 1.0; // Protokollversion 1.0 für AX-12A

// Registeradressen für den AX-12A Servo
const int PRESENT_POSITION_ADDR = 36;  // Adresse für aktuelle Position
const int PRESENT_LOAD_ADDR = 40;      // Adresse für aktuelle Last (Load)

void setup() {
  DEBUG_SERIAL.begin(1000000);         // Serial Monitor auf 1 Mbps setzen
  while (!DEBUG_SERIAL);

  dxl.begin(1000000);            // Dynamixel Shield auf 1 Mbps setzen
  dxl.setPortProtocolVersion(DXL_PROTOCOL_VERSION);
  
  dxl.torqueOn(DXL_ID);          // Aktiviert das Drehmoment des Servos

  DEBUG_SERIAL.println("Dynamixel-Servo ist bereit. Gebe eine Position (0-1023) ein:");

  dxl.setGoalPosition(DXL_ID,800);
  delay(1000);
  dxl.setGoalPosition(DXL_ID,500);
  delay(1000);
}

void loop() {
  // Position und Last (Load) mit readControlTableItem auslesen
  int position = dxl.readControlTableItem(PRESENT_POSITION_ADDR, DXL_ID); // Aktuelle Position
  int load = dxl.readControlTableItem(PRESENT_LOAD_ADDR, DXL_ID);         // Aktuelle Last (Load)

  // Überprüfen, ob der Lesevorgang erfolgreich war
  if (dxl.getLastLibErrCode() == DXL_LIB_OK) {
    // Extrahieren der Richtung und des Betrags der Last
    bool loadDirection = load & 0x0400;    // Richtung: Bit 10
    int loadMagnitude = load & 0x03FF;     // Betrag: Bits 0-9

    // Daten an den Serial Monitor senden
    DEBUG_SERIAL.print("Aktuelle Position: ");
    DEBUG_SERIAL.print(position);
    DEBUG_SERIAL.print(" | Last: ");
    DEBUG_SERIAL.print(loadMagnitude);
    DEBUG_SERIAL.print(" | Richtung: ");
    DEBUG_SERIAL.println(loadDirection ? "Negativ" : "Positiv");
  } else {
    DEBUG_SERIAL.println("Fehler beim Lesen der Daten.");
  }
  
  delay(500);
  
  // Überprüfen, ob eine neue Position im Serial Monitor eingegeben wurde
  if (DEBUG_SERIAL.available() > 0) {
    int newPosition = DEBUG_SERIAL.parseInt();   // Lese neue Zielposition aus dem Serial Input
    DEBUG_SERIAL.print("Eingelesene Position: "); // Debug-Ausgabe
    DEBUG_SERIAL.println(newPosition);
    // Prüfen, ob Position im gültigen Bereich liegt
    if (newPosition >= 0 && newPosition <= 1023) {
      dxl.setGoalPosition(DXL_ID, newPosition);  // Setze die neue Zielposition
      DEBUG_SERIAL.print("Neue Zielposition gesetzt: ");
      //Serial.println(newPosition);
    } else {
      DEBUG_SERIAL.println("Ungültige Position. Bitte eine Zahl zwischen 0 und 1023 eingeben.");
    }
  }

  delay(500); // Aktualisiere Werte alle 500 ms
}
