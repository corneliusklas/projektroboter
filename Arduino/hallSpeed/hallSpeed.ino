#include <SimpleFOC.h>
#include <PciManager.h>
#include <PciListenerImp.h>
int frame=0;
int currentPin = A0;
int tick0 = 512; // sensor tick for 0 current = VCC/2
float VoltPerTick = 5.0/1023.0; 
float VoltPerA = 0.185;
float APerTick = VoltPerTick /VoltPerA;
int idleCurrent = 108; // idle current in mA 

int motionStartPWM=30;
int startPWM = 0;
  
// PID parameters
int previousOutput=0;
int desiredValue= 0;


int mode=0; //0 PWM, 1 Position, 2 torque

struct PID
{
float Kp; // Proportional gain
float Ki; // Integral gain
float Kd; // Derivative gain
};

PID posC= 
{
  1.0, // Proportional gain
  0.0, // Integral gain
  0.0 // Derivative gain
};

PID curC= 
{
  1.1, // Proportional gain
  0.0, // Integral gain
  0.0 // Derivative gain
};

// PID variables
float previousError = 0;
float integral = 0;

int dirPin = 2;
int brakePin = 4;
int pwmPin = 3;        // The PWM pin the Motor is attached to

int Mdir=1;
float mSfilter = 0.9; //velocity filter
float mCfilter = 0.9; //Current filter
float mS=0; //filtered motor speed
float mA=0.0; //motor angle in rad
float mC = 0.0; //motor current

// Hall sensor instance https://docs.simplefoc.com/hall_sensors
// HallSensor(int hallA, int hallB , int hallC , int pp)
//  - hallA, hallB, hallC    - HallSensor A, B and C pins
//  - pp                     - pole pairs
HallSensor sensor = HallSensor(11, 12,10, 7);

// Interrupt routine initialization
// channel A and B callbacks
void doA(){sensor.handleA();}
void doB(){sensor.handleB();}
void doC(){sensor.handleC();}

// sensor interrupt init
PciListenerImp listenA(sensor.pinA, doA);
PciListenerImp listenB(sensor.pinB, doB);
PciListenerImp listenC(sensor.pinC, doC);

//commander for easy serial input processing
Commander comm = Commander(Serial);

void restart() { //(char* cmd)
  char* cmd=(char*)"22";
  // Check if the motor does not start automatically at low PWM
  //if (cmd > 0 && sensor.getVelocity() == 0) {
  analogWrite(pwmPin, 0);
 
  _delay(atoi(cmd)); // Short delay to force a manual restart
  //analogWrite(pwmPin, cmd); // Write the PWM value
  analogWrite(pwmPin, previousOutput);

}

void setMotorPwm(int cmd) {
  //int value = cmd; 
  // Set brake HIGH if value is 0, otherwise LOW
  digitalWrite(brakePin, (cmd == 0) ? HIGH : LOW);
  // Determine direction and adjust value if negative
  if (cmd < 0) {
    digitalWrite(dirPin, HIGH); // Set direction to reverse
    cmd = abs(cmd); // Convert value to positive
    Mdir = -1; // Store direction as reverse
  } else {
    digitalWrite(dirPin, LOW); // Set direction to forward
    Mdir = 1; // Store direction as forward
  }

    // Ensure output is within PWM bounds
  if (cmd>0){
    cmd+=startPWM ;
  }
  if (cmd<0){
    cmd-=startPWM ;
  }

  // Check if the value is within the valid PWM range
  //if (cmd > 255) {
  //  Serial.println("Invalid value. Please enter a value between 0-255.");
  //  return; // Exit the function if the value is out of range
  //}

  cmd = constrain(cmd, 0, 255);
  //char str[12];
  //sprintf(str, "%d", output);
  //Serial.println(output);
  
  analogWrite(pwmPin, cmd); // Write the PWM value
  previousOutput=cmd;
}

void doMotorPwm(char* cmd) {
  desiredValue=atoi(cmd);
  setMotorPwm(desiredValue);
  mode=0;
  startPWM = motionStartPWM;
}

void doPosControl(char* cmd){
  desiredValue= atoi(cmd);
  mode=1;
  previousError = 0;
  integral = 0;
  startPWM = motionStartPWM;
}

void doCurControl(char* cmd){
  desiredValue= atoi(cmd);
  mode=2;
  previousError = 0;
  integral = 0;
  startPWM=0;
}

void positionPIDControl() {
  //Serial.println("loop");

  float desiredPosition = desiredValue;
  float currentPosition = mA;
  float error = desiredPosition - currentPosition;
  // Proportional term
  float Pout = posC.Kp * error;
  // Integral term
  integral += error * posC.Ki;
  float Iout = integral;
  // Derivative term
  float derivative = error - previousError;
  float Dout = posC.Kd * derivative;
  // Calculate total output
  int output = Pout + Iout + Dout;
  previousError = error;
  //check if output changed
  //if (previousOutput!=output){
    // Apply the output to the motor
  setMotorPwm(output);
  //}
}


void currentPIDControl(){
  //Serial.println("loop");

  float desiredCurrent = desiredValue;
  float currentCurrent = mC;
  float error = desiredCurrent - currentCurrent;
  // Proportional term
  float Pout = curC.Kp * error;
  // Integral term
  integral += error * curC.Ki;
  float Iout = integral;
  // Derivative term
  float derivative = error - previousError;
  float Dout = curC.Kd * derivative;
  // Calculate total output
  int output = Pout + Iout + Dout;
  previousError = error;
  //check if output changed


  if (mS==0){
    output=sin(frame)*30+output;
  }
  //  // Apply the output to the motor
  setMotorPwm(output);
  //}
}

void printSensors(){
  Serial.print("output:");
  Serial.print(previousOutput);
  Serial.print(",error:");
  Serial.print(previousError);
  Serial.print(",mA:");
  Serial.print(mA);
  Serial.print(",mS:");//\t")
  Serial.print(mS);
  Serial.print(",mC:");
  Serial.println(mC); //in mA
}

void setup() {

  // monitoring port
  Serial.begin(9600);
  pinMode(brakePin, OUTPUT);  // Initialize the brake pin as an output
  pinMode(pwmPin, OUTPUT);  // Initialize the PWM pin as an output
  pinMode(dirPin, OUTPUT);  // Initialize the dir pin as an output
  //Serial.println("Enter PWM value (0-255):");

  // check if you need internal pullups
  sensor.pullup = Pullup::USE_EXTERN;
  
  // initialize sensor hardware
  sensor.init();
  // interrupt initialization
  PciManager.registerListener(&listenA);
  PciManager.registerListener(&listenB);
  PciManager.registerListener(&listenC);

  //Serial.println("Sensor ready");

  // Add command 'M' with the callback doMotor

  comm.add('M', doMotorPwm, (char*)"motor_pwm");
  comm.add('P', doPosControl, (char*)"motor position");
  comm.add('C', doCurControl, (char*)"motor current");
  comm.add('r', restart, (char*)"motor_restart");

  //Change Variables -> https://docs.simplefoc.com/commander_scalar

  _delay(1000);
}

void loop() {
  frame++;
  // IMPORTANT - call as frequently as possible
  // update the sensor values 
  sensor.update();
  mA = -sensor.getAngle();
  mS = -(sensor.getVelocity()*(1-mSfilter) + mS*(mSfilter));
  //meassure torque via current
  int torqueTick = analogRead(currentPin); 
  int mC_raw = ((torqueTick-tick0) * APerTick * 1000 +idleCurrent) * Mdir;
  mC = mC_raw*(1-mCfilter) + mC*(mCfilter);



  // Process incoming commands
  comm.run();

  printSensors();
  if (mode ==1){
    positionPIDControl();
  }  
    if (mode ==2){
    currentPIDControl();
  }  
  
}
