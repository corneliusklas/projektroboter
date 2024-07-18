
#include <Servo.h>

float smooth0 = .01;
float smooth1 = .99;

// Lid positions
int r_lid_open = 130;
int r_lid_close = 60;
int l_lid_open = 15;
int l_lid_close = 80;
float r_lid = 0.0;
float l_lid = 0.0;
float r_lid_smooth = 0.0;
float l_lid_smooth = 0.0;

// Eye positions
int r_eye_right = 70;
int r_eye_left = 140;
int l_eye_right = 70;
int l_eye_left = 140;
int r_eye_mid = 90;
int l_eye_mid = 90;
float r_eye = 0.0;
float l_eye = 0.0;
float r_eye_smooth = 0.0;
float l_eye_smooth = 0.0;

// Gear position
//int gear_left = 0;
//int gear_right = 180;
//float gear = 0.0;
//float gear_smooth = 0.0;

// Eyebrow positions
int r_brow_v = 60;
int l_brow_v = 120;
int r_brow_A = 120;
int l_brow_A = 60;
float r_brow = 0.0;
float l_brow = 0.0;
float r_brow_smooth = 0.0;
float l_brow_smooth = 0.0;

// Lip positions
int upper_lip_happy = 50;
int upper_lip_sad = 150;
int lower_lip_happy = 150;
int lower_lip_sad = 50;
float upper_lip = 0.0;
float lower_lip = 0.0;
float upper_lip_smooth = 0.0;
float lower_lip_smooth = 0.0;

// Head rotation
float head_rotation = 0.0;
float head_rotation_smooth = 0.0;

Servo servo_pin_2;
Servo servo_pin_3;
Servo servo_pin_4;
Servo servo_pin_5;
//Servo servo_pin_6;
Servo servo_pin_7;
Servo servo_pin_8;
Servo servo_pin_9;
Servo servo_pin_10;
Servo servo_pin_11;

//leds
const int greenPin = A0;
int green =0;
const int redPin = A1;
int red =0;
const int yellowPin = A2;
int yellow=0;

void setup() {
  pinMode(greenPin, OUTPUT);
  pinMode(redPin,OUTPUT);
  pinMode(yellowPin,OUTPUT);
  analogWrite(ledPin, 255);
  
  Serial.begin(1000000);
  
  servo_pin_2.attach(2);
  servo_pin_3.attach(3);
  servo_pin_4.attach(4);
  servo_pin_5.attach(5);
  //servo_pin_6.attach(6);
  servo_pin_7.attach(7);
  servo_pin_8.attach(8);
  servo_pin_9.attach(9);
  servo_pin_10.attach(10);
  servo_pin_11.attach(11);

  r_eye_mid = (r_eye_right + r_eye_left) / 2;
  l_eye_mid = (l_eye_right + l_eye_left) / 2;

  // Initialize positions
  r_lid = r_lid_close; //map(50, 0, 100, r_lid_close, r_lid_open);
  l_lid = l_lid_close; //map(50, 0, 100, l_lid_close, l_lid_open);
  r_lid_smooth = r_lid; //map(0.0, 0, 100, r_lid_close, r_lid_open);
  l_lid_smooth = l_lid; //map(0.0, 0, 100, l_lid_close, l_lid_open);

  r_eye = r_eye_mid; //map(50, 0, 100, r_eye_right, r_eye_left);
  l_eye = l_eye_mid; //map(50, 0, 100, l_eye_right, l_eye_left);
  r_eye_smooth = r_eye;
  l_eye_smooth = l_eye;

  //gear = gear_left; //map(50, 0, 100, gear_left, gear_right);
  //gear_smooth = gear;

  r_brow = r_brow_v; //map(50, 0, 100, r_brow_v, r_brow_A);
  l_brow = l_brow_v; //map(50, 0, 100, l_brow_v, l_brow_A);
  r_brow_smooth = r_brow;
  l_brow_smooth = l_brow;

  upper_lip = (upper_lip_sad+upper_lip_happy)/2; //map(50, 0, 100, upper_lip_happy, upper_lip_sad);
  lower_lip = (lower_lip_happy+lower_lip_sad)/2; //map(50, 0, 100, lower_lip_happy, lower_lip_sad);
  upper_lip_smooth = upper_lip;
  lower_lip_smooth = lower_lip;

  head_rotation = 90 ; //map(50, 0, 100, 0, 180);
  head_rotation_smooth = head_rotation;

  // Set initial servo positions
  //servo_pin_2.write(r_lid_close);
  //servo_pin_3.write(l_lid_close);
  //servo_pin_4.write(r_eye_mid);
  //servo_pin_5.write(l_eye_mid);
  //servo_pin_6.write(gear_left);
  //servo_pin_7.write(r_brow_A);
  //servo_pin_8.write(l_brow_A);
  //servo_pin_9.write(upper_lip_sad);
  //servo_pin_10.write(lower_lip_happy);
  //servo_pin_11.write(90);

  Serial.println("Start");
  Serial.println("Keys: l - lids, e - eyes, b - brows, u - upper lip, w - lower lip, r - head rotation, g - green, y - yellow");
}

void moveServos() {
  // Ensure upper lip is always above lower lip
  int upper_lip_value = map(upper_lip_smooth, upper_lip_happy, upper_lip_sad, 0, 100);
  //Serial.print("upper_lip_value:");
  //Serial.print(upper_lip_value);
  int lower_lip_value = map(lower_lip_smooth,  lower_lip_happy,lower_lip_sad, 0, 100);
  //Serial.print(" lower_lip_value:");
  //Serial.println(lower_lip_value);

  if (upper_lip_value <= lower_lip_value) {
    upper_lip_value = lower_lip_value + 1;
    upper_lip_smooth = map(upper_lip_value, 0, 100, upper_lip_happy, upper_lip_sad);
  }

  servo_pin_2.write(r_lid_smooth);
  servo_pin_3.write(l_lid_smooth);
  servo_pin_4.write(r_eye_smooth);
  servo_pin_5.write(l_eye_smooth);
  //servo_pin_6.write(gear_smooth);
  servo_pin_7.write(r_brow_smooth);
  servo_pin_8.write(l_brow_smooth);
  servo_pin_9.write(upper_lip_smooth);
  servo_pin_10.write(lower_lip_smooth);
  servo_pin_11.write(head_rotation_smooth);
}

void processInput(String input) {
  char var;
  float value;
  
  int spaceIndex = 0; //input.indexOf(' ');
  var = input.charAt(0);
  value = input.substring(spaceIndex + 1).toFloat();
  value = constrain(value, 0.0, 1.0);
  
  switch (var) {
    case 'l': 
      l_lid = map(value*100, 0, 100, l_lid_close, l_lid_open); 
      r_lid = map(value*100, 0, 100, r_lid_close, r_lid_open);
      Serial.print("Lids set to: ");
      Serial.print(r_lid);
      Serial.print(" ");
      Serial.println(l_lid);
      break;
    case 'e': 
      r_eye = map(value*100, 0, 100, r_eye_right, r_eye_left); 
      l_eye = map(value*100, 0, 100, l_eye_right, l_eye_left);
      Serial.print("Eyes set to: ");
      Serial.print(r_eye);
      Serial.print(" ");
      Serial.println(l_eye);
      break;
    case 'b': 
      r_brow = map(value*100, 0, 100, r_brow_v, r_brow_A);
      l_brow = map(value*100, 0, 100, l_brow_v, l_brow_A);
      Serial.print("Brows set to: ");
      Serial.print(r_brow);
      Serial.print(" ");
      Serial.println(l_brow);
      break;
    case 'u': 
      upper_lip = map(value*100, 0, 100, upper_lip_happy, upper_lip_sad);
      Serial.print("Upper lip set to: ");
      Serial.println(upper_lip);
      break;
    case 'w': 
      lower_lip = map(value*100, 0, 100, lower_lip_happy, lower_lip_sad);
      Serial.print("Lower lip set to: ");
      Serial.println(lower_lip);
      break;
    case 'r': 
      head_rotation = map(value*100, 0, 100, 0, 180); 
      Serial.print("Head rotation set to: ");
      Serial.println(head_rotation);
      break;
    case 'g': 
      green = map(value*100, 0, 100, 0, 255);
      red= 255-green;
      analogWrite(greenPin, green);
      analogWrite(redPin, red);
      Serial.print("Green set to: ");
      Serial.println(green);
      Serial.print("Red set to: ");
      Serial.println(red);
      break;
    case 'y': 
      yellow = map(value*100, 0, 100, 0, 255);
      analogWrite(yellowPin, yellow);
      Serial.print("yellow set to: ");
      Serial.println(yellow);
      break;
    default:
      Serial.println("Unknown variable identifier");
      break;
    }
}

void smooth() {
  r_lid_smooth = (r_lid_smooth * smooth1) + (r_lid * smooth0);
  l_lid_smooth = (l_lid_smooth * smooth1) + (l_lid * smooth0);
  r_eye_smooth = (r_eye_smooth * smooth1) + (r_eye * smooth0);
  l_eye_smooth = (l_eye_smooth * smooth1) + (l_eye * smooth0);
  //gear_smooth = (gear_smooth * smooth1) + (gear * smooth0);
  r_brow_smooth = (r_brow_smooth * smooth1) + (r_brow * smooth0);
  l_brow_smooth = (l_brow_smooth * smooth1) + (l_brow * smooth0);
  upper_lip_smooth = (upper_lip_smooth * smooth1) + (upper_lip * smooth0);
  lower_lip_smooth = (lower_lip_smooth * smooth1) + (lower_lip * smooth0);
  head_rotation_smooth = (head_rotation_smooth * smooth1) + (head_rotation * smooth0);
}

void loop() {
  if (Serial.available() > 0) {
    String input = Serial.readStringUntil('\n');
    processInput(input);
  }
  smooth();
  moveServos();
  delay(1);
}
