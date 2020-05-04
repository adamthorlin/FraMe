# PID-kontroller
import time

class PID:
	# Konstanta gains
	def __init__(self, kP=1, kI=0, kD=0):
		self.kP = kP
		self.kI = kI
		self.kD = kD

	def initialize(self):
		# delta t (tid)
		self.tNuv = time.time()
		self.tOld = self.tNuv
		
		# variabeldeklaration
		self.oldErr = 0
		self.cP, self.cI, self.cD = 0, 0, 0
	
	# Uppdatera utsignalen baserat på felet
	def update(self, err, delay = 0.2):
		time.sleep(delay)
		
		# dt för diskret integration och derivata
		self.tNuv = time.time()
		dt = self.tNuv - self.tOld
		dErr = err - self.oldErr
		
		self.cP = err		# proportionell del
		
		self.cI += err * dt # integraldel
		
		# 2020-03-23: Så att kameran inte kan fastna i ett ändläge för länge
		if self.cI > 150:
			self.cI = 150 
		if self.cI < -150:
			self.cI = -150
		# print(str(self.cI))
		
		if dt > 0:
			self.cD = (dErr/dt) # deriverande del
		else:
			self.cD = 0
		
		self.tOld = self.tNuv # För delta t
		self.oldErr = err	  # För delta err
		
		# "Baka ihop" och returnera utsignal
		P = self.kP * self.cP
		I = self.kI * self.cI
		D = self.kD * self.cD
		
		return sum([P, I, D])
	
