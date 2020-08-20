from gda.device.scannable import ScannableMotionBase

class Keith2612CurrentMeter(ScannableMotionBase):
	def __init__(self, name, KeithleyClass, channel):
		#function = 0 (current source), 1 (voltage source)
		self.setName(name)
		self.setInputNames(['Ampere'])
		self.setExtraNames([])
		self.setOutputFormat(['%3.3e'])
		
		self.setLevel(12+channel) 
		self.channel = channel
		
		self.PS = KeithleyClass
		self.PS.setFunction(1)	#set keithley as voltage source
		self.currentPosition = 0 #self.PS.getVoltage()
		self.iambusy = 0

	#ScannableMotionBase Implementation
	def atScanStart(self):
		return;

	def atScanEnd(self):
		return;

	def getPosition(self): 
		self.iambusy = 1
		print('measuring current...')
		self.currentPosition = self.PS.getCurrent()
		self.iambusy = 0
		return float(self.currentPosition) 

	def asynchronousMoveTo(self, newPosition):
		return None

	def isBusy(self):
		return self.iambusy

#curr=Keith2612CurrentMeter('curr', Keithley, 1)
