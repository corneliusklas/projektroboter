#include <SimpleFOC.h>

int dirPin = 2;
int brakePin = 4;
int pwmPin = 3;  

Commander comm = Commander(Serial);

void doMotorPwm(char* cmd) {
  digitalWrite(brakePin, LOW);
  digitalWrite(dirPin, LOW);
  int value = atoi(cmd);
  analogWrite(pwmPin, value);
  Serial.println(value);
}

void setup() {
  // Serial communication for debugging
  Serial.begin(115200);

  // Add command 'M' with the callback doMotor
  comm.add('M', doMotorPwm, "motor pwm");
}

void loop() {
  // Process incoming commands
  comm.run();

}
