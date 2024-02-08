#include <HCSR04.h>
#include <AnalogTouch.h>

#define pinAnalog A0
#define delayTime 250

byte triggerPin = 13;
byte echoCount = 2;
byte* echoPins = new byte[echoCount]{ 12, 7 };

// Slow down the automatic calibration cooldown
#define offset 2
#if offset > 6
#error "Too big offset value"
#endif

void setup() {
  Serial.begin(9600);
  HCSR04.begin(triggerPin, echoPins, echoCount);
}

void loop() {
  //----------------------------
  // TOUCH SENSORS
  uint16_t value = analogTouchRead(pinAnalog);

  // Self calibrate
  static uint16_t ref = 0xFFFF;
  if (value < (ref >> offset))
    ref = (value << offset);
  // Cool down
  else if (value > (ref >> offset))
    ref++;

  uint16_t value_calibrated = value - (ref >> offset);
  // Print calibrated value
  Serial.print("touch");
  Serial.print(": ");
  Serial.println(value_calibrated);

  //----------------------------
  // DISTANCE SENSORS
  double* distances = HCSR04.measureDistanceCm();

  for (int i = 0; i < echoCount; i++) {
    Serial.print("distance");
    Serial.print(i + 1);
    Serial.print(": ");
    Serial.println(distances[i]);
  }

  delay(delayTime);
}
