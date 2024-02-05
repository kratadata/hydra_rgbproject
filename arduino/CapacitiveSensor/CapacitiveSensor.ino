
// AnalogTouch
#include <AnalogTouch.h>

#define pinTouch A0
#define pinMotor 2
#define pinAtomizer A5
#define pinLED 6

// Slow down the automatic calibration cooldown
#define offset 2
#if offset > 6
#error "Too big offset value"
#endif

bool valueChanged = false;
bool touchedState = false;

String incomingBytes;
int touchValue = 0;
int motorValue = 0;
int vapourValue = 0;
int ledValue = 0;

void setup() {
  pinMode(pinAtomizer, OUTPUT);
  pinMode(pinMotor, OUTPUT);
  pinMode(pinLED, OUTPUT);
  digitalWrite(pinLED,HIGH);  
  digitalWrite(pinAtomizer, LOW);  
  digitalWrite(pinMotor, LOW);  
  Serial.begin(9600);
}

void loop() {

  incomingBytes = Serial.readStringUntil('\n');

  if (incomingBytes.startsWith("touch")) {
    incomingBytes.remove(0, 5);
    touchValue = incomingBytes.toInt();
    Serial.print("touch");
    Serial.println(touchValue);
  } else if (incomingBytes.startsWith("vibration")) {
    incomingBytes.remove(0, 9);
    motorValue = incomingBytes.toInt();
    Serial.print("motor");
    Serial.println(motorValue);
  } else if (incomingBytes.startsWith("vapour")) {
    incomingBytes.remove(0, 6);
    vapourValue = incomingBytes.toInt();
    Serial.print("vapour");
    Serial.println(vapourValue);
  } else if (incomingBytes.startsWith("led")) {
    incomingBytes.remove(0, 3);
    ledValue = incomingBytes.toInt();
    Serial.print("led");
    Serial.println(ledValue);
  }

 if (touchValue == 1) {
    //use 1 sample
    uint16_t value = analogTouchRead(pinTouch);
    // Self calibrate
    static uint16_t ref = 0xFFFF;
    if (value < (ref >> offset))
      ref = (value << offset);
    // Cool down
    else if (value > (ref >> offset))
      ref++;

    // Print touched
    bool touched = (value - (ref >> offset)) > 40;

    if (touched != touchedState) {
      valueChanged = true;
    } else {
      valueChanged = false;
    }
      touchedState = touched;
      Serial.print("touched");
      Serial.println(touchedState);
    } 

    if (motorValue == 1) {
      digitalWrite(pinMotor, HIGH);
    } else if (vapourValue == 1) {
      digitalWrite(pinAtomizer, HIGH);      
    } else if (ledValue == 1) {
      digitalWrite(pinLED, HIGH); 
    } 
    if (motorValue == 0) {
      digitalWrite(pinMotor,0);
    }
    if (vapourValue == 0) {
     digitalWrite(pinAtomizer,0);
    }
    if (ledValue == 0) {
      digitalWrite(pinLED,0);
    }
    
    
  digitalWrite(pinLED,HIGH);  
  delay(100);
  digitalWrite(pinLED,LOW);  
  digitalWrite(pinMotor,HIGH);
}
