# Tracker program version 4

from pid import PID
from picamera import PiCamera
from brightKlass import Bright
from multiprocessing import Manager
from multiprocessing import Process
from imutils.video import VideoStream
import os
import cv2
import sys
import time
import pigpio # 2020-03-23: RPi.GPIO är kass
import signal
import numpy as np



# Signalhaterare för CTRL+C
def CTRLC_handler(sig, frame):
	print("CTRL+C pressed")
	setAngles(90, 90, Manager().Value("r", False))
	time.sleep(2)
	cv2.destroyAllWindows()
	sys.exit()
#####################################################################
#
# obj_center: Läser in bild från kameran och uppdaterar koordinater för center och för objektet
#
# IN: Processäkra variabler för respektive koordinat
#
# OUT: Uppdaterar processäkra variabler för motsvarande koordinater utifrån bild från kameran.
#  
def obj_center(objX, objY, cenX, cenY, radie, servoPin):
	
	print("obj_center ready to go!")
	time.sleep(1)
	signal.signal(signal.SIGINT, CTRLC_handler)
	vs = VideoStream(usePiCamera=True, resolution=(320, 240)).start()
	time.sleep(2.0)

	# initiera brightKlass som Bright()	
	obj = Bright(radie)
	
	
	while servoPin.value:
		frame = vs.read()
		orig = frame.copy()
		cenX.value, cenY.value = .5*int(frame.shape[1]), -.5*int(frame.shape[0])	
		locXY = obj.bright(frame)
		objX.value, objY.value = locXY[0], -1*locXY[1]

        # Visar bilden på skärmen
		orig = cv2.resize(orig, (1280, 720), interpolation = cv2.INTER_LINEAR)
		cv2.circle(orig, (int(1280*objX.value/320), int(-720*objY.value/240)), radie, (0, 255, 0), 2)	
		cv2.imshow("imshow", orig)
		
				
		# <ESC> för att stänga video och döda programmet
		if cv2.waitKey(1) == 27:
			print("<ESC> pressed! \nPlease wait!")
			servoPin.value = False
			time.sleep(1)
			break
	

#####################################################################
#
# piddKontrollerX: Regulerar vinkeln på motorn för höger-vänsterrörelse
#
# IN: Processäkra variabler: nuvarande vinkel, pid-konstanter, x-koordinater för center och för objektet
#
# OUT: Uppdaterar nuvarande vinkel för motorn i höger-vänsterled
#
def pidKontrollerX(output, p, i, d, loc, center, servoRuns):
	signal.signal(signal.SIGINT, CTRLC_handler)
	p = PID(p.value, i.value, d.value)
	p.initialize()
	
	print("Xpid controller ready to go!")
	while servoRuns.value:
		err = center.value - loc.value
		toUpdate = p.update(err) + 90

		# Ändlägen
		if toUpdate > 169:
			toUpdate = 169
		if toUpdate < 11:
			toUpdate = 11
		output.value = toUpdate

#####################################################################
#
# pidKontrollerY: Regulerar vinkeln på motorn för upp-nedrörelse
#
# IN: Processäkra variabler: nuvarande vinkel, pid-konstanter, y-koordinater för center och för objektet
#
# OUT: Uppdaterar nuvarande vinkel för motorn uppåt/nedåt
#
def pidKontrollerY(output, p, i, d, loc, center, servoRuns):
	# Signal handler
	signal.signal(signal.SIGINT, CTRLC_handler)
	# Initiera pidkontrollern med valda gains
	p = PID(p.value, i.value, d.value)
	p.initialize()
	
	print("Ypid controller ready to go!")
	while servoRuns.value:
		err = center.value - loc.value
#		print(str([center.value, loc.value]))
#		print(str(err))
#		print(str(output.value))
		toUpdate = p.update(err) + 90

		# Ändlägen
		if toUpdate > 97:
			toUpdate = 97
		if toUpdate < 40:
			toUpdate = 40
		output.value = toUpdate
#####################################################################
#
# setAngles: Omvandlar vinklar till motsvarande utsignal till respektive motor
#
# IN: Processäkra variabler: vinkar för respektive motor
#
# OUT: Skickar utsignal till respektive motor för att sätta önskad vinkel
#
def setAngles(Xangle, Yangle, servoRuns):
	signal.signal(signal.SIGINT, CTRLC_handler)

	# Pin för pan
	xPin = 2
	# Pin för tilt
	yPin = 22

	# MIN_WIDTH = 1000
	# MAX_WIDTH = 2000

	# GPIO-bibliotek
	pi = pigpio.pi()

	# Avsluta om pi inte hittas
	if not pi.connected:
		exit()
	
	# Så att man kan välja pan/tilt GPIO-portar via sys.argv
	if len(sys.argv) == 1:
		G = [xPin, yPin]
	elif len(sys.argv) == 3:
		G = []
		for XYpins in sys.argv[1:]:
			G.append(int(XYpins))
	else:
		print("setAngles NOT ready to go!")
		print("Use programme this way: ")
		print(">> python3 tracker3.py \nor")
		print(">> python3 tracker3.py [pan-GPIO] [tilt-GPIO]")
		print("Exiting setAngles")
		servoRuns.value = False
		exit()
	# Sätter servos till 90 deg	
	for g in G:
		pi.set_servo_pulsewidth(g, 1500)

	if servoRuns.value:
		print("setAngles ready to go!")

	while servoRuns.value:

		pulseX = 1000 + 1000*Xangle.value/180
		pulseY = 1000 + 1000*Yangle.value/180
		
		pulses = [pulseX, pulseY]
		
		# Skickar PWM-signal till servos
		for g in enumerate(G):
			pi.set_servo_pulsewidth(g[1], pulses[g[0]])

	# Går tillbaka till 90 deg innan avstängning
	print("Shutting down servos")
	for g in G:
		pi.set_servo_pulsewidth(g, 1500)
		time.sleep(2)
		pi.set_servo_pulsewidth(g, 0)
	pi.stop()
	exit()	

#####################################################################
#
# Main: Initierar processäkra variabler och definierar radien för objektet som ska spåras. Definierar och kör sedan processerna parallellt.
#
#
if __name__ == "__main__":
	
	radius = 41 # Måste vara udda för Gaussian Blur

	with Manager() as manager:
		# Process safe variables
		
		# Processer körs så länge s=True
		s = manager.Value("r", True)
		
		# Vinklar
		xAngle = manager.Value("i", 90)
		yAngle = manager.Value("i", 90)
		
		# Koordinater för centrum
		centerX = manager.Value("i", 0)
		centerY = manager.Value("i", 0)
		
		# Objektets x-/y-koordinater
		objX = manager.Value("i", 0)
		objY = manager.Value("i", 0)
		
		# Gains för pan
		xP = manager.Value("f", 0.19)
		xI = manager.Value("f", 0.22)
		xD = manager.Value("f", 0.0038)
		
		# Gains för tilt
		yP = manager.Value("f", 0.11) # 0.11
		yI = manager.Value("f", 0.3) # 0.3
		yD = manager.Value("f", 0.0042) # 0.0042
		
		# processer	
		pSnap = Process(target=obj_center, args=(objX, objY, centerX, centerY, radius, s))
		pPIDx = Process(target=pidKontrollerX, args=(xAngle, xP, xI, xD, objX, centerX, s))
		pPIDy = Process(target=pidKontrollerY, args=(yAngle, yP, yI, yD, objY, centerY, s))
		pSetAngle = Process(target=setAngles, args=(xAngle, yAngle, s))
		
		# starta processerna
		pSnap.start()
		pPIDx.start()
		pPIDy.start()
		pSetAngle.start()
		
		# join
		pSnap.join()
		pPIDx.join() 
		pPIDy.join()
		pSetAngle.join()
		
		# döda
		cv2.destroyAllWindows()
		print("END OF CODE, exiting...")
		exit()
		
		
