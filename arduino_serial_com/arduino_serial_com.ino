#include <Servo.h>

Servo ESC; 
Servo servo;   
unsigned long lastCommandTime = 0; // Stores the last time a command was received
const unsigned long commandTimeout = 100; // Command timeout in milliseconds (2 seconds)

void setup() {
  ESC.attach(9,1000,2000);
  servo.attach(3,1000,2000);
  Serial.begin(9600);
}

void loop() {
  // Check if commands have been received
  if (Serial.available() >= 2) {
    // Update the last command time
    lastCommandTime = millis();
    
    char speedCommand = Serial.read();
    char directionCommand = Serial.read();
    Serial.println(speedCommand);
    Serial.println(directionCommand);
    
    if (directionCommand == 'u') {
      ESC.write(map(speedCommand - '0', 1, 3, 104, 180));
    } else if (directionCommand == 'd') {
      ESC.write(map(speedCommand - '0', 1, 3, 102, 0));
    } else if (directionCommand == 'l') {
      servo.write(5);
    } else if (directionCommand == 'r') {
      servo.write(165);
    }
  } else {
    // Check if the command timeout has been exceeded
    if (millis() - lastCommandTime > commandTimeout) {
      // Set default positions if no command has been received within the timeout period
      ESC.write(106);
      servo.write(106); // Assuming you want to set the servo to 106 as well, but adjust if needed
      lastCommandTime = millis(); // Reset the timer to avoid constant resetting
    }
  }
}

