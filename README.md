# Overview
http://wiki.lvl1.org/Group_Project_ELEPHANT_1.0

# Network

* MAC Address: `7c:dd:90:36:2d:56`
* Static IP: `10.0.0.191`

# Setup
Install required packages:
```
sudo apt-get update
sudo apt-get upgrade

sudo apt-get install -y python3-gpiozero
sudo apt-get install -y python-smbus
sudo apt-get install -y i2c-tools
sudo apt-get install -y omxplayer
sudo apt-get install -y python3-pip

sudo pip3 install adafruit-blinka
sudo pip3 install adafruit-circuitpython-servokit
```

Configure the python script to autostart:

`sudo nano /lib/systemd/system/elephant.service`

With the following contents:
```
[Unit]
Description=Elephant Service
After=multi-user.target

[Service]
Type=idle
ExecStart=/usr/bin/python3 /home/pi/elephant.py

[Install]
WantedBy=multi-user.target
```

Then enable the autostart script:
```
sudo chmod 644 /lib/systemd/system/elephant.service
sudo systemctl daemon-reload
sudo systemctl enable elephant.service
```

# Control
The python program will start automatically when the Pi reboots. If needbe, to stop the program, create the following file:

`touch /home/pi/elephant.stop`

Remember to delete the stop file otherwise the program will autostart and then immediately stop.

`rm /home/pi/elephant.stop`
