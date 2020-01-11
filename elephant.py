#
# elephant.py
#

from threading import Thread
from adafruit_servokit import ServoKit
from gpiozero import LED,Button,Servo
import time
import random
import board
import neopixel
import subprocess
import os.path

print("Initializing...")

# pin definitions
PIN_LEFT_EYE	= 17
PIN_LEFT_BROW	= 23
PIN_RIGHT_EYE	= 27
PIN_RIGHT_BROW	= 24
PIN_SENSOR	= 25
PIN_BUTTON	= 22

# TODO: choose a random WAV file from subfolder
# otherwise you will always be rick rolled
soundFile = "/home/pi/rickroll.wav"

# if this file exists, the the program will exit
# this is how to we stop the program gracefully
stopFile = "/home/pi/elephant.stop"
keepRunning = True

servoEarRight = 0 # the servo channel number for the left ear
servoEarLeft = 15 # the servo channel number for the right ear
kit = ServoKit(channels=16)

leftEye = LED(PIN_LEFT_EYE)
leftBrow = LED(PIN_LEFT_BROW)
rightEye = LED(PIN_RIGHT_EYE)
rightBrow = LED(PIN_RIGHT_BROW)
sensorInput = Button(PIN_SENSOR, pull_up=False)
buttonInput = Button(PIN_BUTTON, pull_up=False)

neoCount = 10 # the number of pixels in the strip
neoDelay = 0.5 # the amount of time to wait before changing effects
# change the NeoPixel pin in the next line
neoPixels = neopixel.NeoPixel(board.D10, neoCount)

servoValue = 0.0 # the current servo angle
servoMin = 90 # the minimum allowable servo angle, depends on library
servoMax = 180 # the maximum allowable servo angle, depends on library
servoDirection = 1.0 # will always be positive 1 or negative 1
servoStep = 10.0 # the amount the servo moves in each iteration
servoDelay = 0.05 # the amount to wait before moving the servo in each iteration
servoEnabled = False # the button will toggle this value

browState = 0 # 0 is off and 1 is on, the loop changes this value
eyeState = 0 # 0 is off and 1 is on, the loop changes this value
eyeDelay = 0 # see below, when state=1 the delay is long, when state=0 the delay is short
eyeDelayOn = 6 # the amount of seconds the eyes are on
eyeDelayOff = 1 # the amount of seconds the eyes are off
buttonDelay = 10 # the amount of time the servo is enabled after button press

# turn off all the LEDs
leftEye.off()
leftBrow.off()
rightEye.off()
rightBrow.off()

# start any process that exits immediatly so that the omxprocess variable is defined for down below
omxprocess = subprocess.Popen(['/bin/false'], stdin=subprocess.PIPE, stdout=None, stderr=None, bufsize=0)

# display all GREEN
neoPixels.fill((0, 255, 0))
neoPixels.show()
time.sleep(1)

# display all RED
neoPixels.fill((255, 0, 0))
neoPixels.show()
time.sleep(1)

def wheel(pos):
    if pos < 0 or pos > 255:
        r = g = b = 0
    elif pos < 85:
        r = int(pos * 3)
        g = int(255 - pos * 3)
        b = 0
    elif pos < 170:
        pos -= 85
        r = int(255 - pos * 3)
        g = 0
        b = int(pos * 3)
    else:
        pos -= 170
        r = 0
        g = int(pos * 3)
        b = int(255 - pos * 3)
    return (r, g, b)

for j in range(255):
	for i in range(neoCount):
		pixel_index = (i * 256 // neoCount) + j
		neoPixels[i] = wheel(pixel_index & 255)
	neoPixels.show()
	time.sleep(0.001)

# The main loop is implemented as a timed-loop that enables certain
# behaviors at certain intervals. These intervals as maintained by 
# remembering when the last behavior occurred (in seconds) and only
# enabling the next behavior when a certain amount of time has surpased.
# To accomplish this, we check the current time vs the behavior time,
# see the main loop for more details.
currentTime = time.perf_counter()
neoTime = currentTime
eyeTime = currentTime
servoTime = currentTime
buttonTime = currentTime

def color_chase(color, wait, dir):
	for i in range(neoCount):
		if dir == -1:
			i = neoCount - i - 1
		neoPixels[i] = color
		time.sleep(wait)
		neoPixels.show()
	time.sleep(0.05)

RED	= (255, 0, 0)
YELLOW	= (255, 150, 0)
GREEN	= (0, 255, 0)
CYAN	= (0, 255, 255)
BLUE	= (0, 0, 255)
PURPLE	= (180, 0, 255)

# DESIGN: we control the neopixels from a separate thread
# because the main loop is implemented as a timed-loop
# (i.e. minimize usage of sleep calls) vs a busy-wait-loop
# (i.e. use sleep to control timing). A busy-wait-loop is always
# inefficient so therefore dedicate a separate thread for that.
class NeoManager:
	def run(self):
		while keepRunning:
			color_chase(RED, 0.05, 1)
			color_chase(YELLOW, 0.05, -1)
			color_chase(GREEN, 0.05, 1)
			color_chase(CYAN, 0.05, -1)
			color_chase(BLUE, 0.05, 1)
			color_chase(PURPLE, 0.05, -1)
		print("NeoPixel thread exiting")

# start the NeoPixel thread
neoManager = NeoManager()
neoThread = Thread(target=neoManager.run)
neoThread.start()

# wheeeeee......
print("Main loop starting")
while keepRunning:
	currentTime = time.perf_counter()

	# toggle the eyebrows from the motion sensor
	if sensorInput.value:
		if browState == 0:
			print("Enable Brows")
		browState = 1
		leftBrow.on()
		rightBrow.on()
	else:
		if browState == 1:
			print("Disable Brows")
		browState = 0
		leftBrow.off()
		rightBrow.off()

	# enable the servo for a period of time after the button is pressed
	if buttonInput.value:
		if not servoEnabled:
			print("Servo enabled")
			# audio is played by starting the omxplayer in a child process
			# but we protect our selves from playing again while already
			# playing by checking the exitcode of the process. If the result
			# of poll() is None then the audio is still playing.
			if not omxprocess.poll() is None:
				print("Playing sound")
				omxprocess = subprocess.Popen(['omxplayer', '--adev', 'local', '--vol', '90', soundFile], stdin=subprocess.PIPE, stdout=None, stderr=None, bufsize=0)
		servoEnabled = True
		buttonTime = currentTime
	elif servoEnabled and currentTime > (buttonTime + buttonDelay):
		print("Servo disabled")
		servoEnabled = False

	# toggle the eyes periodically, on-time is long, off-time is short
	if currentTime > (eyeTime + eyeDelay):
		eyeTime = currentTime
		if eyeState == 0:
			print("Enable Eyes")
			eyeState = 1
			eyeDelay = eyeDelayOn
			leftEye.on()
			rightEye.on()
		else:
			print("Disable Eyes")
			eyeState = 0
			eyeDelay = eyeDelayOff
			leftEye.off()
			rightEye.off()

	# if enabled, move the servos
	if servoEnabled and currentTime > (servoTime + servoDelay):
		servoTime = currentTime
		# calculate the next servo value
		servoValue = servoValue + (servoStep * servoDirection)
		# check for allowable maximum value
		if servoValue >= servoMax:
			servoValue = servoMax
			servoDirection = -1.0
		# check for allowable minimum value
		elif servoValue <= servoMin:
			servoValue = servoMin
			servoDirection = 1.0
		print(f"Servo Value = {servoValue}")
		# for the left servo we have to subtract 180
		# because its mounted mirror opposite of the right side
		kit.servo[servoEarLeft].angle = 180 - servoValue
		kit.servo[servoEarRight].angle = servoValue

	# if the stop file exists, then thats an instruction to exit the program
	keepRunning = not os.path.isfile(stopFile)

# bye bye...
print("Main loop exiting")

# if the audio is still playing, instruct the player to quit
if omxprocess.poll() == None:
	print("Attempting to stop audio")
	omxprocess.stdin.write(b'q')
