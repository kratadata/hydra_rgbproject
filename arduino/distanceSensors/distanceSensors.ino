#include <HCSR04.h>

byte triggerPin = 12;
byte echoPin = 13;
String incomingBytes;
int distanceValue;

#define delayTime 250

void setup () {
  Serial.begin(19200);
  HCSR04.begin(triggerPin, echoPin);
}

void loop () {
  double* distances = HCSR04.measureDistanceCm();
  Serial.print("distance");
  Serial.println(distances[0]);
  delay(delayTime);
  //incomingBytes = Serial.readStringUntil('\n');
  // if (incomingBytes.startsWith("distance")) {
  //   incomingBytes.remove(0, 8);
  //   distanceValue = incomingBytes.toInt();
  // }

  // if (distanceValue == 1) {
  //   Serial.println(distances[0]);
  //   delay(delayTime);
  // }
}