###########################################################
###########################################################
##
## Name       :  brightKlass.py
##
## Description:  Class that holds the value of the blur 
##               radius and returns coordinates of the 
##               brightest spot in a processed image or 
##               video frame.
##
############################################################
############################################################
##
## Authors    :  Grahn, Anton & Thalin, Adam
##
## Course     :  Bachelor's thesis in Mechatronics, 
##               MF133XVT20
##
## Institute  :  Department of Mechatronics, School of 
##               Industrial Engineering and Management,
##               Royal Institute of Technonogy, Stockholm
##
## Last edited:  2020-05-22
##
############################################################
############################################################

import cv2
import numpy as np

###############################################
# Bright: Holds the value of the blur radius # 
#############################################

class Bright():
	def __init__(self, radie):
		self.radie = radie
	
#########################################################
# bright: Processes an image or video fram and returns #
# coordinates for the brightest spot                  #
######################################################

	def bright(self, image):
                
                # Convert the image to black and grey and 
                # blur it
		
                gray = cv2.GaussianBlur(cv2.cvtColor(image, cv2.COLOR_BGR2GRAY), (self.radie, self.radie), 0)
		
                # Compute the coordinates

		(minVal, maxVal, minLoc, maxLoc) = cv2.minMaxLoc(gray)

		# Return coordinates for center if no
                # brightest spot is found

		if maxLoc[0]==0 and maxLoc[1]==0:
			maxLoc = [160, 120]

		return maxLoc
	
		
