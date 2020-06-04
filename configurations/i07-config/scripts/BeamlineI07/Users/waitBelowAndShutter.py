from gda.device.scannable import ScannableMotionBase
from gda.jython import JythonServerFacade
from gda.jython.JythonStatus import RUNNING

from time import asctime, sleep
from datetime import time


class WaitBelowAndShutterMonitorOnly(ScannableMotionBase):
	'''
	Can be configured with any monitor-like scannable and a minimum threshold.
	This scannable\'s getPosition method will not return until the monitor-like scannables
	return a number above the threshold and the port shutter is open.
	
	When it does return getPosition returns 1 if okay or zero to indicate that during the last point a
	beamdump occured.
	
	getPosition reports status changes and time.
	
	'''
	def __init__(self, name, scannableToMonitor, minimumThreshold, shutterScannable, shutterValue, secondsBetweenChecks, secondsToWaitAfterBeamBackUp, idgap=0):
		self.scannableToMonitor = scannableToMonitor
		self.minimumThreshold = minimumThreshold
		self.shutterScannable = shutterScannable
		self.shutterValue = shutterValue
		self.secondsBetweenChecks = secondsBetweenChecks
		self.secondsToWaitAfterBeamBackUp = secondsToWaitAfterBeamBackUp
		self.idgap = idgap
		
		self.setName(name);
		self.setInputNames([])
		self.setExtraNames(['beamok']);

		self.Units=[]
		self.setOutputFormat(['%.0f'])
		self.setLevel(6)
		
		self.lastStatus = True # Good

	def atScanStart(self):
		global safegap
		print '=== Beam checking enabled'
		self.statusRemainedGoodSinceLastGetPosition = True
		try:
			self.gap = self.idgap.getPosition()
			print '=== idgap at start of scan: '+str(self.gap)+' mm'
			if self.gap >= 6.99 and self.gap <= 7.01:
				print '\n\n*** WARNING: gap appears to be 7mm so may not have been restored after beam loss'
				try:
					if safegap >= 5 and safegap <= 12:
						print '*** safegap is set to '+str(safegap)
						print "*** Restoring idgap to "+str(safegap)+"mm"
						self.gap = safegap						
						self.idgap.asynchronousMoveTo(safegap)
						while self.idgap.isBusy():
							sleep(0.2)
				except:
					print '*** no safegap set so can not restore previous gap'
					self.gap = -1
				print '\n\n'
		except:
			self.gap = -1
			print '=== Could not read idgap at start of scan'
			try:
				if safegap >= 5 and safegap <= 12:
					print '*** Using safegap value of '+str(safegap)+'mm as desired gap setting'
					self.gap = safegap
			except:
				self.gap = -1

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
				print "WaitBelowAndShutter not holding readback as no scan is running"
			self.statusRemainedGoodSinceLastGetPosition = currentStatus
		
		return self.statusRemainedGoodSinceLastGetPosition

	def getStatus(self):
		# return true if there's an error to avoid crashing scan
		try:
			val = self.scannableToMonitor.getPosition()
			if type(val) in (type(()), type([])):
				val = val[0]
			val2 = self.shutterScannable.getPosition()
			if type(val2) in (type(()), type([])):
				val2 = val2[0]			
			status =  ((val >= self.minimumThreshold) and (val2 == self.shutterValue))
		except:
			status=True
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
			print "*** Beam back up at: " + asctime() + ". Resuming scan in " + str(self.secondsToWaitAfterBeamBackUp) + "s..."
			self.lastStatus = True
			sleep(self.secondsToWaitAfterBeamBackUp)
			try:
				if self.gap != -1 and self.idgap.getPosition() != self.gap:
					print "*** Restoring idgap to "+str(self.gap)+" mm"
					self.idgap.asynchronousMoveTo(self.gap)
					while self.idgap.isBusy():
						sleep(0.2)
			except:
				print '*** Error while attempting to restore idgap'
			print "*** " + asctime() + ". Resuming scan now."
		if not status and not self.lastStatus:
			pass # beam still down
		if not status and self.lastStatus:
			print "*** Beam down at: " + asctime() + ". Pausing scan..."
			self.lastStatus = False



class WaitBelowAndShutter(WaitBelowAndShutterMonitorOnly):

	'''
	For any scannable the first number returned will pause a scan by halting the 
	getPosition method.
	
	getPosition returns 1 if okay or zero to indicate that during the last point a
	beamdump occured.
	
	getPosition reports status changes and time.
	
	In this DEVELOPMENT version if a time is specified in a scan command, the scannable
	to monitor will be triggered; this is useful if a countertimer is used to monitor
	some physical parameter.
	This will start the thing counting in the synchronousMoveTo method, and if needbe start
	it counting again before reading it every secondsBetweenChecks.
	
	'''

	# overide
	def __init__(self, name, scannableToMonitor, minimumThreshold, shutterScannable, shutterValue, secondsBetweenChecks, secondsToWaitAfterBeamBackUp, idgap=0):
		self.countTime = None
		# Call super class' constructor
		WaitBelowAndShutterMonitorOnly.__init__( self, name, scannableToMonitor, minimumThreshold, shutterScannable, shutterValue, secondsBetweenChecks, secondsToWaitAfterBeamBackUp, idgap )

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
				print "WaitBelowAndShutter not holding readback as no scan is running"
			self.statusRemainedGoodSinceLastGetPosition = currentStatus
		# now okay
		return self.statusRemainedGoodSinceLastGetPosition

