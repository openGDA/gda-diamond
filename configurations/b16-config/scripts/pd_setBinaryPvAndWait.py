from gda.device.scannable import ScannableMotionBase
from gda.epics import CAClient 
from gdascripts.pd.time_pds import tictoc
from time import sleep

class SetBinaryPvAndWait(ScannableMotionBase):
	""" This class is a template and can't be initialised or easily extended """
	""" This is an example constructor.  Make sure to call completeInitialisationt(). """

	def __init__(self, name, pvstring, delayAfterAskingToMove=0.2, flip=False):
		self.name = name
		self.setInputNames([name])
		self.setOutputFormat(['%d'])
		self.setcli = CAClient(pvstring)
		self.configure()
		self.delayAfterAskingToMove=delayAfterAskingToMove
		self.flip = flip


	def isBusy(self):
		return 0

	def getPosition(self):
		val = self.setcli.caget()=='1'
		if self.flip:
			val = not val
		return val

	def asynchronousMoveTo(self, rawposition):
		if self.flip:
			rawposition = not rawposition
		self.setcli.caput(rawposition)
		sleep(self.delayAfterAskingToMove)

	def configure(self):
		self.setcli.configure()

	def clearup(self):
		self.setcli.clearup()

