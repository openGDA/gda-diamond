from gda.device.scannable import ScannableMotionBase
from gda.epics import CAClient 
from time import sleep

class ToggleBinaryPvDuringScan(ScannableMotionBase):
	
	def __init__(self, name, pvstring, normalLevel=True, leave_at_end=False):
		self.name = name
		self.cli = CAClient(pvstring)
		self.setInputNames([])
		self.setOutputFormat([])
		self.setLevel(10)
		self.cli.configure()
		self.normalLevel = normalLevel
		self.leave_at_end = leave_at_end

	def setOutsideScan(self): 
		if self.normalLevel==True:
			self.cli.caput('on')
		else:
			self.cli.caput('off')			

	def setInsideScan(self): 
		if self.normalLevel==True:
			self.cli.caput('off')
		else:
			self.cli.caput('on')
			

	def atScanStart(self):
		self.setOutsideScan()
		sleep(1)
		print "* enable bo1"
		self.setInsideScan()
		
	def atScanEnd(self):
		if not self.leave_at_end:
			print "* disable bo1"
			self.setOutsideScan()

	def isBusy(self):
		return False
	
	def getPosition(self):
		return None


