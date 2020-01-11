# Overview
TODO

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
