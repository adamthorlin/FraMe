# PID-kontroller
# 
# Property of Adam Thålin and Anton Grahn
#
# 2020-05-08

import time

# Klass for pid-kontrollern
class PID:
	# Konstanta gains som publika attribut
	def __init__(self, kP=0, kI=0, kD=0):
		self.kP = kP
		self.kI = kI
		self.kD = kD

    # Initiera variabler
	def initialize(self):
		# delta t (tid)
		self.tNuv = time.time()
		self.tOld = self.tNuv
		
		# variabeldeklaration
		self.oldErr = 0
		self.cP, self.cI, self.cD = 0, 0, 0
	
	#################################################################
    #
    # update: Uppdaterar vardet pa utsignalen som en pid-kontroller
    #
    # IN: Skillnaden mellan nuvarande utsignal och onskad utsignal (felet)
    #
    # OUT: Reglerade vardet pa utsignalen
    #
	def update(self, err, delay = 0.2):
		time.sleep(delay)
		
		# dt for diskret integration och derivata
		self.tNuv = time.time()
		dt = self.tNuv - self.tOld
		dErr = err - self.oldErr
		
		self.cP = err		# proportionell del
		
		self.cI += err * dt # integraldel
		
		# 2020-03-23: Sa att kameran inte kan fastna i ett andlage for lange
		if self.cI > 150:
			self.cI = 150 
		if self.cI < -150:
			self.cI = -150
		# print(str(self.cI))
		
		if dt > 0:
			self.cD = (dErr/dt) # deriverande del
		else:
			self.cD = 0
		
		self.tOld = self.tNuv # For delta t
		self.oldErr = err	  # For delta err
		
		# "Baka ihop" och returnera reglerad utsignal
		P = self.kP * self.cP
		I = self.kI * self.cI
		D = self.kD * self.cD
		
		return sum([P, I, D])
	
