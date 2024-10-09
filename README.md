# Hydra 🐙


# Software 

1. Arduino [IDE 2.3.3](https://www.arduino.cc/en/software).
   * [FastTouch](https://github.com/adrianfreed/FastTouch) library. Install as .zip library found in `arduino/libraries/FastTouch`.
   * [Teensyduino](https://www.pjrc.com/teensy/td_download.html). Download and install via Board Manager.
2. TouchDesigner version [2023.11510](https://derivative.ca/download/archive) 
3. Ableton version ??
4. [Anaconda](https://www.anaconda.com/download/success).
5. After succsefful installation click `RUN.bat` 

<br/>

# Hardware

1 PC running TouchDesigner  
1 Laptop running Ableton  
2 Webcams   
1 Router    
4 Portable Speakers 

<br/>

#  The head

A big module placed in the middle of the stage. It is controlled with a PC running TouchDesigner and Ableton, and it is built out of the following components:

    Inputs:
    1. Speech: 
       * Single Microphone running speech recognition
    2. Vision:
       * Single Camera running object classification. 
    3. Sensors: 
       * 4 Proximity sensors

    Outputs:
    4. Audio: 
       * Sound coming from theatre speakers system
    5. Light: 
       * 10 LEDs with optic fibers
    6. Sensors: 
       * 4 Water vapours 

### Schematics

![Big Hydra Image](/images/big_hydra.png)

### Components

| Object | Description | Amount |  
| --- | --- | --- |
| MICROCONTROLLER | Arduino Mega R3 | 1 |
| PROXIMITY SENSOR | RCWL-1601|  4 |
| LIGHT | 12V RGB| 10 |
| WATER VAPOUR| Mist Maker| 4 |
| POWER | 24V + 5V USB | 1 |
| EXTRA | |


### Arduino code 
`/arduino/HYDRA_small/HYDRA_small.ino `  


Code is structured as follows:  
   1. **Proximity sensors** trigger **lights** based on a certain distance threshold. The threshold can be changed in `/arduino/HYDRA_small/values.h`  
   2. **Vaporizer** trigger **audio** based on a certain touch threshold. The threshold can be changed in `/arduino/HYDRA_small/values.h`. 

<br/>

# The tentacle

A smaller module placed in the center of each community (4 in total). It is not modulated in real-time i.e. different audio tracks are triggered depending on some values e.x. touch on/off, proximity close/far. It is built out of the following components:

    Inputs:
    1. Sensors: 
       * 4 Touch sensors
       * 2 Proximity sensors

    Outputs:
    2. Audio: 
       * A single portable speaker through line in
    3. Light: 
       * 4 LEDs with optic fibers


### Schematics
![Small Hydra Image](/images/small_hydra.png)

### Components per module

| Object | Description | Amount |
| --- | --- | --- |
| MICROCONTROLLER | Teensy 4.1 | 1 |
| AUDIO | Audio Shield for Teensy 4.x | 1 |
| SPEAKER | JBL Charge 5 | 1 |
| SD-CARD | SONY 16GB plugged to Teensy (not Audio Shield!)| 1 |
| PROXIMITY SENSOR | RCWL-1601|2 |
| TOUCH SENSOR | CROCODILE CLAMPS + ELECTROMAGNETIC PAINT| 4 |
| LIGHT | 12V RGB| 4 |
| POWER | 12V MIN. 2A POWER BANK | 1 |
| EXTRA | |


### Arduino code 
`/arduino/HYDRA_small/HYDRA_small.ino `  


Code is structured as follows:  
   1. **Proximity sensors** trigger **lights** based on a certain distance threshold. The threshold can be changed in `/arduino/HYDRA_small/values.h`  
   2. **Touch sensors** trigger **audio** based on a certain touch threshold. The threshold can be changed in `/arduino/HYDRA_small/values.h`.  
    <span style="color:red">**IMPORTANT!! The songs need to be named using capital letters followed by number (starting at 1) and use ".wav" extension e.x. AUDIO1.wav**</span>

<br/>

# TouchDesigner


### Interface

![UI](/images/ui.png)


### 🟣Vision

Based on [MediaPipe TD Plugin](https://github.com/torinmb/mediapipe-touchdesigner), this module runs recognition model to indicate the number of people in front of the camera
1. Press "Active" to turn camera on/off. 
2. Press "Reset" to restart camera. **Debugging** If object recognition does not start, press "Reset", next press "Active" off, then "Active" on. Wait for a few seconds.
3. "Object recognition" displays found object in one of the class trained on [COCO dataset](https://storage.googleapis.com/mediapipe-tasks/object_detector/labelmap.txt)
4. Select external webcam. <span style="color:red">**IMPORTANT! Select different camera than in Classification Menu**</span>

### 🟣Classification

Based on [Teachable Machine](https://teachablemachine.withgoogle.com/train/image), this module runs object recognition model to classifiy the objects belonging to each community. See [TeachableMachine instructions](/TM.md). 

1. Select external webcam. <span style="color:red">**IMPORTANT! Select different camera than in Classification Menu**</span>
2. Place your model ID from Teachable Machine website.
3. Click Pulse next to download model (only needed if updating the model).
4. Click Pulse to reset the model (only needed if updating the model).
5. Using RGB sliders define colors of each community. Depending on the dominant color in the camera view, the community category will be highlighted green. 


### 🟢Sensors

Connects Hydra Head with Ableton [Arduino code](/arduino/HYDRA_big/HYDRA_big/HYDRA_big.ino). It tracks incoming values from [RHWL-1601](https://www.adafruit.com/product/4007) distance sensors, controls LEDs and vaporizers.
1. Press "Active" to close/start connection with Serial Port. 
2. "Distance Value 1" etc. display the current incoming values.
3. "Distance Sensor 1 Min Max" etc. allows you to change the minimum and maximum range (in cm) for the sensor to take effect on Ableton parameters. 


### 🟠Audio

Uses [TDAbleton](https://derivative.ca/UserGuide/TDAbleton) extension to create a connection between TouchDesigner and Ableton in the same network. 
1. Press "Active" to close/start connection with Ableton. If "connected" shows 1 it means that the connection was sucessful.
3. Trigger menu allows the controller in the backstage to trigger sounds based on audio triggers e.x. specific words.
4. Volume control in Ableton
5. Knobs viusalising how values coming from sensors/camera/speech detection influence the parameters in Ableton.

### ⚪Logger

Shows all incoming/outgoing python messages. Useful for debugging.

</br>

# Ableton

## Network settings

<span style="color:red">**IMPORTANT!! Make sure that both computers are connected to the same network!**</span>

### Windows

Static IP address:

1. Click Start Menu > Control Panel > Network and Sharing Center or Network and Internet > Network and Sharing Center.
2. Click Change adapter settings.
3. Right-click on Wi-Fi or Local Area Connection. Click Properties and select Internet Protocol Version 4 (TCP/IPv4).
4. Select "Use the following IP address" and enter the IP address (192.168.0.50) and Subnet mask (255.255.255.0)


---

### Mac

Static IP address:

1. Go to the Apple menu and select System Preferences. Under Internet and Network, select Network.
2. Right-click the network connection you want to use, then click Details.
3. Click on “TCP/IP”.
4. Click the Configure IPv4 pop-up menu and select "Manual". Enter the IP address (192.168.0.52) and subnet mask (255.255.255.0)

## Connection with TouchDesigner
Follow instruction installations [here](https://derivative.ca/UserGuide/TDAbleton)


The three locations for TDA devices are:

* TouchDesigner
* TouchDesigner>TDA Project>Presets>Audio Effects>Max Audio Effect>Imported
* TouchDesigner>TDA Project>Presets>MIDI Effects>Max MIDI Effect>Imported