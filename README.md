# FraMe
Python code to my bachelor's thesis project in MF133X Mechatronics at KTH, Spring 2020. A pan-tilt camera mount that uses an infrared camera to detect a bright object, and with the help of two servo motors, keep the object centered in the image.

 Authors      :   Grahn, Anthon & Thalin, Adam

 Course       :   Bachelor's thesis in Mechatronics,
                  MF133XVT20                 
                                            
 Institute    :   Department of Mechatronics, School of
                  Industrial Engineering and Management,
                  Royal Institute of Technology, Stockholm
 Last edited  :   2020-05-22

 Name         :   FraMe.py                                                                                                           
 Description  :   FraMe.py is the main script for FraMe.
                  It is ran on a Raspberry Pi 3 B+ and 
                  controls two servo motors that rotate a
                  camera in order to identfy a target and
                  keep it centered in the picture.
                                                        
                  The script uses two classes that are put
                  in separate files:                   
                                                     
                  --"brightKlass.py"--                 
                  Contains the class that processes an  
                  image and returns the coordinates for  
                  the brightest spot in the prosessed   
                  image.                                 
                  ****************************************
                  --"pid.py"--                             
                  Contains the class that defines the       
                  PID-controller that is used to control     
                  the angles of the servo motors.             
                  ****************************************     
                                                     
                  No user interface is needed, but the
                  GPIO-pins for each servo motor can be
                  defined via commandline arguments. If
                  no arguments are given, default is set 
                  to 2 and 22, for the pan- and tilt-servo
                  respectively.                    
                                                    
                  The stream from the picamera can be
                  displayed locally or forwarded to an
                  an external device via an
                  SSH-connection.
