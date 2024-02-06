## RGBproject Hydra Module

# Communication between TouchDesigner and Logic Pro

**Make sure that both computers are in the same network.**

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
4. Launch TouchDesigner version 2023

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

# TouchDesigner

1. Open RGBPrototype.toe. The file opens up in perform mode, however if you see nodes, press F1.

# Logic Pro