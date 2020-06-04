from gda.device.scannable import ScannableMotionBase
from gda.epics import CAClient 
from gdascripts.pd.time_pds import tictoc
from time import sleep


class I04Scannable(ScannableMotionBase):

	def __init__(self, name, exposeUniblitzShutterObject):
		"""
		If given the counter timer will be used to time the exposure
		"""
		self.name = name
		self.setInputNames(['exposure', 'file'])
		self.setOutputFormat(['%.6f', '%s'])
		
		self.expuni = exposeUniblitzShutterObject
		self.last_actual_shutter_open_time = -9999
		self.lastFileName = ''
		
	def isBusy(self):
		return 0	# The asynchronousMoveTo method is blocking

	def getPosition(self):
		return [self.last_actual_shutter_open_time, self.lastFileName]

	def asynchronousMoveTo(self, expose):
		## 1. Start exposure ##
		print "=== Start exposure"
		sleep(.2)
		
		## 2. Open and close shutter ##
		self.expuni.asynchronousMoveTo(expose)
		self.last_actual_shutter_open_time = self.expuni.getPosition()
		
		## 3. End exposure ##
		sleep(.2)
		print "=== Stopping exposure"
		self.lastFileName = "blarghh.dat"
		print "Saving file: %s" % self.lastFileName