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
	def __init__(self, name, pvinstring, unitstring, formatstring):
		self.setName(name);
		self.setInputNames([name])
		self.Units=[unitstring]
		self.setOutputFormat([formatstring])
		self.setLevel(3)
		self.incli=CAClient(pvinstring)

	def getPosition(self):
		try:
			self.incli.configure()
			output=float(self.incli.caget())
			self.incli.clearup()
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
	

usery_centre_speed=EpicsSetGetClass("usery_centre_speed","BL22I-MO-USER-01:Y:CENTER.VELO","","%4.4f")
usery_size_speed=EpicsSetGetClass("usery_size_speed","BL22I-MO-USER-01:Y:SIZE.VELO","","%4.4f")

