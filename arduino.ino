// Pin connected to the relay for controlling the lights
const int relayPin = 3;

void setup() {
  // Initialize serial communication at a baud rate of 9600
  Serial.begin(9600);
  
  // Set the relay pin as an output
  pinMode(relayPin, OUTPUT);
  
  // Initialize the relay to the OFF state (HIGH)
  digitalWrite(relayPin, HIGH);
}

void loop() {
  // Check if there is data available on the serial port
  if (Serial.available() > 0) {
    // Read the incoming data as a string until a newline character is encountered
    String command = Serial.readStringUntil('\n');

    // Evaluate the received command and control the relay accordingly
    if (command == "ON") {
      digitalWrite(relayPin, HIGH); // Activate the relay to turn on the lights
      Serial.println("Relay ON");    // Send feedback indicating the relay state
    } else if (command == "OFF") {
      digitalWrite(relayPin, LOW);   // Deactivate the relay to turn off the lights
      Serial.println("Relay OFF");    // Send feedback indicating the relay state
    }
  }
}

