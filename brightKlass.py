# brightKlass
# 
# Property of Adam Thalin and Anton Grahn
#
# 2020-05-08

import cv2
import numpy as np


# Klass for att halla reda pa ljusaste punken i bilden
class Bright():
	def __init__(self, radie):
		self.radie = radie
	
#################################################################
#
# bright: Tar en bild och returnerar koordinater for ljuste punkten i bilden
#
	def bright(self, image): # update	
		gray = cv2.GaussianBlur(cv2.cvtColor(image, cv2.COLOR_BGR2GRAY), (self.radie, self.radie), 0)
		
		# minMaxLoc returnerar koordinater for ljusaste och morkaste punkten i bilden.
		(minVal, maxVal, minLoc, maxLoc) = cv2.minMaxLoc(gray)

		# Gardering mot bug som gor att hornet returneras om ingen ljusaste punkt hittas
		if maxLoc[0]==0 and maxLoc[1]==0:
			maxLoc = [160, 120]

		return maxLoc
	
		
