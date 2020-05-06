# Klass som håller reda på ljusaste punkten i bilden
import cv2
import numpy as np


class Bright():
	def __init__(self, radie):
		self.radie = radie
	
	def bright(self, image): # update	
		gray = cv2.GaussianBlur(cv2.cvtColor(image, cv2.COLOR_BGR2GRAY), (self.radie, self.radie), 0)
		
		# Ljusaste (x, y) 
		(minVal, maxVal, minLoc, maxLoc) = cv2.minMaxLoc(gray)

		# Minigardering mot bug som gör att hörnet returneras om ingen ljusaste punkt hittas.
		if maxLoc[0]==0 and maxLoc[1]==0:
			maxLoc = [160, 120]

		return maxLoc
	
		
