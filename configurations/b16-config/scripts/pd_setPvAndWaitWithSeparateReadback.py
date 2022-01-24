from gda.device.scannable import ScannableMotionBase
from gda.epics import CAClient 
from gdascripts.pd.time_pds import tictoc
from time import sleep

class SetPvAndWaitWithSeparateReadback(ScannableMotionBase):
	""" This class is a template and can't be initialised or easily extended """
	""" This is an example constructor.  Make sure to call completeInitialisationt(). """


	def __init__(self, name, pvset, pvread, delayAfterAskingToMove=0.2):
		self.name = name
		self.setInputNames([name])
		self.setOutputFormat(['%.3f'])
		self.setcli = CAClient(pvset)
		self.readcli = CAClient(pvread)
		self.configure()
		self.delayAfterAskingToMove=delayAfterAskingToMove

	def isBusy(self):
		return 0

	def getPosition(self):
		return float(self.readcli.caget())

	def asynchronousMoveTo(self, rawposition):
		self.setcli.caput(rawposition)
		sleep(self.delayAfterAskingToMove)

	def configure(self):
		self.setcli.configure()
		self.readcli.configure()

	def clearup(self):
		self.setcli.clearup()
		self.readcli.clearup()

