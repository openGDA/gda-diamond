from gda.epics import CAClient
from java import lang
import time
import math
from gda.device.scannable import PseudoDevice
from gda.device import DeviceException

class Cryojet(PseudoDevice):
	'''Create PD to operate Oxford Cryojet'''
	def __init__(self, name, pvstring):
		self.setName(name)
		self.pvbase = pvstring
		self.temp=CAClient(pvstring+":STEMP")
		self.target=CAClient(pvstring+":TTEMP:SET")
		self.err=CAClient(pvstring+":TEMP:ERR")
		self.sampleflw=CAClient(pvstring+":SAMPLEFLW:SET")
		self.shieldflw=CAClient(pvstring+":SHIELDFLW:SET")
		self.heatmode=CAClient(pvstring+":ACTIVITY:SET")
		self.ctrlmode=CAClient(pvstring+":CTRL:SET")
		self.maxv=CAClient(pvstring+":MAXV:SET")
		self.disable=CAClient(pvstring+":DISABLE")
		self.temp.configure()
		self.target.configure()
		self.err.configure()
		self.sampleflw.configure()
		self.shieldflw.configure()
		self.heatmode.configure()
		self.ctrlmode.configure()
		self.maxv.configure()
		self.disable.configure()
		self.heatmode.caput("Auto")
		self.ctrlmode.caput("EPICS+FPLock")
		self.state=0
		self.nextmove=298
		
		
	
	def getStatus(self):
		return self.status.caget()
	
	def setTemp(self, temp):
		self.target.caput(temp)
	
	def getTemp(self):
		return float(self.temp.caget())
	
	def setFlow(self, sample, shield):
		self.sampleflw.caput(sample)
		self.shieldflw.caput(shield)
		
	
	def setV(self, v):
		self.maxv.caput(v)
	
	def getPosition(self):
		if int(self.disable.caget()) == 1:
			raise DeviceException(self.getName()+" disabled in EPICS")
		else:
			return [float(self.temp.caget())]
		
	
	def wait(self, timeout, period):
		mustend = time.time() + timeout
		while time.time() < mustend:
			if self.state == 0 : return 0
			time.sleep(period)
			return 1
		
	def asynchronousMoveTo(self,p):
		if int(self.disable.caget()) == 1:
			raise DeviceException(self.getName()+" disabled in EPICS")
		self.nextmove=p
		t=float(self.temp.caget())
		l=float(self.target.caget())
		if (0.05 >= math.fabs(p-t)):
			self.state=0
			return
		if (p>t):
			self.state=1
			if (l<p):
				self.setTemp(p)
		if (p<t):
			self.state=-1
			if (l>p):
				self.setTemp(p)
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
