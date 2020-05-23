############################################################
##
## Name         :   FraMe.py
##
## Description  :   This is the main script for FraMe. It is
##                  ran on a Raspberry Pi 3 B+ and controls
##                  two servo motors that rotate a camera in
##                  order to identfy a target and keep it
##                  centered in the picture.
##
##                  The script uses two classes that are put
##                  in separate files:
##
##                  --"brightKlass.py"--
##                  Contains the class that processes an
##                  image and returns the coordinates for
##                  the brightest spot in the prosessed
##                  image. 
##                  ****************************************
##                  --"pid.py"--
##                  Contains the class that defines the
##                  PID-controller that is used to control
##                  the angles of the servo motors.
##                  ****************************************
##
##                  No user interface is needed, but the
##                  GPIO-pins for each servo motor can be
##                  defined via commandline arguments. If
##                  no arguments are given, default is set
##                  to 2 and 22, for the pan- and tilt-servo
##                  respectively.
##
##                  The stream from the picamera can be
##                  displayed locally or forwarded to an
##                  an external device via an 
##                  SSH-connection.
##                  
############################################################
##
## Authors      :   Grahn, Anthon & Thalin
##
## Course       :   Bachelor's thesis in Mechatronics,
##                  MF133XVT20
##
## Institute    :   Department of Mechatronics, School of
##                  Industrial Engineering and Management,
##                  Royal Institute of Technology, Stockholm
##
## Last edited  :   2020-05-22
##
############################################################
############################################################

import os
import cv2
import sys
import time
import pigpio
import signal
import numpy as np
from pid import PID
from picamera import PiCamera
from brightKlass import Bright
from multiprocessing import Manager
from multiprocessing import Process
from imutils.video import VideoStream

############################################################
# Signalhandler for CTRL+C: Exits program in a desired way #
# if KeyboardInterrupt is raised through CTRL+C           #
##########################################################

def CTRLC_handler(sig, frame):
    print("CTRL+C pressed")
    setAngles(90, 90, Manager().Value("r", False))
    time.sleep(2)
    cv2.destroyAllWindows()
    sys.exit()

############################################################
#                                                          #
# obj_center: Captures a video frame with the camera and   #
#             updates the 2D-coordinates for the center    #
#             and the object                               #
#                                                          #
# IN: Process safe variables for each coordinate           #
#                                                         #
# OUT: Updates the process safe variables based on input #
#      from the camera                                  #
########################################################

def obj_center(objX, objY, cenX, cenY, radie, servoPin):
    
    print("obj_center ready to go!")
    time.sleep(1)
    signal.signal(signal.SIGINT, CTRLC_handler)
    vs = VideoStream(usePiCamera=True, resolution=(320, 240)).start()
    time.sleep(2.0)

    obj = Bright(radie)
    
    while servoPin.value:
        frame = vs.read()
        orig = frame.copy()
        cenX.value, cenY.value = .5*int(frame.shape[1]), -.5*int(frame.shape[0])    
        locXY = obj.bright(frame)
        objX.value, objY.value = locXY[0], -1*locXY[1]

        # Display the image
        orig = cv2.resize(orig, (1280, 720), interpolation = cv2.INTER_LINEAR)
        cv2.circle(orig, (int(1280*objX.value/320), int(-720*objY.value/240)), radie, (0, 255, 0), 2)    
        cv2.imshow("imshow", orig)
                
        # <ESC> to raise KeyboardInterrupt
        if cv2.waitKey(1) == 27:
            print("<ESC> pressed! \nPlease wait!")
            servoPin.value = False
            time.sleep(1)
            break
    
############################################################
#                                                          #
# piddKontrollerX: Controls the angle of the servo that is #
#                  responsible for the pan-motion          #
#                                                          #
# IN: Current angle, pid-gains, x-coordinates for center   #
#     and object                                           #
#                                                          #
# OUT: Updates the process safe variable for the pan-angle #
############################################################

def pidKontrollerX(output, p, i, d, loc, center, servoRuns):
    signal.signal(signal.SIGINT, CTRLC_handler)
    p = PID(p.value, i.value, d.value)
    p.initialize()
    
    print("Xpid controller ready to go!")
    while servoRuns.value:
        err = center.value - loc.value
        toUpdate = p.update(err) + 90

        # Constraints
        if toUpdate > 169:
            toUpdate = 169
        if toUpdate < 11:
            toUpdate = 11
        output.value = toUpdate

############################################################
#                                                          #
# piddKontrollerY: Controls the angle of the servo that is #
#                  responsible for the tilt-motion         #
#                                                         #
# IN: Current angle, pid-gains, y-coordinates for center #
#     and object                                        #
#                                                      #
# OUT: Updates the process safe variable for the      #
#      tilt-angle                                    #
#####################################################

def pidKontrollerY(output, p, i, d, loc, center, servoRuns):
    signal.signal(signal.SIGINT, CTRLC_handler)
    p = PID(p.value, i.value, d.value)
    p.initialize()
    
    print("Ypid controller ready to go!")
    while servoRuns.value:
        err = center.value - loc.value
        toUpdate = p.update(err) + 90

        # Constraints due to physical limitations
        if toUpdate > 97:
            toUpdate = 97
        if toUpdate < 40:
            toUpdate = 40
        output.value = toUpdate
############################################################
#                                                          #
# setAngles: Converts the angle value for each servo to a #
#            PWM signal and sets the desired angles      #
#                                                       #
# IN: Angles for both servos                           #
#                                                     #
# OUT: Sends PWM signal to the servos                #
#                                                   #
####################################################

def setAngles(Xangle, Yangle, servoRuns):
    signal.signal(signal.SIGINT, CTRLC_handler)

    # Pin for pan servo
    xPin = 2
    # Pin for tilt servo
    yPin = 22

    # GPIO-library
    pi = pigpio.pi()

    if not pi.connected:
        exit()
    
    # So that GPIO-pins also can be set with sys.argv
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
        print("where pan-GPIO is the GPIO-number for the pan motion motor\n and tilt-GPIO is the GPIO-number for the tilt motion motor")
        print("Exiting setAngles")
        servoRuns.value = False
        exit()

        # Start both servos in 90 degree angle
    for g in G:
        pi.set_servo_pulsewidth(g, 1500)

    if servoRuns.value:
        print("setAngles ready to go!")

    while servoRuns.value:

        pulseX = 1000 + 1000*Xangle.value/180
        pulseY = 1000 + 1000*Yangle.value/180
        
        pulses = [pulseX, pulseY]
        
        for g in enumerate(G):
            pi.set_servo_pulsewidth(g[1], pulses[g[0]])

    print("Shutting down servos")
    for g in G:
        pi.set_servo_pulsewidth(g, 1500)
        time.sleep(2)
        pi.set_servo_pulsewidth(g, 0)
    pi.stop()
    exit()    

############################################################
#                                                          #
# Main: Defines process safe variables and the radius for #
#       the object to be tracked                         #
#                                                       #
########################################################

if __name__ == "__main__":
    
    radius = 41 # Needs to be an odd integer

    with Manager() as manager:
        # Process safe variables
        
        # Condition variabel
        s = manager.Value("r", True)
        
        # Angles
        xAngle = manager.Value("i", 90)
        yAngle = manager.Value("i", 90)
        
        # Coordinates for center
        centerX = manager.Value("i", 0)
        centerY = manager.Value("i", 0)
        
        # Coordinates for object
        objX = manager.Value("i", 0)
        objY = manager.Value("i", 0)
        
        # PID gains for pan servo
        xP = manager.Value("f", 0.19)
        xI = manager.Value("f", 0.22)
        xD = manager.Value("f", 0.0038)
        
        # PID gains for tilt servo
        yP = manager.Value("f", 0.11)
        yI = manager.Value("f", 0.3)
        yD = manager.Value("f", 0.0042)
        
        # Define processes    
        pSnap = Process(target=obj_center, args=(objX, objY, centerX, centerY, radius, s))
        pPIDx = Process(target=pidKontrollerX, args=(xAngle, xP, xI, xD, objX, centerX, s))
        pPIDy = Process(target=pidKontrollerY, args=(yAngle, yP, yI, yD, objY, centerY, s))
        pSetAngle = Process(target=setAngles, args=(xAngle, yAngle, s))
        
        # Start
        pSnap.start()
        pPIDx.start()
        pPIDy.start()
        pSetAngle.start()
        
        # join
        pSnap.join()
        pPIDx.join() 
        pPIDy.join()
        pSetAngle.join()
        
        # Kill and exit program
        cv2.destroyAllWindows()
        print("END OF CODE, exiting...")
        exit()
        
        
