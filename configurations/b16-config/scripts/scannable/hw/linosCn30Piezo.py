from gda.device.scannable import ScannableMotionBase
from gdascripts.scannable.epics.PvManager import PvManager

import math
import time
from copy import copy

STEPSIZES = (100, 50, 20, 10, 5, 2, 1)

#def toDecimal(multipliers):
#	if len(multipliers) != len(STEPSIZES):
#		raise ValueError("length was %i, expected %i" % 
#(len(multipliers), len(STEPSIZES)))
#	total = 0
#	for m, s in zip(multipliers, STEPSIZES):
#		total += m * s
#	return total

def toSteps(toconvert, multipliers, stepsizes):
	stepsizes = list(stepsizes)
	if len(stepsizes) == 0:
		if toconvert != 0:
			raise AssertionError()
		return multipliers
	stepsize = stepsizes.pop(0)
	multiplier = math.floor(toconvert / stepsize)
	multipliers.append(multiplier)
	return toSteps(toconvert - multiplier * stepsize, multipliers, stepsizes)


class LinosCn30PiezoStage(ScannableMotionBase):
	
	def __init__(self, name, pvroot):
		# pvroot is for example: BL16B-EA-CN30-01:X:
		self.setName(name)
		self.setInputNames([name])
		self.pvs = PvManager(['POSITION', 'STEPSIZE', 'DIR', 'SPEED', 'STEP', 'BUSY', 'STAT'], pvroot)
		self.pvs.configure()
		self.delayAfterAskingToMove = .5
		self.debug = False
		
	def getPosition(self):
		return int(float(self.pvs['POSITION'].caget()))
	
	def isBusy(self):
		return False
		#asynchMoveToWill block for now
	
	def asynchronousMoveTo(self, absolutePosition):
		absolutePosition = int(absolutePosition)
		delta = absolutePosition - self.getPosition()
		self.moveBy(delta)

	def moveBy(self, relativePosition):
		if relativePosition >= 0:
			sign = 1
		else:
			relativePosition = -relativePosition
			sign = -1
		multiples = toSteps(relativePosition, [], copy(STEPSIZES))
		if self.debug:
			self._printPlan(multiples)
		totalRequested = 0
		for stepsize, multiple in zip(STEPSIZES, multiples):
			for _ in range(multiple):
				self.moveBySingleStep(sign * copy(stepsize))
				totalRequested += sign * copy(stepsize)
		if self.debug:
			print "Total requested of epics: ", totalRequested
		
	def moveBySingleStep(self, relativePosition):
		if self.debug:
			print "moving ", self.getName(), " by ", relativePosition
		if relativePosition >= 0:
			self._setDirection(+1)
		else:
			self._setDirection(-1)
			relativePosition = -relativePosition
		self._setStepSize(relativePosition)
		self.pvs['STEP'].caput(10, 1)
		
	def _setDirection(self, dir):
		# dir is +1 or -1
		if dir == +1:
			self.pvs['DIR'].caput(0)
		elif dir == -1:
			self.pvs['DIR'].caput(1)
		else:
			raise ValueError("_setdirection expects 1 or -1, not: ", dir)
		
	def _getDirection(self):
		directionIndex = int(float(self.pvs['DIR'].caget()))
		if directionIndex == 0:
			return 1
		if directionIndex == 1:
			return -1
		raise ValueError("Unexpected index: ", directionIndex)
	
	def _getStepSize(self):
		index = 7 - int(float(self.pvs['STEPSIZE'].caget()))
		return STEPSIZES[index]
	
	def _setStepSize(self, size):
		index = 7 - list(STEPSIZES).index(size)
		self.pvs['STEPSIZE'].caput(index)
		
	def _printPlan(self, multiples):
		total = 0
		for stepsize, multiple in zip(STEPSIZES, multiples):
			print '%i * %i = %i' % (multiple, stepsize, multiple*stepsize)
			total += multiple*stepsize
		print "planned total: ", total