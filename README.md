**TO DO:** 

    [ ] add websocket server
    [ ] create bat file
    [ ] re-calibrate touch sensor every x seconds
    [ ] finish documentation

---------

# Hydra 🐙

Hydra consists out of two entities: the head and 4 children. 

**The head** is a big module placed in the middle of the stage. It is controlled with a PC running TouchDesigner and Ableton, and it is built out of the following components:

    **Inputs:**
    1. Speech: 1 Microphone running speech recognition
    2. Vision: 1 Camera running object classification. 
    3. Sensors: Proximity sensor

    **Outputs:**
    1. Audio: sound coming from theatre speakers system
    2. Light: Optic fibers
    3. Sensor: Water vapour 

**The children** are smaller modules placed in each community. It is not modulated in real-time, different audio tracks are triggered depending on simple values e.x. touch on/off, proximity close/far. It is built out of the following components:

    **Inputs:**
    1. Sensors: Touch and proximity sensors

    **Outputs:**
    1. Audio: Sound coming from single, portable speaker
    2. Light: Optic fibers
   
---------


<a name="network" style="font-size:20px"># Network settings</a>

**Make sure that both computers are connected to the same network!**

Windows:

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

Mac:

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

---------

# TouchDesigner

1. Launch TouchDesigner version [2023.11510](https://derivative.ca/download/archive) 
2. Open RGBPrototype.toe.

**Interface**

![UI](/ui.png)
Interface consists of of 5 modules, that allow the user to monitor the inputs from different sensors.

# Speech🔵

Based on [Vosk](https://alphacephei.com/vosk/) TTS to facilitate offline speech recognition. The model in use is [vosk-model-small-fr-0.22](https://alphacephei.com/vosk/models). The purpose of this module is to trigger certain sounds based on **trigger words**.
1. Press "Active" to turn speech recognition on/off.
2. Add "Keywords" to filter out **trigger words**. The blue square next to it indicates that the word was found.
3. The big area underneath displays all sentences. The rectangle with "chan1" indicates microphone signal.
   

# Vision🟣

Based on [MediaPipe TD Plugin](https://github.com/torinmb/mediapipe-touchdesigner), this module runs object recognition model to indicate the number of people in front of the camera
1. Press "Active" to turn camera on/off. 
2. "Object recognition" displays found object in one of the class trained on [COCO dataset](https://storage.googleapis.com/mediapipe-tasks/object_detector/labelmap.txt)
   
**Debugging** If object recognition does not start, press "Reset", next press "Active" off, then "Active" on. Wait for a few seconds.   


# Sensors🟢

Based on [Arduino code](/arduino/distanceSensors/distanceSensors.ino). It tracks incoming values from two [RHWL-1601](https://www.adafruit.com/product/4007) distance sensors and capacitive sensor (Bare Conductive Electric Paint)
1. Press "Active" to close/start connection with Serial Port. 
2. "Distance Value 1", "Distance Value 2", "Touch Value 1" display the current incoming values.
3. "Distance Sensor 1 Min Max" allows you to change the minimum and maximum range (in cm) for the sensor to take effect on Ableton parameters. 
4. "Distance Sensor 2 Min Max" see above.
5. "Touch Sensor 1 Min Max" allows you to change the minimum and maximum range for the sensor to take effect on Ableton parameters. This varies greatly based on the humidity in the space, amount of people, etc. And needs to be calibrated before each show.


# Audio🟠

Uses TDAbleton extension to create a connection between TouchDesigner and Ableton in the same network. For setup please refer to [this section](#network).
1. Press "Active" to close/start connection with Ableton. If connected shows 1 the connection was sucessful.
2. Monitor the knobs to see how the values from sensors/camera/speech detection influence different parameters in Ableton.

# Logger⚪

Shows all incoming/outgoing python messages. Useful for debugging.

---------

# Ableton