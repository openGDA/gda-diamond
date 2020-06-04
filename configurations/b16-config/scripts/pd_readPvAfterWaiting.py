from gda.device.scannable import ScannableMotionBase
from gdascripts.utils import caget
from gdascripts.pd.time_pds import tictoc
from gda.epics import CAClient 

class ReadPvAfterWaiting(ScannableMotionBase):

	""" This is the constructor for the class. """
	def __init__(self, name, pvstring):
		self.name = name
		self.cli = CAClient(pvstring)

		self.setInputNames([name])
		self.setOutputFormat(['%.9f'])
		self.timer=tictoc()
		self.waitfortime=0
		self.currenttime=0

	# Configure the CA client's channel at the start of a scan
	def atScanStart(self):
		if not(self.cli.isConfigured()):
			self.cli.configure()

	def isBusy(self):
		if self.timer()<self.waitfortime:
			return 1
		else:
			return 0

	def getPosition(self):	
		# If the CA client has already had a channel configured by atStart()
		if self.cli.isConfigured():
			return float(self.cli.caget())
			# ...and leave the channel open for the following points in scan
		else:
			# No channel open (atStart is not called with a single pos command)
			# Open a channel for this request only, and then close it again
			self.cli.configure()
			return float(self.cli.caget())
			self.cli.clearup()

	def asynchronousMoveTo(self,waittime=0):
		self.currenttime=self.timer()
		self.waitfortime=self.currenttime+waittime


	#Close the CA EPICS channel at the end of a scan:
	def atScanEnd(self):
		if self.cli.isConfigured():
			self.cli.clearup()

