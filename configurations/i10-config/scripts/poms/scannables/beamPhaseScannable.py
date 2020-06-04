""" #########################################################################################################
Scannable to monitor the phase of the beam

David Burn - 30/11/16

######################################################################################################### """

from gda.device.scannable import ScannableMotionBase
from gda.epics import CAClient


class beamPhaseScannable(ScannableMotionBase):
	def __init__(self, name):
		self.name = name
		self.setInputNames([])
		self.setExtraNames(["beam-evr", "evr-cable", "beam-cable"])
		self.setOutputFormat(["%.6g","%.6g","%.6g"])
		self.iambusy = 0 
		
		self.ca = CAClient();
		
		self.offsetC = 0
		self.offsetD = 0

	def getPosition(self):
		#a = float(ca.caget("SR23C-DI-EBPM-09:SC:PHASEA"))
		#b = float(ca.caget("SR23C-DI-EBPM-09:SC:PHASEB"))
		c = float(self.ca.caget("SR23C-DI-EBPM-09:SC:PHASEC")) - self.offsetC
		d = float(self.ca.caget("SR23C-DI-EBPM-09:SC:PHASED")) - self.offsetD
		
		return [d-c, c, d]


	def asynchronousMoveTo(self, fieldValue):
		pass


	def isBusy(self):
		return self.iambusy
	
	def getDataDimensions(self):
		return 1
	
	def resetOffsets(self):
		self.offsetC = float(self.ca.caget("SR23C-DI-EBPM-09:SC:PHASEC"))
		self.offsetD = float(self.ca.caget("SR23C-DI-EBPM-09:SC:PHASED"))
		
		print "offsets c is: %0.3f" % self.offsetC
		print "offsets d is: %0.3f" % self.offsetD
