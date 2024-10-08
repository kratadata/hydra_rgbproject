#define vaporizer 52

const int ledPins[] = {4, 5, 6, 7, 8, 9, 10, 11, 12, 13};
const int triggerPins[] = {36, 32, 28, 24};
const int echoPins[] = {34, 30, 26, 22};

int brightness = 0;      // Starting brightness for the LEDs
int fadeAmount = 5;      // Amount to change the brightness each time through the loop
unsigned long lastProximityCheck = 0; // Last time proximity was checked
const unsigned long proximityInterval = 2000; // Interval for checking proximity (in milliseconds)
bool fadeEnabled = false; // Flag to indicate if fading should happen

void setup() {
  Serial.begin(19200);

  // Initialize LED pins as outputs
  for (int i = 0; i < 10; i++) {
    pinMode(ledPins[i], OUTPUT);
  }

  // Initialize proximity sensor pins
  for (int i = 0; i < 4; i++) {
    pinMode(triggerPins[i], OUTPUT);
    pinMode(echoPins[i], INPUT);
  }

  pinMode(vaporizer, OUTPUT);
  digitalWrite(vaporizer, LOW);
}

void loop() {
  // Check if it's time to measure proximity
  unsigned long currentMillis = millis();
  if (currentMillis - lastProximityCheck >= proximityInterval) {
    lastProximityCheck = currentMillis;

    // Reset the fadeEnabled flag for this proximity check cycle
    fadeEnabled = false;

    // Check distances for all sensors
    for (int i = 0; i < 4; i++) {
      long distance = proximity(triggerPins[i], echoPins[i], "dist" + String(i + 1));
      
      // If any sensor detects a distance less than 50 cm, enable the fading
      if (distance < 50 && distance > 30) { // Ensure distance > 0 (valid reading)
        fadeEnabled = true;
        digitalWrite(vaporizer, HIGH);
      }
    }
  }

  // Only fade the LEDs if an object is detected within 50 cm
  if (fadeEnabled) {
    for (int i = 0; i < 10; i++) {
      analogWrite(ledPins[i], brightness);
    }

    // Update brightness
    brightness += fadeAmount;

    // Reverse the fading direction at the limits
    if (brightness <= 0 || brightness >= 255) {
      fadeAmount = -fadeAmount;
    }
  } else {
    // Optionally turn off the LEDs if no object is detected within range
    for (int i = 0; i < 10; i++) {
      analogWrite(ledPins[i], 0); // Turn off LEDs when no proximity
    }
  }

  Serial.println(brightness);
  delay(10); // Short delay for smooth fading
}

// Proximity function to measure distance from the ultrasonic sensor
long proximity(int t, int e, const String& name) {
  long duration, distance;
  
  // Trigger the ultrasonic sensor
  digitalWrite(t, LOW);
  delayMicroseconds(2);
  digitalWrite(t, HIGH);
  delayMicroseconds(10);
  digitalWrite(t, LOW);
  
  // Measure the duration of the echo pulse
  duration = pulseIn(e, HIGH);
  
  // Calculate distance in cm
  distance = duration * 0.034 / 2;

  // Print the distance for debugging
  Serial.print(name);
  Serial.print(": ");
  Serial.print(distance);
  Serial.println(" cm");

  return distance;
}