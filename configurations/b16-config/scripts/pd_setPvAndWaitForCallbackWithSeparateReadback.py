from gda.device.scannable import ScannableMotionBase
from gdascripts.utils import caget
from gdascripts.pd.time_pds import tictoc
from gda.epics import CAClient 
from time import sleep

class SetPvAndWaitForCallbackWithSeparateReadback(ScannableMotionBase):

	""" This is the constructor for the class. """
	def __init__(self, name, pvset, pvread, timeout):
		self.name = name
		self.cliset = CAClient(pvset)
		self.cliread = CAClient(pvread)
		self.timeout = timeout
		self.setInputNames([name])
		self.setOutputFormat(['%6.3f'])
		self.configure()
		
	def isBusy(self):
			return 0

	def getPosition(self):	
		return float(self.cliread.caget())

	def asynchronousMoveTo(self, value):
		self.cliset.caput(self.timeout, value)

	def configure(self):
		self.cliread.configure()
		self.cliset.configure()
		

class SetPvAndWaitForCallbackWithSeparateReadback2(SetPvAndWaitForCallbackWithSeparateReadback):
	# This is a quick cludge to get around the fact that if you command some
	# Peizo motors to move to where they are, the motor goes busy and never
	# returns, causing a timeout.
	
	def __init__(self, name, pvset, pvread, timeout, deadband):
		self.deadband=deadband
		SetPvAndWaitForCallbackWithSeparateReadback.__init__(self, name, pvset, pvread, timeout)

	def asynchronousMoveTo(self, value):
		pos=float(self.getPosition())
		if (value == pos):
			print "Position %f is too close to current position %f so " % \
				(value, pos) + "tweaking by %f first!" % self.deadband
			if (value > 0 ):
				SetPvAndWaitForCallbackWithSeparateReadback.asynchronousMoveTo(self, value-self.deadband)
			else:
				SetPvAndWaitForCallbackWithSeparateReadback.asynchronousMoveTo(self, value+self.deadband)
			sleep(0.1)
			
		SetPvAndWaitForCallbackWithSeparateReadback.asynchronousMoveTo(self, value)