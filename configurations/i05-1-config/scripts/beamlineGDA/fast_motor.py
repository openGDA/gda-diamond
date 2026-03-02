from gda.device.scannable import ScannableMotor, PositionConvertorFunctions
from time import sleep
import logging
from java.lang import Double
logger = logging.getLogger('__main__')

class FastScannableMotor(ScannableMotor):
	"""
	Scannable Motor which doesn't wait for the motor to be in position
	and returns demand value as readback.
	"""
	def __init__(self, name, motor):
		self.setName(name)
		self.setInputNames([name])
		self.setOutputFormat(["%5.5g"])
		self.setInitialUserUnits("micron")
		self.setHardwareUnitString("mm")
		self.setLowerGdaLimits(-7000)
		self.setUpperGdaLimits(6000)
		self.logger = logger.getChild(self.__class__.__name__)
		self.motor = motor
		self.lastDemandedInternalPosition = self.motor.getPosition()
		self.configure()

	def isBusy(self):
		return False

	def waitWhileBusy(self):
		"""
		Don't wait for motor to arrive
		"""
		return

	def getPosition(self):
		return self.internalToExternal(self.lastDemandedInternalPosition)

	def rawAsynchronousMoveTo(self, newInternalPosition):
		self.logger.debug("Fast motor %s has got command to move to new internal position %f"%(self.name, newInternalPosition))
		self.internalDoublePosition = PositionConvertorFunctions.toDouble(newInternalPosition)
		self.motor.moveTo(self.internalDoublePosition);
		self.lastDemandedInternalPosition = self.internalDoublePosition;
