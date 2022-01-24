from gda.device.scannable import ScannableMotionBase
from gda.epics import CAClient 

from time import sleep

class DisplayEpicsPVClassLS(ScannableMotionBase):
	def __init__(self, name, pvstring, unitstring, formatstring, channel, level):
		self.name = name;
		self.inputNames = [name]
		self.outputFormat = [formatstring]
		self.level = level
		self.KRDG = CAClient(pvstring + 'KRDG' + channel)
		self.KRDG.configure()

	def getPosition(self):
		return float(self.KRDG.caget())
		
	def isBusy(self):
		sleep(0.1)
		return False


class DisplayEpicsPVClassLS2(DisplayEpicsPVClassLS):

	def __init__(self, name, pvstring, unitstring, formatstring, channel,level):
		DisplayEpicsPVClassLS.__init__(self,  name, pvstring, unitstring, formatstring, channel, level)
		self.extraNames = [name]
		self.SRDG = CAClient(pvstring + 'SRDG' + channel)
		self.SRDG.configure()
		self.outputFormat = [formatstring, formatstring]

	def getPosition(self):
		return float(self.KRDG.caget()), float(self.SRDG.caget())
		



