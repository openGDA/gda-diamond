import sys

from gda.factory import Finder
from gdascripts.parameters import beamline_parameters

from math import fabs

from framework import script_utilities

from org.slf4j import LoggerFactory

# Used by sub-classes:
from script_utilities import device, userlog, confirm # @UnusedImport
from gda.device import DeviceException # @UnusedImport

STATE_PREP = "PREP"
STATE_IDLE = "IDLE"
STATE_TRANSIT = "TRANSIT"
STATE_ERROR = "ERROR"

class StageControl(object):

	def __init__(self):
		self.state = STATE_PREP
		self.enabled = True
		self.params = beamline_parameters.Parameters()
		self.logger = LoggerFactory.getLogger(__name__) # @UndefinedVariable


	def blParameters(self):
		self.params = beamline_parameters.Parameters()
		return self.params


	def checkActiveHutch(self):
		doProceed = False
		reason ="Active Hutch check not initialised"
		if self.hutch_check:
			doProceed = self.hutch_check.actionApproved()
			reason = self.hutch_check.getDenialReason()
		return doProceed, reason


	def checkTolerance(self, scannable,target, tolerance):
		is_in_tolerance = False
		message=None
		try:
			if scannable:
				stats = (scannable.getName(), scannable.getPosition(), target, tolerance)
				is_in_tolerance = self.in_tolerance(target, stats[1], tolerance)
				
				if not is_in_tolerance:
					message = "scannable %s FAILED move tolerance: pos=%g : target %g +/- %g" % stats
			else:
				message = "WARNING: FAILED to check position tolerance"
				
			if message:
				self.notify(message, False)
		except:
			message = "FAILED to check position tolerance"
			self.raiseError(message)
			
		return is_in_tolerance


	def configure(self,controller=None):
		self.state = STATE_PREP
		try:
			self.procedure = "Configure Stage"
			self.stage = "initialise"
			self.controller = controller
			self.state = STATE_IDLE
			self.bus = Finder.find("gda_event_bus")
			self.hutch_check = None
			
		except:
			message = "FAILURE to configure StageControl"
			self.raiseError(message)
		
		return STATE_IDLE==self.state


	def getInstance(self):
		if not self.isConfigured():
			self.configure()
		return self


	def in_tolerance(self, target, actual, tolerance):
		return fabs(target - actual) <= tolerance


	def isConfigured(self):
		return not STATE_PREP==self.state


	def isEnabled(self):
		return self.enabled


	def isIdle(self):
		return STATE_IDLE==self.state


	def isReady(self):
		return self.enabled and not (STATE_PREP==self.state or STATE_ERROR==self.state)


	def notify(self, message, doWarning=False):
		script_utilities.update(self.controller, None, message, None, None, doWarning, logger_ref=self.logger)


	def raiseError(self, message):
		type_, exception, traceback = sys.exc_info()
		self.state = STATE_ERROR
		script_utilities.update(self.controller, message, type_, exception, traceback, True, logger_ref=self.logger)


	def reloadBeamlineParameters(self):
		self.params = beamline_parameters.Parameters()


	def report(self,procedure=None,stage=None):
		if procedure:
			self.procedure = procedure
		if stage:
			self.stage = stage
		if not self.procedure:
			self.procedure = ""
		if not self.stage:
			self.stage = "..."
		self.notify(self.procedure+" : "+self.stage)


	def reportComplete(self,success):
		self.notify("Complete Procedure: %s : success = %s" % (self.procedure, str(success)))


	def reset(self):
		self.state = STATE_PREP
		self.params = beamline_parameters.Parameters()


	def setEnabled(self, doEnable):
		self.enabled = doEnable


	def testTolerance(self, scannable, inpos, outpos, tolerance, numtests):
		for i in range(0, numtests):
			print ('test %d of %d: move %s between %7.5f and %7.5f' % (i+1, numtests, scannable.getName(), inpos, outpos))
			
			position, success = self.testMove(scannable, inpos, tolerance)
			print (': arrive %7.5f +/- %7.5f : %s' % (position, tolerance, str(success)))
			
			position, success = self.testMove(scannable, outpos, tolerance)
			print (': return %7.5f +/- %7.5f : %s' % (position, tolerance, str(success)))
			
			if not success:
				break


	def testMove(self, scannable, target, tolerance):
		scannable.moveTo(target)
		position = scannable.getPosition()
		success = self.checkTolerance(scannable, target, tolerance)
		return position, success

