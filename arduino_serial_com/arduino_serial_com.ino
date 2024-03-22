void setup() {
  // Start serial communication at 9600 baud rate
  Serial.begin(9600);
  // Initialize the built-in LED pin as an output.
  pinMode(LED_BUILTIN, OUTPUT);
}

void loop() {
  // Check if data is available to read
  if (Serial.available() > 0) {
    // Read the incoming byte
    char receivedChar = Serial.read();
    
   

    // Blink the LED
    digitalWrite(LED_BUILTIN, HIGH);   // Turn the LED on
    delay(250);                        // Wait for 250 milliseconds
    digitalWrite(LED_BUILTIN, LOW);    // Turn the LED off
    delay(250);                        // Wait for 250 milliseconds

    // This additional delay is optional, adjust based on your preference
    // for how quickly the LED blinks after receiving data.
  }
}
