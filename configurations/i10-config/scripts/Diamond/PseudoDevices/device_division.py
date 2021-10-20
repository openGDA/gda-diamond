'''
This module provides a class definition for creating a detector that returns the division of detector1 over detector2
while continuously scanning energy.
Usage:
	>>>c17dbc16= DeviceDivisionClass("c17dbc16", mcsr17_g, mcsr16_g);;
	>>> cvscan egy_g 695 705 1 mcsr17_g 0.4 mcsr16_g c17dbc16

Created on 24 May 2018

@author: fy65
'''
#from gda.factory import Finder
#from scannable.continuous.deprecated.try_continuous_energy import mcsr16_g, mcsr17_g
from gda.device.detector.hardwaretriggerable import HardwareTriggerableDetectorBase
from gda.device.scannable import PositionCallableProvider
from org.slf4j import LoggerFactory
from threading import Timer
from gda.device import Detector

class DeviceDivisionClass(HardwareTriggerableDetectorBase, PositionCallableProvider):
	
	def __init__(self, name, det1, det2):
		'''constructor parameters:
				name:   Name of the new device
				det1: Name of the detector on X-axis (for example: "mcsr17_g")
				det2: Name of the detector on Y-axis (for example: "mcsr16_g")
		'''
		self.logger = LoggerFactory.getLogger("DeviceDivisionClass:%s" % name)
		self.setName(name);
		self.setInputNames([name]);
		#self.setLevel(8);
		self.s1values = []
		self.s2values = []		
		self.normalisedvalues = []
		self.refObj1 = det1
		self.refObj2 = det2
		
	def collectData(self):
		if self.verbose: self.logger.info('collectData()...')
		# Here we need to wait for the motor runup to complete when our Triggerable Detector is actually
		# a Software triggerable detector rather than a Hardware one. We do this by getting the runup time
		# from the motion controller.
		motion_controller = self.getHardwareTriggerProvider()
		runupdown_time = motion_controller.getTimeToVelocity()
		if self.verbose: self.logger.info('collectData()... motion_controller=%r, runupdown_time=%r' % (motion_controller, runupdown_time))
		if runupdown_time:
			self.delayed_collection_timer = Timer(motion_controller.getTimeToVelocity(), self._delayed_collectData)
			self.delayed_collection_timer.start()
			if self.verbose: self.logger.info('collectData()... delayed start...')
		else:
			if self.verbose: self.logger.info('collectData()... immediate start...')
		
		if self.verbose: self.logger.info('...collectData()')

	def _delayed_collectData(self):
		if self.verbose: self.logger.info('..._delayed_collectData()')

	def getStatus(self):
		return Detector.IDLE

	def readout(self):
		# read the last element collected
		raise Exception(self.name + "for use only in normal scan")

	def atScanLineStart(self):
		if self.verbose: self.logger.info('atScanLineStart()...')
		self.number_of_positions = 0
		if self.verbose: self.logger.info('...atScanLineStart()')

	def atScanLineEnd(self):
		if self.verbose: self.logger.info('...atScanLineEnd()')

	def getPositionCallable(self):
		if self.verbose: self.logger.info('getPositionCallable()... number_of_positions=%i' % self.number_of_positions)
		self.number_of_positions += 1
		self.s1values=list(self.refObj1.getPositionCallable())
		self.s2values=list(self.refObj2.getPositionCallable())
		self.normalisedvalues = self.elementWiseDivision(self.s1values, self.s2values);
		return self.normalisedvalues;

	def elementWiseDivision(self, x1=[], x2=[]):
		'''returns the element-wise division of the two array'''
		if len(x1)==0:
			print "detector %s returns no value" % (self.refObj1.getName())
		if len(x2)==0:
			print "detector %s returns no value" % (self.refObj2.getName())
			return []
		if len(x1)!=len(x2):
			print "The number of elements returned from 2 detectors are different"
			return []
		y=[float(a)/float(b) for a,b in zip(x1, x2)]
		return y;

	def createsOwnFiles(self):
		return False

	def getDescription(self):
		return ""

	def getDetectorID(self):
		return ""

	def getDetectorType(self):
		return ""

	def getDataDimensions(self):
		return (1,)


c17dbc16= DeviceDivisionClass("c17dbc16", mcsr17_g, mcsr16_g);  # @UndefinedVariable