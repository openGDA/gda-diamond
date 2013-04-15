#
# A collection of pds representing some Epics objects
#

from gda.epics import CAClient 
from java import lang
from gda.device.scannable import PseudoDevice
from gda.device import Scannable
from time import sleep

class EpicsSetGetClass(PseudoDevice):
	'''Create PD for single EPICS positioner'''
	def __init__(self, name, pvinstring, pvoutstring, unitstring, formatstring):
		self.setName(name);
		self.setInputNames([name])
		self.Units=[unitstring]
		self.setOutputFormat([formatstring])
		self.setLevel(3)
		self.incli=CAClient(pvinstring)
		self.outcli=CAClient(pvoutstring)

	def getPosition(self):
		try:
			self.outcli.configure()
			output=float(self.outcli.caget())
			self.outcli.clearup()
			return output
		except:
			print "Error returning position"
			return 0

	def asynchronousMoveTo(self,new_position):
		try:
			self.incli.configure()
			self.incli.caput(new_position)
			self.incli.clearup()
		except:
			print "error moving to position"

	def isBusy(self):
		return 0
	

gainD4=EpicsSetGetClass("gainD4","BL22I-DI-PHDGN-04:CAM:SET_GAIN","BL22I-DI-PHDGN-04:CAM:GAIN","","%3.0f")
gainD10=EpicsSetGetClass("gainD10","BL22I-DI-PHDGN-10:CAM:SET_GAIN","BL22I-DI-PHDGN-10:CAM:GAIN","","%3.0f")
