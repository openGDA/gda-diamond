from gda.device.scannable import ScannableMotionBase
from gdascripts.utils import caget
from gdascripts.pd.time_pds import tictoc
from gda.epics import CAClient 

class ReadManyPVs(ScannableMotionBase):

	""" This is the constructor for the class. """
	def __init__(self, name, basepvstring, suffixlist):
		self.name = name

		self.cli = []
		extraNames=[]
		for suffix in suffixlist:
			self.cli += [CAClient(basepvstring+suffix)]
			extraNames += [suffix]

		self.setInputNames([])
		self.setExtraNames(extraNames)
		self.setOutputFormat(['%.9f']*len(self.cli))

	# Configure the CA client's channel at the start of a scan
	def atScanStart(self):
		for aCli in self.cli:
			if not(aCli.isConfigured()):
				aCli.configure()

	def isBusy(self):
		return 0

	def getPosition(self):	
		# If the CA client has already had a channel configured by atStart()
		toReturn = []
		for aCli in self.cli:
			if aCli.isConfigured():
				toReturn += [ float(aCli.caget())]
				# ...and leave the channel open for the following points in scan
			else:
				# No channel open (atStart is not called with a single pos command)
				# Open a channel for this request only, and then close it again
				aCli.configure()
				toReturn+= [ float(aCli.caget()) ]
				aCli.clearup()
		return toReturn

	def asynchronousMoveTo(self,waittime=0):
		pass


	#Close the CA EPICS channel at the end of a scan:
	def atScanEnd(self):
		for aCli in self.cli:
			if aCli.isConfigured():
				aCli.clearup()

