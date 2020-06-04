from gda.epics import CAClient 
from gdascripts.pd.time_pds import tictoc
from time import sleep
import time
import pd_toggleBinaryPvAndWait;reload(pd_toggleBinaryPvAndWait)

class ToggleBinaryPvAndWaitFancy(pd_toggleBinaryPvAndWait.ToggleBinaryPvAndWait):
	"""
	Similar to ToggleBinaryPvAndWait this is useful for triggering detectors which
	have been setup to record images on hardware triggers. In this version the 
	exposure and readout times are specified seperately, allowing motors to be
	moved while the detector is readout during a scan.
	
	Call with two inputs: exposure % readout. For example:
	
		scan x 1 10 1 toggler [2, .5]

	will expose for 2 seconds and make sure that the detector gets .5s to readout
	before again being triggered.
	
	Detailed operation:
	
	When first asked to expose, the device toggles the binary pulse as before. It
	returns busy until the exposure time has passed. When asked again to expose
	it will wait if necesary before sending the next trigger to ensure that readout-time
	seconds have elapsed since the last exposure completed.
	
	
	"""
	def __init__(self, name, pvstring, normalLevel=True):
		self.name = name
		self.cli = CAClient(pvstring)
		self.setInputNames(['exposure','readout'])
		self.setOutputFormat(['%5.5f','%5.5f'])
		self.setLevel(9)		
		self.timer=tictoc()
		self.waitfortime=0
		self.currenttime=0
		self.cli.configure()
		self.normalLevel = normalLevel
		self.setNormal()
		self.lastExposureTime=0
		self.lastReadoutTime=0
		self.debug = False


	def isBusy(self):
		return 0
#		if self.timer()<self.waitfortime:
#			return 1
#		else:
#			return 0


	def getPosition(self):
		return (self.lastExposureTime,self.lastReadoutTime)

	def isReadingOut(self):
		if self.timer()<self.waitfortime:
			return 1
		else:
			return 0

	def waitWhileReadingOut(self):
		while 1:
			if not self.isReadingOut():
				break
			sleep(0.05)

	def asynchronousMoveTo(self, pos):
		if self.debug:
			print "**%9.2f: asynchronousMoveTo(%s)" % (time.time(), str(pos))
		(exposureTime, readoutTime) = pos
		self.lastExposureTime = exposureTime
		self.lastReadoutTime = readoutTime
		
		self.waitWhileReadingOut()
		self.currenttime=self.timer()
		self.waitfortime=self.currenttime+exposureTime+readoutTime
		if self.debug:
			print "**%9.2f: Starting exposure" % time.time()
		self.trigger(exposure_time)
		if self.debug:
			print "**%9.2f: Exposure complete" % time.time()
