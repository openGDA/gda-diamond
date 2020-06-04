from gda.device.scannable import ScannableMotionBase
from gda.epics import CAClient 
from gdascripts.pd.time_pds import tictoc
from time import sleep

class JenaPiezoChannel(ScannableMotionBase):
	""" This class is a template and can't be initialised or easily extended """
	""" This is an example constructor.  Make sure to call completeInitialisationt(). """

	def __init__(self, name, pvstring, distancePerStep=1, readSetPosition=0, delayAfterAskingToMove=0.2):
		self.name = name
		self.setInputNames([name])
		self.setOutputFormat(['%.3f'])
		self.setcli = CAClient(pvstring + ":DEMAND")
		self.poscli = CAClient(pvstring + ":RBV")
		self.busycli = CAClient(pvstring + ":BUSY")
		self.configure()
		self.lastSetPosition = 0 # stored as steps
		self.delayAfterAskingToMove=delayAfterAskingToMove
		self.readSetPosition = readSetPosition
		self.distancePerStep = distancePerStep

	def isBusy(self):
		return int(self.busycli.caget())	

	def getPosition(self):
		if self.readSetPosition:
			return self.lastSetPosition * self.distancePerStep
		else:
			return float(self.poscli.caget()) * self.distancePerStep

	def asynchronousMoveTo(self, rawposition):
		self.setcli.caput(rawposition/self.distancePerStep)
		self.lastSetPosition = rawposition/self.distancePerStep
		sleep(self.delayAfterAskingToMove)
	
	def configure(self):
		self.setcli.configure()
		self.poscli.configure()
		self.busycli.configure()

	def clearup(self):
		self.setcli.clearup()
		self.poscli.clearup()
		self.busycli.clearup()
