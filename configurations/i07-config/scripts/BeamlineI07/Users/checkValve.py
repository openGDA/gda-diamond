from gda.device.scannable import ScannableMotionBase
from gda.jython import JythonServerFacade
from gda.jython.JythonStatus import RUNNING

from time import asctime, sleep
from datetime import time
from commands import getoutput


class CheckValve(ScannableMotionBase):
	'''
	Checks if Valve 8 is open, and if not, opens it
	
	'''
	def __init__(self, name):
		self.valveStatus = "BL07I-VA-VALVE-08:STA"
		self.interlockStatus = "BL07I-VA-VALVE-08:ILKSTA"
		self.control = "BL07I-VA-VALVE-08:CON"
		self.caget = "/dls_sw/epics/R3.14.12.3/base/bin/linux-x86_64/caget"
		self.caput = "/dls_sw/epics/R3.14.12.3/base/bin/linux-x86_64/caput"
		self.statusRemainedGoodSinceLastGetPosition = 1.0
	
		self.setName(name);
		self.Units=[]
		self.setOutputFormat(['%.0f'])
		self.setLevel(6)
		self.setInputNames(['valveok'])
	
	def atScanStart(self):
		self.statusRemainedGoodSinceLastGetPosition = 1.0

	def isBusy(self):
		'''This can't be used as isBusy is not checked unless the scannable
		is 'moved' by passing in a number'''
		return False
	
	def getPosition(self):
		'''Pauses until status is okay'''
		self.statusRemainedGoodSinceLastGetPosition = 1.0
		# loop until okay
		if JythonServerFacade.getInstance().getScanStatus()==RUNNING:
			valveOK = self.getStatus()
			if not valveOK:
				self.statusRemainedGoodSinceLastGetPosition = 0.0
				print "*** Valve 8 closed"	
			while not valveOK:
				sleep(5)
				interlockOK = self.getInterlock()
				if not interlockOK:
					print "*** Resetting valve interlock"
					self.setState("Reset")
					sleep(5)
				print "*** Opening valve"
				self.setState("Open")
				sleep(5)
				valveOK = self.getStatus()
				
		else: # scan not running
			currentStatus = self.getStatus()
			if not currentStatus: # bad
				print "CheckValve not holding readback as no scan is running"
			self.statusRemainedGoodSinceLastGetPosition = currentStatus
		# now okay
		return self.statusRemainedGoodSinceLastGetPosition

	def asynchronousMoveTo(self, time):
		return True

	def getStatus(self):
		out = getoutput(self.caget + " " + self.valveStatus)
		st = out.split()[1]
		if st == 'Open':
			ret = True
		else:
			ret = False
		return ret

	def getInterlock(self):
		out = getoutput(self.caget + " " + self.interlockStatus)
		st = out.split()[1]
		if st == 'OK':
			ret = True
		else:
			ret = False
		return ret

	def setState(self, state):
		out = getoutput(self.caput + " " + self.control + " " + state)

checkvalve = CheckValve('checkvalve')
