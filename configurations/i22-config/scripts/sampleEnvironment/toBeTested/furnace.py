from gda.epics import CAClient
from java import lang
from time import sleep
import math
from gda.device.scannable import PseudoDevice
from gda.device import DeviceException

class Eurotherm(PseudoDevice):
	'''Create PD to operate Eurotherm furnace'''
	def __init__(self, name, pvstring):
		self.setName(name)
		self.pvbase = pvstring
		self.temp=CAClient(pvstring+":PV:RBV")
		self.ramplmt=CAClient(pvstring+":SP")
		self.ramprte=CAClient(pvstring+":RR")
		self.power=CAClient(pvstring+":O")
		self.mode=CAClient(pvstring+":MAN")
		self.pidp=CAClient(pvstring+":P")
		self.pidi=CAClient(pvstring+":I")
		self.pidd=CAClient(pvstring+":D")
		self.disable=CAClient(pvstring+":DISABLE")
		self.temp.configure()
		self.ramplmt.configure()
		self.ramprte.configure()
		self.power.configure()
		self.mode.configure()
		self.pidp.configure()
		self.pidi.configure()
		self.pidd.configure()
		self.disable.configure()
		self.mode.caput("Manual")
		self.power.caput(0.0)
		self.state=0
		self.nextmove=25
		self.nextLimit = None
		

	
	def setRate(self, rate):
		self.ramprte.caput(rate / 60.0)

	def getRate(self):
		return float(self.ramprte.caget()) * 60.0

	def setLimit(self, limit):
		self.ramplmt.caput(limit)

	def getLimit(self):
		return float(self.ramplmt.caget())

	def start(self):
		self.mode.caput("Automatic")
	
	def stop(self):
		self.mode.caput("Manual")
		self.power.caput(0.0)
		self.state=0

	def setNextScanLimit(self, limit):
		self.nextLimit = limit

	def atScanStart(self):
		if not self.nextLimit == None:
			self.setLimit(self.nextLimit)
			self.nextLimit = None

	def atScanEnd(self):
		self.state=0

	def getPosition(self):
		if int(self.disable.caget()) == 1:
			raise DeviceException(self.getName()+" disabled in EPICS")
		else:
			return [float(self.temp.caget())]
		
	def asynchronousMoveTo(self,p):
		if int(self.disable.caget()) == 1:
			raise DeviceException(self.getName()+" disabled in EPICS")
		self.nextmove=p
		t=float(self.temp.caget())
		l=float(self.ramplmt.caget())
		if (0.05 >= math.fabs(p-t)):
			self.state=0
			return
		if (p>t):
			self.state=1
			if (l<p):
				self.setLimit(p)
		if (p<t):
			self.state=-1
			if (l>p):
				self.setLimit(p)
		self.start()			
		return

	def isBusy(self):
		if (self.state==0):
			return 0
		if (self.state > 0):
			if (float(self.temp.caget()) + 0.05 >= self.nextmove):
				return 0
			else:
				return 1
		if (self.state < 0):
			if (float(self.temp.caget()) - 0.05 <= self.nextmove):
				return 0
			else:
				return 1
