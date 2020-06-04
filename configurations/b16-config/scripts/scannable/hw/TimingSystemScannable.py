from gda.device.scannable import ScannableMotionBase
from gda.epics import CAClient 
from gdascripts.pd.time_pds import tictoc
from time import sleep
from gdascripts.scannable.epics.PvManager import PvManager

def caput(pvstring, val):
	cac = CAClient(pvstring)
	cac.configure()
	cac.caput(val)
	cac.clearup()

def caget(pvstring):
	cac = CAClient(pvstring)
	cac.configure()
	val = cac.caget()
	cac.clearup()	
	return val


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

class TimingSystemScannable(ScannableMotionBase):
	"""
	Controls a PMC-EVR often used at Diamond for TopUp Gating Control 
	"""
	def __init__(self, name, binaryOutPvString, timingSystemPvBase, counterTimerPvBase = None):
		self.binaryOutPvString = binaryOutPvString
		self.timingSystemPvBase = timingSystemPvBase
		
		self.name = name
		self.setInputNames(['t'])
		self.setOutputFormat(['%2.7f'])
		self.setLevel(9)		
		self.timer=tictoc()
		self.waitfortime=0
		self.currenttime=0
		
		if counterTimerPvBase:
			self.counterTimer = CounterTimerForGatedMeasurement(counterTimerPvBase)
		else:
			self.counterTimer = None
		
		self.configure()


	def configure(self):
		
		self.boCA = CAClient(self.binaryOutPvString)
		self.boCA.configure()
		self.boCA.caput('off')
		
		self.widthCA = CAClient(self.timingSystemPvBase + ':FRONT-WIDTH:SET')
		self.widthCA.configure()
		
		caput(self.timingSystemPvBase + ':SELECT-FPS2', 'External')
		caput(self.timingSystemPvBase + ':FRONT-ENABLE:SET', 'Enabled')
		caput(self.timingSystemPvBase + ':FRONT-DELAY:SET', 0)
		caput(self.timingSystemPvBase + ':FRONT-POLARITY:SET', 'Normal')
		
		self.minwidth = float(caget(self.timingSystemPvBase + ':FRONT-WIDTH:SET.DRVL'))
		self.maxwidth = float(caget(self.timingSystemPvBase + ':FRONT-WIDTH:SET.DRVH'))
		
		
		if self.counterTimer:
			self.counterTimer.configure()
		
	def asynchronousMoveTo(self,width):
		if self.counterTimer:
			self.readyCounterTimer()
		self.setWidth(width)
		self.currenttime=self.timer()
		self.waitfortime=self.currenttime+width+.1 # add an extra .1s for overhead/safety
		self.trigger()
	
	def setWidth(self, width):
		if (width>self.maxwidth) or (width<self.minwidth):
			raise ValueError("Could not set width to %.10fs. The PMC-EVR currently only accepts widths between %.10fs and %f to 1s"%(width, self.minwidth, self.maxwidth))
		self.widthCA.caput(width)
	
	def trigger(self):
		self.boCA.caput('off')
		self.boCA.caput('on')
		self.boCA.caput('off')
		
	def isBusy(self):
		if self.timer()<self.waitfortime:
			return 1
		else:
			return 0

	def getPosition(self):
		if self.counterTimer:
			return self.readTimeFromCounterTimer()
		else:
			return self.widthCA.caget()
		
	def readyCounterTimer(self):
		self.counterTimer.makeReady()
	
	def readTimeFromCounterTimer(self):
		return self.counterTimer.readS1Count()/50e6


