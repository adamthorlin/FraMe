############################################################
############################################################
##
## Name         :   pid.py
##
## Description  :   Class for the pid controller. The 
##                  constant gains are initialized as
##                  class attributes, and the code 
##                  functions as a PID-controller
##
############################################################
############################################################
##
## Authors      :   Grahn, Anton & Adam Thalin
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

import time

###############################################
# PID: Holds the value of the constant gains #
#############################################

class PID:
	def __init__(self, kP=0, kI=0, kD=0):
		self.kP = kP
		self.kI = kI
		self.kD = kD

	def initialize(self):
		self.tNuv = time.time()
		self.tOld = self.tNuv
		
		self.oldErr = 0
		self.cP, self.cI, self.cD = 0, 0, 0
	
#########################################################
#                                                      #
# update: Controls the control signal (u) based on a  #
#         control error (e(t)) like a PID-controller #
#                                                   #
# IN: Control error                                #
#                                                 #
# OUT: Regulated output value                    #
#                                               #
################################################

	def update(self, err, delay = 0.2):
		time.sleep(delay)
		
		self.tNuv = time.time()
		dt = self.tNuv - self.tOld
		dErr = err - self.oldErr
		
		self.cP = err
		
		self.cI += err * dt

		############################################
		# 2020-03-23: Constraints so that the      #
                #             integral-part does not go to #
                #             infinity, which causes the   #
                #             camera to be caught in an    #
                #             end position                 #
		if self.cI > 150:                          #
			self.cI = 150                      #
		if self.cI < -150:                         #
			self.cI = -150                     #
                ############################################
		
		if dt > 0:
			self.cD = (dErr/dt)
		else:
			self.cD = 0
		
		self.tOld = self.tNuv
		self.oldErr = err
		
		P = self.kP * self.cP
		I = self.kI * self.cI
		D = self.kD * self.cD
		
		return sum([P, I, D])
	
