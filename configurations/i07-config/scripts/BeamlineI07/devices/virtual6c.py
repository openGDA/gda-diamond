from gda.device.scannable import ScannableBase

from math import sin
from math import asin
from math import cos
from math import atan
from math import radians
from math import degrees

# These functions outlined at:
# https://confluence.diamond.ac.uk/x/go1KBg
# Here all the parameters and return values are in radians

def horizontal_virtual_gamma(alpha, gamma, delta):
	return asin((sin(gamma) * cos(delta)) / cos(horizontal_virtual_delta(alpha, gamma, delta)))

def horizontal_virtual_delta(alpha, gamma, delta):
	return asin(sin(delta) * cos(alpha) - cos(gamma) * cos(delta) * sin(alpha))

def horizontal_real_gamma(alpha, gamma_virt, delta_virt):
	return atan((sin(gamma_virt) * cos(delta_virt)) / (cos(gamma_virt) * cos(delta_virt) * cos(alpha) - sin(delta_virt) * sin(alpha)))

def horizontal_real_delta(alpha, gamma_virt, delta_virt):
	return asin(sin(delta_virt) * cos(alpha) + cos(gamma_virt) * cos(delta_virt) * sin(alpha))
	
def vertical_virtual_gamma(alpha, gamma, delta):
	return asin(sin(gamma - alpha) * cos(delta))

def vertical_virtual_delta(alpha, gamma, delta):
	return asin(sin(delta) / cos(vertical_virtual_gamma(alpha, gamma, delta)))

def vertical_real_gamma(alpha, gamma_virt, delta_virt):
	return atan((cos(delta_virt) * cos(gamma_virt) * sin(alpha) + sin(gamma_virt) * cos(alpha)) / (cos(delta_virt) * cos(gamma_virt) * cos(alpha) - sin(gamma_virt) * sin(alpha)))

def vertical_real_delta(alpha, gamma_virt, delta_virt):
	return asin(sin(delta_virt) * cos(gamma_virt + alpha))


class Virtual6CircleCompositeMotor(ScannableBase):

# Two different axes can be created 'virtual gamma' or 'virtual delta' , these are prepended by the geometry

	def __init__(self, name, realAlpha, realGamma, realDelta, virtualMotorName):

		self.setName(name)
		self.setInputNames([name])
		#self.setOutputFormat(["%5.5g"])

		# Note we never move realAlpha, just use it to calculate positions
		self.realAlpha = realAlpha
		self.realGamma = realGamma
		self.realDelta = realDelta
		self.virtualMotorName = virtualMotorName
		if self.virtualMotorName == 'horizontalVirtualGamma':
			self.getThisVirtualMotorPosition = horizontal_virtual_gamma
			self.getOtherVirtualMotorPosition = horizontal_virtual_delta
			self.calcRealGammaMoveTo = horizontal_real_gamma
			self.calcRealDeltaMoveTo = horizontal_real_delta
		elif self.virtualMotorName == 'horizontalVirtualDelta':
			self.getThisVirtualMotorPosition = horizontal_virtual_delta
			self.getOtherVirtualMotorPosition = horizontal_virtual_gamma
			self.calcRealGammaMoveTo = horizontal_real_gamma
			self.calcRealDeltaMoveTo = horizontal_real_delta
		elif self.virtualMotorName == 'verticalVirtualGamma':
			self.getThisVirtualMotorPosition = vertical_virtual_gamma
			self.getOtherVirtualMotorPosition = vertical_virtual_delta
			self.calcRealGammaMoveTo = vertical_real_gamma
			self.calcRealDeltaMoveTo = vertical_real_delta
		elif self.virtualMotorName == 'verticalVirtualDelta':
			self.getThisVirtualMotorPosition = vertical_virtual_delta
			self.getOtherVirtualMotorPosition = vertical_virtual_gamma
			self.calcRealGammaMoveTo = vertical_real_gamma
			self.calcRealDeltaMoveTo = vertical_real_delta
		else:
			raise NameError("Invalid virtual motor name")


	def asynchronousMoveTo(self, position):
		gammaDemand, deltaDemand = self.calculateMovePositions(position)
		self.realGamma.asynchronousMoveTo(gammaDemand)
		self.realDelta.asynchronousMoveTo(deltaDemand)

	def calculateMovePositions(self, position):
		alphaPosRadians = radians(self.realAlpha.getPosition()) #  This is always const
		currentRealGammaPosRadians = radians(self.realGamma.getPosition())
		currentRealDeltaPosRadians = radians(self.realDelta.getPosition())
		if 'Gamma' in self.virtualMotorName:
			alphaPosRadians = radians(self.realAlpha.getPosition())
			gammaVirtPosRadians = radians(position)
			deltaVirtPosRadians = self.getOtherVirtualMotorPosition(alphaPosRadians, currentRealGammaPosRadians, currentRealDeltaPosRadians)
		else:
			alphaPosRadians = radians(self.realAlpha.getPosition())
			gammaVirtPosRadians = self.getOtherVirtualMotorPosition(alphaPosRadians, currentRealGammaPosRadians, currentRealDeltaPosRadians)
			deltaVirtPosRadians = radians(position)

		gammaRealDemandPositionRadians = self.calcRealGammaMoveTo(alphaPosRadians, gammaVirtPosRadians, deltaVirtPosRadians)
		deltaRealDemandPositionRadians = self.calcRealDeltaMoveTo(alphaPosRadians, gammaVirtPosRadians, deltaVirtPosRadians)
		return (degrees(gammaRealDemandPositionRadians), degrees(deltaRealDemandPositionRadians))

	def sim(self, position):
		print("pos {} {} would move:".format(self.getName(), position))
		gamma, delta = self.calculateMovePositions(position)
		print("{} to {}".format(self.realGamma.getName(), gamma))
		print("{} to {}".format(self.realDelta.getName(), delta))

	def waitWhileBusy(self):
		self.realGamma.waitWhileBusy()
		self.realDelta.waitWhileBusy()


	def getPosition(self):
		alpha = radians(self.realAlpha.getPosition())
		gamma = radians(self.realGamma.getPosition())
		delta = radians(self.realDelta.getPosition())
		#print(alpha, gamma, delta)
		#print(degrees(self.getThisVirtualMotorPosition(alpha, gamma, delta)))
		return degrees(self.getThisVirtualMotorPosition(alpha, gamma, delta))





