#include <SoftwareSerial.h>

// Define the software serial pins
SoftwareSerial BTSerial(10, 11); // TX,RX -> HC-05-RX:11, HC-05-TX:10

void setup() {
  // Start the hardware serial communication with the computer
  Serial.begin(9600);
  Serial.println("Enter AT commands:");

  // Start the software serial communication with the Bluetooth module
  BTSerial.begin(38400);  // Default baud rate for AT mode is usually 38400
}

void loop() {
  // Read from the Bluetooth module and send to Serial Monitor
  if (BTSerial.available()) {
    while (BTSerial.available()) {
      Serial.write(BTSerial.read());
    }
  }

  // Read from Serial Monitor and send to the Bluetooth module
  if (Serial.available()) {
    delay(10); // Add a small delay to ensure all characters are received
    BTSerial.write(Serial.read());
  }
}
