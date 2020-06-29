from gda.factory import Finder
from gda.device.scannable import ScannableMotionBase
from gda.scan import ConcurrentScan
import math

#class IPositionCompareableScannable(ScannableMotionBase):
#	'''
#	'''
#	pass
#
#	# Define Interface Here

class XpsPositionCompareableScannable(ScannableMotionBase):
	"""
	"""

	def __init__(self, dofAdapter):
		self.dofAdapter = dofAdapter
		self.xpsmotor=Finder.find(dofAdapter.getDofname() + '_motor') # I16 specific hack
		self.normalSpeed = self.xpsmotor.getSpeed()
		self.offset = dofAdapter.getOE().getOE().getPositionOffset(dofAdapter.getName()).amount
		self.dummypos = dofAdapter.getPosition()
		
		self.setInputNames([dofAdapter.getName()])
###
	# This wrapper will be scanned over in order to fudge the data into an SRS
	# file using the same mechanism as other scans.
	def asynchronousMoveTo(self, pos):
		self.dummypos = pos
		
	def getPosition(self):
		# assume that when the scan-for-writing scan is run, it is called with the correct
		# parameters.
		return self.dummypos
	
	def isBusy(self):
		return False
###
	def preparePositionCompareAndSetSpeed(self, start, stop, stepSize, stepTime):
		"""
		"""
		print "** %s.setPositionCompare(start=%f, stop=%f, step=%f)" % (self.xpsmotor.getName(), start-self.offset, stop-self.offset, stepSize)
		self.disablePositionCompare() # just in case
		self.xpsmotor.setPositionCompare(start-self.offset, stop-self.offset, stepSize)
		speed = float(stepSize)/stepTime
		self.setSpeed(speed)

	def setSpeed(self, speed):
		print "** %s.getSpeed() = %f" % (self.xpsmotor.getName(), self.xpsmotor.getSpeed())
		print "** %s.setSpeed(%f)" %(self.xpsmotor.getName(), speed)
		self.xpsmotor.setSpeed(speed)
		
	def moveTo(self, pos):
		print "** %s.moveTo(%f)" %(self.dofAdapter.getName(), pos)
		self.dofAdapter.moveTo(pos)
		
	def setSpeedToNormal(self):
		self.setSpeed(self.normalSpeed)
	
	def enablePositionCompare(self):
		print "** %s.enablePositionerCompare()" %(self.xpsmotor.getName())
		self.xpsmotor.enablePositionerCompare()
		
	def disablePositionCompare(self):
		print "** %s.disablePositionerCompare()" %(self.xpsmotor.getName())
		self.xpsmotor.disablePositionerCompare()

			
class Cvscan:
	"""
	"""
	
	def __init__(self, rampUpDownDistance = 0):
		self.rampUpDownDistance = rampUpDownDistance
	
	def __call__(self, *args):
		"""
		cvscan dofAdapter start stop step multiChannelScaler time
		"""
		# 1. Perform the actual movements and collect the data
		dofAdapter, start, stop, stepSize, wmcs, stepTime = args
		self.dofAdapter = dofAdapter
		self.pcmotor = XpsPositionCompareableScannable(dofAdapter)
	
		wmcs.prepareForCollection()
		wmcs.collectData()
		self.performMove(start, stop, stepSize, stepTime)
		wmcs.stop()
		
		# 2. Run a fake scan to get the results into a file
		no_points = int(math.floor( abs(float(stop) - start)/stepSize)) + 1
		wmcs.prepareResults(no_points)
		fakescan = ConcurrentScan([self.pcmotor, start, stop, stepSize, wmcs])
		fakescan.runScan()

	def performMove(self, start, stop,stepSize, stepTime):
		# Calculate rampup/down positions
		movingPositiveDirection = (stop-start) > 0
		if movingPositiveDirection:
			rampupFrom = start - self.rampUpDownDistance
			rampdownTo = stop + self.rampUpDownDistance
		else:
			rampupFrom = start + self.rampUpDownDistance
			rampdownTo = stop - self.rampUpDownDistance
		

		# Move to start (including rampup)
		print "Moving to rampup position..."
		self.pcmotor.disablePositionCompare()
		self.pcmotor.setSpeedToNormal()
		self.pcmotor.moveTo(rampupFrom)
		
		# Configure
		print "Configuring position compare..."
		self.pcmotor.preparePositionCompareAndSetSpeed(start, stop, stepSize, stepTime)
		self.pcmotor.enablePositionCompare()
		
		# Move to end (including rampdown)
		print "Performing move..."
		self.pcmotor.moveTo(rampdownTo)
		self.pcmotor.disablePositionCompare()
		self.pcmotor.setSpeedToNormal()
		print "Move complete."
