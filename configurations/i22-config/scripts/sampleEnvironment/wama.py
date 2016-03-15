from gda.epics import CAClient
from java import lang
from time import sleep
import math
from gda.device.scannable import PseudoDevice
from gda.device import DeviceException

class Wama:
	'''Create PD to operate Watson Marlow Peristaltic Pump'''
	def __init__(self, name, pvstring):
		self.name = name
		self.pvbase = pvstring
		self.running=CAClient(pvstring+":SET:RUN")
		self.speed=CAClient(pvstring+":SET:SPD")
		self.direction=CAClient(pvstring+":SET:DIR")
		self.running.configure()
		self.speed.configure()
		self.direction.configure()
		self.runningRBV=CAClient(pvstring+":INFO:RUN")
		self.speedRBV=CAClient(pvstring+":INFO:SPD")
		self.directionRBV=CAClient(pvstring+":INFO:DIR")
		self.runningRBV.configure()
		self.speedRBV.configure()
		self.directionRBV.configure()
		
	def stop(self):
		self.running.caput(0)

	def start(self, speed=None, dir=None):
		if speed != None:
			self.setSpeed(speed)
		if dir != None:
			self.setDirection(dir)
		self.running.caput(1)
		
	def setSpeed(self, rate):
		if (rate > 400 or rate < 3):
			raise DeviceException("speed outside allowed limits")
		self.speed.caput(rate)

	def setDirection(self, dir):
		if (dir != "CW" and dir != "CCW"):
			raise DeviceException("allowed directions are CW and CCW")
		self.direction.caput(dir)

	def getDirection(self):
		return self.directionRBV.caget()
		
	def getSpeed(self):
		return self.speedRBV.caget()

	def getState(self):
		if self.isRunning():
			return "Running"
		else:
			return "Stopped"
		
	def isRunning(self):
		return self.runningRBV.caget() == 1

	def getLimit(self):
		return float(self.ramplmt.caget())
	
	def __str__(self):
		if self.isRunning():
			return "Pump called %s running at speed %d in %s direction." % (self.name, int(self.getSpeed), self.getDirection())
		else:
			return "Pump called %s is stopped." % self.name


wama = Wama("wama", "BL22I-EA-PUMP-01")