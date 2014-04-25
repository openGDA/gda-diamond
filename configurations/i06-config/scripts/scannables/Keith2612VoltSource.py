from gda.device.scannable import ScannableMotionBase
from time import sleep

class Keith2612VoltSource(ScannableMotionBase):
	def __init__(self, name, KeithleyClass, channel):
		#function = 0 (current source), 1 (voltage source)
		#
		self.setName(name)
		self.setInputNames(['Volt'])
		self.setExtraNames([])
		self.setOutputFormat(['%3.3e'])
		
		self.setLevel(10+channel) 
		self.channel = channel
		
		self.PS = KeithleyClass
		self.PS.setFunction(1)	#set keithley as voltage source
		self.currentPosition = 0#self.PS.getVoltage()
		self.iambusy = 0

	def atScanStart(self):
		self.PS.turnOn()
		return;

	def atScanEnd(self):
		#self.PS.turnOff()
		return;

	def getPosition(self): 
		self.iambusy = 1
		self.currentPosition = self.PS.getVoltage()
		self.iambusy = 0
		return float(self.currentPosition) 

	def asynchronousMoveTo(self, newPosition):
		self.PS.setVoltage(newPosition) 
		#if (newPosition==0):
		#	self.PS.turnOff()
		#else:
		#	self.PS.turnOn()
		sleep(2)	  #this delay is necessary, because after setting the voltage, the instrument takes 2 sec to answer
		#sleep(0.5)	# Is 0.5s enough?
		return None

	def isBusy(self):
		return self.iambusy

#volt=Keith2612VoltSource('volt', Keithley, 1)