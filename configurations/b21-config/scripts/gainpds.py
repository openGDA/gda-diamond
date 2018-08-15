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

class AmpGain(PseudoDevice):
	'''Create PD to select Amplifier Gain'''
	def __init__(self, name, pvstring):
		self.setName(name);
		self.setInputNames([name])
		self.setOutputFormat(["%s"])
		self.pvstring=pvstring
		epicsnamelist=[".ZRST", ".ONST", ".TWST", ".THST", ".FRST", ".FVST", ".SXST", ".SVST", ".EIST", ".NIST", ".TEST", ".ELST", ".TVST", ".TTST", ".FFST"]
		self.namelist=epicsnamelist

	def getPositions(self):
		slots=[]
		for i in self.namelist:
			slots = slots + [ caget(self.pvstring+i) ]
		return slots

	def getPosition(self):
		return self.int2str(int(caget(self.pvstring)))
	
	def asynchronousMoveTo(self,p):
		if type(p) == type("string"):
			p = self.str2int(p)
		caput(self.pvstring,p)

	def isBusy(self):
		return 0

	def int2str(self, num):
		n=0
		for i in self.namelist:
			if num == n:
				return caget(self.pvstring+i)
			n += 1
		return "Unknown"
		
	def str2int(self, string):
		n=0
		for i in self.namelist:
			if string == caget(self.pvstring+i):
				return n
			n += 1
		return 0

d4d6gain=AmpGain("d4d6gain","BL22I-DI-IAMP-03:RANGE_MENU")
bsdiodegain=AmpGain("bsdiodegain","BL22I-DI-IAMP-10:GAIN")
d10d1gain=AmpGain("d10d1gain","BL22I-DI-IAMP-17:GAIN")
d10d2gain=AmpGain("d10d2gain","BL22I-DI-IAMP-18:GAIN")
