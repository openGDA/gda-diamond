import java
import gda.device.scannable.ScannableBase
from math import log


class NormaliseAndAverage(gda.device.scannable.PseudoDevice):
	"""
		Purpose:       A pseudo device for normalising and averaging diode readouts
			Author:        Andy Smith
			Date:          Mar 24 2015

			This scannable allows one to divide the position of one variable by another and average
			eg. diode value by ringcurrent
			example initialisation:
			d10d2_normAv = NormalisedAndAverage("d10d2_normAv", d10d2, ringcurrent, 5)
			
	"""

	def __init__(self, name, num, denom, numberOfPoints):
		""" Constructor takes a string as a name and i0 and it scannables """
		self.name = name
		self.num = num
		self.denom = denom
		self.numberOfPoints = numberOfPoints
		self.setInputNames([name])


	def isBusy(self):
		""" This dummy device is never busy"""
		return 0

	def getPosition(self):
		""" Return the normalisation value"""
		average = 0.0
		for i in range (self.numberOfPoints):				
			sleep(0.2)
			readout = self.num.getPosition()/self.denom.getPosition()
			average = average + readout
		average = average/ self.numberOfPoints
		return average

	def asynchronousMoveTo(self,newPosition):
		""" we are not moveable """
		return

