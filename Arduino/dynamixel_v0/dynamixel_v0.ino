// uno mit dynamixel shield, com 13
#include <DynamixelShield.h>  

DynamixelShield dxl(Serial);

const uint8_t DXL_ID = 18; // Die ID des Dynamixel-Servos (anpassen falls nötig)
const float DXL_PROTOCOL_VERSION = 1.0; // Protokollversion 1.0 für AX-12A

// Registeradressen für den AX-12A Servo
const int PRESENT_POSITION_ADDR = 36;  // Adresse für aktuelle Position
const int PRESENT_LOAD_ADDR = 40;      // Adresse für aktuelle Last (Load)

void setup() {

  Serial.begin(1000000);   //Set debugging port baudrate to 115200bps
  while(!Serial);         //Wait until the serial port for terminal is opened

  dxl.begin(1000000);            // Dynamixel Shield auf 1 Mbps setzen
  dxl.setPortProtocolVersion(DXL_PROTOCOL_VERSION);
  
  dxl.torqueOn(DXL_ID);          // Aktiviert das Drehmoment des Servos
  Serial.println("Dynamixel-Servo ist bereit.");

}

void loop() {
  dxl.setGoalPosition(DXL_ID,0);
  delay(1000);
  dxl.setGoalPosition(DXL_ID,500);
  delay(1000);
}
