from gda.device.scannable import ScannableMotionBase
from gdascripts.utils import caget
from gdascripts.pd.time_pds import tictoc
from gda.epics import CAClient 

class SetPvAndWaitForCallback(ScannableMotionBase):

	""" This is the constructor for the class. """
	def __init__(self, name, pvstring, timeout):
		self.name = name
		self.cli = CAClient(pvstring)
		self.timeout = timeout
		self.setInputNames([name])
		self.setOutputFormat(['%.9f'])
		
	# Configure the CA client's channel at the start of a scan
	def atScanStart(self):
		if not(self.cli.isConfigured()):
			self.cli.configure()

	def isBusy(self):
			return 0

	def getPosition(self):	
		if self.cli.isConfigured():
			return float(self.cli.caget())
		else:
			self.cli.configure()
			return float(self.cli.caget())
			self.cli.clearup()

	def asynchronousMoveTo(self, value):
		if self.cli.isConfigured():		
			self.cli.caput(self.timeout, value)
		else:
			self.cli.configure()
			self.cli.caput(self.timeout, value)
			self.cli.clearup()

	#Close the CA EPICS channel at the end of a scan:
	def atScanEnd(self):
		if self.cli.isConfigured():
			self.cli.clearup()

