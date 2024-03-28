#include <Servo.h>

Servo ESC; 
Servo servo;   
unsigned long lastCommandTime = 0; // Stores the last time a command was received
const unsigned long commandTimeout = 100; // Command timeout in milliseconds (2 seconds)

void setup() {
  pinMode(LED_BUILTIN, OUTPUT);
  ESC.attach(9,1000,2000);
  servo.attach(3,1000,2000);
  Serial.begin(9600);
}

void loop() {
  if (Serial.available() >= 3) {
    
    char speedCommand = Serial.read();
    char directionUpDown = Serial.read();
    char directionLeftRight = Serial.read();
    Serial.println(speedCommand);
    Serial.println(directionUpDown);
    Serial.println(directionLeftRight);
    lastCommandTime = millis();
    
    if (directionUpDown == 'u') {
      ESC.write(map(speedCommand - '0', 1, 3, 130, 180));
    } 
    if (directionUpDown == 'd') {
      ESC.write(map(speedCommand - '0', 1, 3, 90, 0));
    }
    if (directionLeftRight == 'l') {
      servo.write(5);
    }
    if (directionLeftRight == 'r') {
      servo.write(165);
    }
  } else {
    if (millis() - lastCommandTime > commandTimeout) {
      ESC.write(106);
      servo.write(77); 
      lastCommandTime = millis(); 
  }
 }
}

