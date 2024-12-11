#define vaporizer 52

const int ledPins[] = { 4, 5, 6, 7, 8, 9, 10, 11, 12, 13 };
int numLeds = sizeof(ledPins) / sizeof(ledPins[0]);
const int triggerPins[] = { 36, 32, 28, 24 };
const int echoPins[] = { 34, 30, 26, 22 };

int currentBrightness = 0;                     // Current brightness level
int targetBrightness = 0;                      // Target brightness level based on distance
unsigned long lastProximityCheck = 0;          // Last time proximity was checked
const unsigned long proximityInterval = 100;  // Interval for checking proximity (in milliseconds)
bool fadeEnabled = false;                      // Flag to indicate if fading should happen
bool vaporizerEnabled = false;                 // Flag to indicate if vaporizers should be on
unsigned long previousMillis = 0;
int lightDistance = 150;                    // 100 cm
int vaporDistance = 20;                     // 30 cm
unsigned long distance1;
unsigned long distance2;
unsigned long distance3;
unsigned long distance4;
unsigned long lastUpdate = 0; 
int updateInterval = 1;     
int brightnessStep = 20;     


void setup() {
  Serial.begin(19200);

  // Initialize LED pins as outputs
  for (int i = 0; i < 10; i++) {
    pinMode(ledPins[i], OUTPUT);
    analogWrite(ledPins[i], 255);
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

    distance1 = proximity(triggerPins[0], echoPins[0], "dist1");
    distance2 = proximity(triggerPins[1], echoPins[1], "dist2");
    distance3 = proximity(triggerPins[2], echoPins[2], "dist3");
    distance4 = proximity(triggerPins[3], echoPins[3], "dist4");

    controlVaporizer(distance2); //assign vaporizer to sensor 2
    pulseLights(distance1);     //assign vaporizer to sensor 1
  }
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

void controlVaporizer(long dist_sensor) {
  // Vaporizer should be ON when distance is less than vaporDistance
  if (dist_sensor < vaporDistance && dist_sensor > 0) {
    digitalWrite(vaporizer, HIGH);
    vaporizerEnabled = true;
  } else {
    digitalWrite(vaporizer, LOW);
    vaporizerEnabled = false;
  }
}

void pulseLights(long dist_sensor) {
  // Pulsate mode when distance is less than lightDistance
  if (dist_sensor < lightDistance && dist_sensor > 0) { 
    fadeEnabled = true;
    targetBrightness = map(constrain(dist_sensor, 0, lightDistance), 0, lightDistance, 10, 255);
  } else { 
    // Default to 10% brightness when not in range
    fadeEnabled = false;
    targetBrightness = 10; // 10% of 255 is approximately 26
  }

  // Update brightness based on timing
  unsigned long currentMillis = millis();
  if (currentMillis - lastUpdate >= updateInterval) {
    lastUpdate = currentMillis;

    // Smoothly adjust the brightness
    if (currentBrightness < targetBrightness) {
      currentBrightness += brightnessStep;
      if (currentBrightness > targetBrightness) {
        currentBrightness = targetBrightness;
      }
    } else if (currentBrightness > targetBrightness) {
      currentBrightness -= brightnessStep;
      if (currentBrightness < targetBrightness) {
        currentBrightness = targetBrightness;
      }
    }

    // Apply the brightness to all LEDs
    for (int i = 0; i < numLeds; i++) {
      analogWrite(ledPins[i], currentBrightness);
    }
  }
}
