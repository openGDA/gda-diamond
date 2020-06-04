
from gda.device.scannable import ScannableMotionBase
from java.lang import Thread, Runnable
from gdascripts.pd.dummy_pds import DummyPD
import time

class BlockingTestScannable(ScannableMotionBase):
	def __init__(self, name):
		self.setName(name)
		self.setInputNames([name])
		self.setExtraNames([])
		self.setOutputFormat(["%5.5g"])
		self.currentposition = 10 # this template scannable represents a single number


	def getPosition(self):
		return self.currentposition

	def asynchronousMoveTo(self, new_position):
		self.currentposition = new_position
		print "BTS moving"
		time.sleep(new_position)
		print "BTS complete"

	def isBusy(self):
		return False


class MakeScannableThreaded(ScannableMotionBase):
	
	#
	# The constructor. 
	#
	def __init__(self, name, scn):
		self.name = name
		self.scn = scn

		self.setInputNames(scn.getInputNames())
		self.setExtraNames(scn.getExtraNames())
		self.setOutputFormat(scn.getOutputFormat())
		self.iambusy = 0 # flag to hold the status of the scannable
	
	def getPosition(self):
		return self.scn.getPosition()
	
	def asynchronousMoveTo(self, new_position):
		self.iambusy = 1
		newThread = moveScannableThread(self, new_position)
		t = Thread(newThread)
		t.start()
	
	def isBusy(self):
		return self.iambusy


class moveScannableThread(Runnable):
	
	def __init__(self, parent, target):
		self.parent = parent
		self.target = target
	
	def run(self):
		self.parent.scn.asynchronousMoveTo(self.target) # assume this is blocking
		self.parent.iambusy = False
