void setup() {
  // Start serial communication at 9600 baud rate
  Serial.begin(9600);
}

void loop() {
  // Check if data is available to read
  if (Serial.available() > 0) {
    // Read the incoming byte
    char receivedChar = Serial.read();
    
    // Echo the received byte back
    Serial.write(receivedChar);
  }
}
