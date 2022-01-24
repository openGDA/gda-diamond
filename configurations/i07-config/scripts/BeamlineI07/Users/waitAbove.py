from gda.device.scannable import ScannableMotionBase
from gda.jython import JythonServerFacade
from gda.jython.JythonStatus import RUNNING

from time import asctime, sleep
from datetime import time


class WaitAboveMonitorOnly(ScannableMotionBase):
	'''
	Can be configured with any any monitor-like scannable and a maximum threshold.
	This scannable's getPosition method will not return until the monitor-like scannable
	returns a number below the lower threshold.
	
	When it does return getPosition returns 1 if okay or zero to indicate that during the last point an
	exceeding of the threshold  occured.
	
	getPosition reports status changes and time.
	
	'''
	def __init__(self, name, scannableToMonitor, maximumThreshold, maximumToResume, secondsBetweenChecks, secondsToWaitAfterOK):
		self.scannableToMonitor = scannableToMonitor
		self.maximumThreshold = maximumThreshold
		self.maximumToResume = maximumToResume		
		self.secondsBetweenChecks = secondsBetweenChecks
		self.secondsToWaitAfterOK = secondsToWaitAfterOK
		
		self.setName(name);
		self.Units=[]
		self.setOutputFormat(['%.0f'])
		self.setLevel(6)
		self.setInputNames(['dcmok'])
		
		self.lastStatus = True # Good

	def atScanStart(self):
		print '=== Threshold checking enabled: '+self.scannableToMonitor.getName()+' must not exceed '+str(self.maximumThreshold)
		self.statusRemainedGoodSinceLastGetPosition = True

	def isBusy(self):
		'''This can't be used as isBusy is not checked unless the scannable
		is 'moved' by passing in a number'''
		return False
	
	def getPosition(self):
		'''If scan is running then pauses until status is okay and returning False
		if the scan was not okay. If scan is not running, return the current state
		and print a warning that the scan is not being paused.'''
		
		self.statusRemainedGoodSinceLastGetPosition = 1.0
		
		if JythonServerFacade.getInstance().getScanStatus()==RUNNING:
			# loop until okay
			while not self.getStatusAndReport():  
				# not okay
				self.statusRemainedGoodSinceLastGetPosition = 0.0
				sleep(self.secondsBetweenChecks)	
			# now okay
		else: # scan not running
			currentStatus = self.getStatus()
			if not currentStatus: # bad
				print "WaitAbove not holding readback as no scan is running"
			self.statusRemainedGoodSinceLastGetPosition = currentStatus
		
		return self.statusRemainedGoodSinceLastGetPosition

	def getStatus(self):
		val = self.scannableToMonitor.getPosition()
		if type(val) in (type(()), type([])):
			val = val[0]
		status =  ((self.lastStatus and (val <= self.maximumThreshold)) or ((not self.lastStatus) and (val <= self.maximumToResume)))
		return status

	def getStatusAndReport(self):
		## Check current status, reports and returns it
		status = self.getStatus()
		self.reportStatusChange(status)
		return status
		
	def reportStatusChange(self,status):
		## check for status change to provide feedback:
		if status and self.lastStatus:
			pass # still okay
		if status and not self.lastStatus:
			print "*** Value below threshold at: " + asctime() + ". Resuming scan in " + str(self.secondsToWaitAfterOK) + "s..."
			self.lastStatus = True
			sleep(self.secondsToWaitAfterOK)
			print "*** " + asctime() + ". Resuming scan now."
		if not status and not self.lastStatus:
			pass # beam still down
		if not status and self.lastStatus:
			print "*** Value above threshold: " + asctime() + ". Pausing scan..."
			self.lastStatus = False



class WaitAbove(WaitAboveMonitorOnly):

	'''
	For any scannable the first number returned will pause a scan by halting the 
	getPosition method.
	
	getPosition returns 1 if okay or zero to indicate that during the last point an
	exceeding of the threshold occured.
	
	getPosition reports status changes and time.
	
	In this DEVELOPMENT version if a time is specified in a scan command, the scannable
	to monitor will be triggered; this is useful if a countertimer is used to monitor
	some physical parameter.
	This will start the thing counting in the synchronousMoveTo method, and if needbe start
	it counting again before reading it every secondsBetweenChecks.
	
	'''

	# overide
	def __init__(self, name, scannableToMonitor, maximumThreshold, maximumToResume, secondsBetweenChecks, secondsToWaitAfterOK):
		self.countTime = None
		# Call super class' constructor
		WaitAboveMonitorOnly.__init__( self, name, scannableToMonitor, maximumThreshold, maximumToResume, secondsBetweenChecks, secondsToWaitAfterOK )

	def asynchronousMoveTo(self, time):
		# Store the time for the case that the threshold is low and a new count must be made.
		self.countTime = time
		if time !=None:
			self.__triggerCount(time)
	
	def __triggerCount(self, time):
		self.scannableToMonitor.asynchronousMoveTo(time)

	def __waitForCountToComplete(self):
		while self.scannableToMonitor.isBusy():
			sleep(.1)
	
	def isBusy(self):
		return self.scannableToMonitor.isBusy()
	
	def getPosition(self):
		'''Pauses until status is okay'''
		self.statusRemainedGoodSinceLastGetPosition = 1.0
		# loop until okay (note that the count will have been triggered if count time was given)
		if JythonServerFacade.getInstance().getScanStatus()==RUNNING:
			while not self.getStatusAndReport():  
				# not okay
				self.statusRemainedGoodSinceLastGetPosition = 0.0
				sleep(self.secondsBetweenChecks)
				if self.countTime !=None:
					self.__triggerCount(self.countTime)#
					self.__waitForCountToComplete()
		else: # scan not running
			currentStatus = self.getStatus()
			if not currentStatus: # bad
				print "WaitAbove not holding readback as no scan is running"
			self.statusRemainedGoodSinceLastGetPosition = currentStatus
		# now okay
		return self.statusRemainedGoodSinceLastGetPosition

