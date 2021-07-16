from gda.device.scannable import ScannableMotionBase
from gda.epics import CAClient 
from gdascripts.pd.time_pds import tictoc
from time import sleep


class CounterTimerForGatedMeasurement:
	def __init__(self, rootPv): #BL16B-EA-DET-01
		self.CONT = CAClient(rootPv+'.CONT')
		self.CNT = CAClient(rootPv+'.CNT')
		self.S1 = CAClient(rootPv+'.S1')
		
	def configure(self):
		self.CONT.configure()
		self.CNT.configure()
		self.S1.configure()
	
	def makeReady(self):
		self.CONT.caput('AutoCount')
		self.CNT.caput('0')
		self.CNT.caput('1')
		sleep(.1)
		
	def readS1Count(self):
		return int(float(self.S1.caget()))


class ExposeUniblitzShutter(ScannableMotionBase):

	def __init__(self, name, rootPv, counterTimerPv = None):
		"""
		If given the counter timer will be used to time the exposure. Gate control
		line 3 with the sync output from the shutter. This outpus is 1kohm TTL.
		"""
		self.name = name
		self.setInputNames(['exposure'])
		self.setOutputFormat(['%.6f'])
		self.timeout = 10 #s
		
		if counterTimerPv:
			self.counterTimer = CounterTimerForGatedMeasurement(counterTimerPv)
		else:
			self.counterTimer = None
		
		self.PROC1 = CAClient(rootPv + ":SEQ.PROC")
		self.DLY2  = CAClient(rootPv + ":SEQ.DLY2")
		self.SHUTTER=CAClient(rootPv + ":SHUTTER")
		
		self.configure()
		self.lastExposureTime = -9999

	def configure(self):
		self.PROC1.configure()
		self.DLY2.configure()
		self.SHUTTER.configure()
		if self.counterTimer:
			self.counterTimer.configure()

	def isBusy(self):
		return 0	# The asynchronousMoveTo method is blocking

	def getPosition(self):
		if self.counterTimer:
			return self.readTimeFromCounterTimer()
		else:
			return self.lastExposureTime

	def asynchronousMoveTo(self, expose):
		self.close() # make sure it starts closed
		sleep(.2)
		if self.counterTimer:
			self.readyCounterTimer()
		self.setExposureTime(expose)
		self.timeout = expose + 10
		self.trigger() # waits for completion
		self.lastExposureTime = expose
###
	def open(self):
		self.SHUTTER.caput('OPEN')
	
	def close(self):
		self.SHUTTER.caput('CLOSE')
		
	def setExposureTime(self, expose):
		self.DLY2.caput(expose)
		
	def trigger(self):
		# Waits for exposure to complete
		self.PROC1.caput(self.timeout, 1)
		
	def readyCounterTimer(self):
		self.counterTimer.makeReady()
	
	def readTimeFromCounterTimer(self):
		return self.counterTimer.readS1Count()/50e6
