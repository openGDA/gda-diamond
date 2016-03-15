import java
import gda.device.scannable.ScannableBase
from math import log


class NormalisedScannable(gda.device.scannable.PseudoDevice):
	"""
		Purpose:       A pseudo device for Exafs measurements
			Author:        Tobias Richter
			Date:          Feb 27 2008

			This scannable allows one to divide the position of one variable by another
			eg. diode value by ringcurrent
			example initialisation:
			d10d2_norm = NormalisedScannable("d10d2_norm", d10d2, ringcurrent)
	"""

	def __init__(self, name, numerator, divisor):
		""" Constructor takes a string as a name and numerator and divisor scannables """
		self.name = name
		self.setInputNames([name])
		self.numerator = numerator
		self.divisor = divisor

	def isBusy(self):
		""" This dummy device is never busy"""
		return 0

	def getPosition(self):
		""" Return the normalised value"""
		return self.numerator.getPosition()/self.divisor.getPosition()

	def asynchronousMoveTo(self,newPosition):
		""" we are not moveable """
		return
