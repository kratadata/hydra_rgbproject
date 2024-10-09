# Hydra 🐙


## Discussion Points
- Costs of final product and work hours
- Rehersal dates in November
- Configuring Ableton
- Switch to Vosk for offline TTS (lower quality but offline)

# Running

Click `RUN.bat` to get HYDRAted.

# Software 

1. Arduino [IDE 2.3.3](https://www.arduino.cc/en/software).
   * [FastTouch](https://github.com/adrianfreed/FastTouch) library. Install as .zip library found in `arduino/libraries/FastTouch`.
   * [Teensyduino](https://www.pjrc.com/teensy/td_download.html). Download and install via Board Manager.
2. TouchDesigner version [2023.11510](https://derivative.ca/download/archive) 
3. Ableton version ??
4. [Anaconda](https://www.anaconda.com/download/success).

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

| Object | Description |
| --- | --- |
| MICROCONTROLLER | Arduino Mega R3 |
| PROXIMITY SENSOR | RCWL-1601|
| LIGHT | 12V RGB|
| WATER VAPOUR| Mist Maker|
| POWER | 24V + 5V USB |
| EXTRA | |


### Arduino code 
`/arduino/HYDRA_small/HYDRA_small.ino `  


Code is structured as follows:  
   1. **Proximity sensors** trigger **lights** based on a certain distance threshold. The threshold can be changed in `/arduino/HYDRA_small/values.h`  
   2. **Touch sensors** trigger **audio** based on a certain touch threshold. The threshold can be changed in `/arduino/HYDRA_small/values.h`.  
    <span style="color:red">**IMPORTANT!! The songs need to be named using capital letters followed by number (starting at 1) and use ".wav" extension e.x. AUDIO1.wav**</span>      

_________

# The tentacle

A smaller module placed in the center of each community. It is not modulated in real-time i.e. different audio tracks are triggered depending on some values e.x. touch on/off, proximity close/far. It is built out of the following components:

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

### Components

| Object | Description |
| --- | --- |
| MICROCONTROLLER | Teensy 4.1 |
| AUDIO | Audio Shield for Teensy 4.x |
| SPEAKER | ?? |
| SD-CARD | SONY 16GB plugged to Teensy (not Audio Shield!)|
| PROXIMITY SENSOR | RCWL-1601|
| TOUCH SENSOR | CROCODILE CLAMPS + ELECTROMAGNETIC PAINT|
| LIGHT | 12V RGB|
| POWER | 12V MIN. 2A POWER BANK |
| EXTRA | |


### Arduino code 
`/arduino/HYDRA_small/HYDRA_small.ino `  


Code is structured as follows:  
   1. **Proximity sensors** trigger **lights** based on a certain distance threshold. The threshold can be changed in `/arduino/HYDRA_small/values.h`  
   2. **Touch sensors** trigger **audio** based on a certain touch threshold. The threshold can be changed in `/arduino/HYDRA_small/values.h`.  
    <span style="color:red">**IMPORTANT!! The songs need to be named using capital letters followed by number (starting at 1) and use ".wav" extension e.x. AUDIO1.wav**</span>

_________________________

# Network settings

<span style="color:red">**IMPORTANT!! Make sure that both computers are connected to the same network!**</span>

### Windows

Static IP address:

1. Click Start Menu > Control Panel > Network and Sharing Center or Network and Internet > Network and Sharing Center.
2. Click Change adapter settings.
3. Right-click on Wi-Fi or Local Area Connection. Click Properties and select Internet Protocol Version 4 (TCP/IPv4).
4. Select "Use the following IP address" and enter the IP address (192.168.0.50) and Subnet mask (255.255.255.0)

Virtual MIDI:

1. Install [rtpMidi](https://www.tobias-erichsen.de/software/rtpmidi.html)
2. Create a Session which will be seen by all machines/devices connected to the same network. To do this, click on the + sign in the My Sessions part of the window and edit its "Local name" and its "Bonjour name". Note that the Bonjour name will be the name that is visible to other computers. Make sure that you select "Anyone" under "Who might connnect to me".
3. Check Enabled to enable the virtual MIDI Network.

---

### Mac

Static IP address:

1. Go to the Apple menu and select System Preferences. Under Internet and Network, select Network.
2. Right-click the network connection you want to use, then click Details.
3. Click on “TCP/IP”.
4. Click the Configure IPv4 pop-up menu and select "Manual". Enter the IP address (192.168.0.52) and subnet mask (255.255.255.0)

Virtual MIDI:

1. Open Audio/MIDI Setup from Utilities and select Show MIDI Window from the Window menu.
2. Click twice on Network to open the MIDI Network panel.
3. Create a Session which will be seen by all machines/devices connected to the same network. To do this, click on the + sign in the My Sessions part of the window and edit its "Local name" and its "Bonjour name". Note that the Bonjour name will be the name that is visible to other computers. Make sure that you select "Anyone" under "Who might connnect to me".
4. Select existing connection in "Directory" and click connect.
5. Launch Logic Pro X

______________
# TouchDesigner

### Components

| Object | Description |
| --- | --- |
| 
| WEBCAM | ?? |
| MICROPHONE | ?? |
| EXTRA | |

### Interface

![UI](/images/ui.png)
The interface constinst of 5 modules.

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

Uses TDAbleton extension to create a connection between TouchDesigner and Ableton in the same network. For setup please refer to Network Settings in this README.
1. Press "Active" to close/start connection with Ableton. If connected shows 1 the connection was sucessful.
2. Monitor the knobs to see how the values from sensors/camera/speech detection influence different parameters in Ableton.

### ⚪Logger

Shows all incoming/outgoing python messages. Useful for debugging.

---------

### 🔵Speech

Based on OpenAI [Whisper ](https://openai.com/index/whisper/) TTS model. <span style="color:red">**IMPORTANT! Requires OpenAI API Key in order to work**</span>. The purpose of this module is to trigger certain sounds based on **trigger words**.
1. Press "Active" to turn speech recognition on/off.
2. Add "Keywords" to filter out **trigger words**. The bgreen square next to it indicates that the word was found in the spoken sequence.
3. Add your [OpenAI API Key](https://openai.com/index/openai-api/).
4. Change language "en" for English and "fr" for French.
   
