#include <FastTouch.h>
#include <Audio.h>
#include <Wire.h>
#include <SPI.h>
#include <SD.h>
#include <SerialFlash.h>

//AUDIO
AudioPlaySdWav           playWav1;
AudioOutputI2S           audioOutput; //Digital I2S
//AudioOutputSPDIF       audioOutput; //Digital S/PDIF
//AudioOutputAnalog      audioOutput; // Analog DAC

AudioConnection          patchCord1(playWav1, 0, audioOutput, 0);
AudioConnection          patchCord2(playWav1, 1, audioOutput, 1);
AudioControlSGTL5000     sgtl5000_1;

float volume = 0; 
float fadeDuration = 2000; // Duration of the fade in (in milliseconds)
unsigned long startTime;

// Use these with the Teensy 3.5 & 3.6 & 4.1 SD card
#define SDCARD_CS_PIN    BUILTIN_SDCARD
//#define SDCARD_MOSI_PIN  11  // not actually used
//#define SDCARD_SCK_PIN   13  // not actually used

// PROXIMITY
#define echo1Pin 36
#define trigger1Pin 37

#define echo2Pin 33
#define trigger2Pin 35

//LEDS
#define led1Pin 38
#define led2Pin 39

// Variables for LED fading
//int brightness = 0; // Current LED brightness
//int fadeAmount = 1; // How much to change the brightness
//unsigned long previousMillis = 0; // Store the last time the LED was updated
//const int fadeInterval = 10; // Time interval for fading (adjust for speed)

//TOUCH
#define NUM_SENSORS 6  // Total number of touch sensors (pins 27 to 32)
int touchValues[NUM_SENSORS];     // Array to store raw touch sensor values
int baselineValues[NUM_SENSORS];  // Array to store baseline values for calibration
int calibratedValues[NUM_SENSORS];// Array to store calibrated touch values
int inx = 0;                      // Index to track sensor number
int threshold = 10;               // Sensitivity threshold for detecting touch
bool isPlaying[NUM_SENSORS] = {false};

//VAPORIZER
#define vaporizer 24

// the setup function runs once when you press reset or power the board
void setup() {
  Serial.begin(9600);
  audioSetup();

  pinMode(led1Pin, OUTPUT);
  pinMode(led2Pin, OUTPUT);
  pinMode(trigger1Pin, OUTPUT);
  pinMode(echo1Pin, INPUT);
  pinMode(trigger2Pin, OUTPUT);
  pinMode(echo2Pin, INPUT);
  pinMode(vaporizer, OUTPUT);

  digitalWrite(led1Pin, LOW);
  digitalWrite(led2Pin, LOW);

  calibrateTouchSensors();

}

// the loop function runs over and over again forever
void loop() {
  proximity(trigger1Pin, echo1Pin, led1Pin, "dist1");
  proximity(trigger2Pin, echo2Pin, led2Pin, "dist2");
  touchReadings();

  delay(400);
}

void proximity(int t, int e, int ledPin, const char* name) {
  long duration, distance;

  // Trigger the ultrasonic sensor
  digitalWrite(t, LOW);
  delayMicroseconds(2);
  digitalWrite(t, HIGH);
  delayMicroseconds(10);
  digitalWrite(t, LOW);
  duration = pulseIn(e, HIGH);

  // Calculate distance (in cm)
  distance = (duration / 2) / 29.1;
  if (distance > 20) {
    digitalWrite(ledPin, LOW);
  } else {
    digitalWrite(ledPin, HIGH);
  }

  Serial.print(name);
  Serial.print(":");
  Serial.print(distance);
  Serial.println(" ");
}

void calibrateTouchSensors() {
  Serial.println("Calibrating touch sensors...");

  // Read the baseline (untouched) value for each sensor
  for (int i = 27; i < 33; ++i) {
    if (i != LED_BUILTIN) {
      baselineValues[inx] = fastTouchRead(i);
      Serial.print("Baseline for touch");
      Serial.print(inx + 1);
      Serial.print(": ");
      Serial.println(baselineValues[inx]);
      inx += 1;
    }
  }

  inx = 0;  // Reset index after calibration
  Serial.println("Calibration complete.");
}

void touchReadings() {
  for (int i = 27; i < 33; ++i) {
    int inx = i - 27;
    if (i != LED_BUILTIN) {
      // Read raw sensor value
      touchValues[inx] = fastTouchRead(i);

      // Subtract the baseline value to get calibrated value
      calibratedValues[inx] = touchValues[inx] - baselineValues[inx];

      Serial.print("touch");
      Serial.print(inx + 1);
      Serial.print(": ");
      Serial.print(calibratedValues[inx]);

      if (calibratedValues[inx] > threshold) {
        if (!isPlaying[inx]) { // Check if the specific song for this sensor is not playing
          fadeIn();
          playFile(inx); // Play the file associated with the sensor
          isPlaying[inx] = true; // Mark this sensor's song as playing
        }
      } else {
        if (isPlaying[inx]) { // Check if the specific song for this sensor is currently playing
          fadeOut();
          isPlaying[inx] = false; // Mark this sensor's song as stopped
        }
      }

      Serial.print(" ");
      inx += 1;
    }
  }

  inx = 0;  // Reset index after looping
  Serial.println();
}

void audioSetup() {

  // Audio connections require memory to work.  For more
  // detailed information, see the MemoryAndCpuUsage example
  AudioMemory(8);

  // Comment these out if not using the audio adaptor board.
  // This may wait forever if the SDA & SCL pins lack
  // pullup resistors
  sgtl5000_1.enable();
  //sgtl5000_1.volume(1);

  //SPI.setMOSI(SDCARD_MOSI_PIN);
  //SPI.setSCK(SDCARD_SCK_PIN);
  if (!(SD.begin(SDCARD_CS_PIN))) {
    // stop here, but print a message repetitively
    while (1) {
      Serial.println("Unable to access the SD card");
      delay(500);
    }
  }
}

void fadeIn() {
  unsigned long elapsed = millis() - startTime; // Calculate elapsed time
  if (elapsed < fadeDuration) {
    volume = map(elapsed, 0, fadeDuration, 0, 1); // Map elapsed time to volume
    sgtl5000_1.volume(volume); // Set the volume
  } else {
    sgtl5000_1.volume(1); // Set volume to max after fade
  }
}

void fadeOut() {
  unsigned long elapsed = millis() - startTime; // Calculate elapsed time
  if (elapsed < fadeDuration) {
    volume = map(elapsed, 0, fadeDuration, 1, 0); // Map elapsed time to volume
    sgtl5000_1.volume(volume); // Set the volume
  } else {
    playWav1.stop(); // Stop playback after fade
  }

}


void playFile(int inx) {
  //Serial.print("Playing...");
  char filename[20];
  snprintf(filename, sizeof(filename), "AUDIO%d.wav", inx); // Format the filename

  playWav1.play(filename);

  // A brief delay for the library read WAV info
  delay(25);
}


//void proximityAnalog(int t, int e, const char* name) {
//  long duration, distance;
//
//  // Trigger the ultrasonic sensor
//  digitalWrite(t, LOW);
//  delayMicroseconds(2);
//  digitalWrite(t, HIGH);
//  delayMicroseconds(10);
//  digitalWrite(t, LOW);
//  duration = pulseIn(e, HIGH);
//
//  // Calculate distance (in cm)
//  distance = (duration / 2) / 29.1;
//
//  // Non-blocking LED fading
//  unsigned long currentMillis = millis();
//  if (currentMillis - previousMillis >= fadeInterval) {
//    previousMillis = currentMillis;
//
//    // Adjust brightness based on proximity
//    if (distance > 100) {
//      brightness -= fadeAmount; // Fade out if distance is greater than 100cm
//      if (brightness <= 0) {
//        brightness = 0; // Clamp brightness to minimum
//      }
//    } else {
//      brightness += fadeAmount; // Fade in if distance is less than or equal to 100cm
//      if (brightness >= 255) {
//        brightness = 255; // Clamp brightness to maximum
//      }
//    }
//
//    // Apply brightness to both LEDs
//    analogWrite(led1Pin, brightness);
//    analogWrite(led2Pin, brightness);
//  }
//
//  // Output sensor data to Serial Monitor
//  Serial.print(name);
//  Serial.print(": ");
//  Serial.print(distance);
//  Serial.println(" ");
//
//}
