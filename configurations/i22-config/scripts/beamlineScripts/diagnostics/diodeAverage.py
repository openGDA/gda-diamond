import java
import gda.device.scannable.ScannableBase
from math import log
from time import sleep

"""
    Purpose:       A pseudo device for measuring several points on the diode before returning
    Author:        M. Malfois
    Date:          Dec 07 2010

    This dummy scannable acts like a diode might, except rather than moving a physical axis, it simply moves an internal variable called currentPosition.

	To use this script first run the script with the run button then in the Jython Terminal type diode_average=DiodeAverage("diode_average", d10d1, 10)
    	where d10d1 is the variables used to create norm. In this example it will read 10 points and average them before returning the readout. 
	This can be used to set up other diodes etc as required.

    Edited:        N. Terrill
    Date:          13 September 2013
    Notes:	   Changed names to reflect new naming convention. This script is currently enabled for d10d2
    example initialisation: da=DiodeAverage("da", d10d2, 5)
"""

class DiodeAverage(gda.device.scannable.PseudoDevice):

	def __init__(self, name, diode, numberOfPoints):
		self.setName(name)
		self.diode = diode
		self.numberOfPoints = numberOfPoints
		self.setInputNames([])
		self.setExtraNames(["da_"+diode.getName()])
		topup.secsAfter = 580
		
	def setNumberOfPoints(self, numberOfPoints):
		self.numberOfPoints = numberOfPoints

	def getNumberOfPoints(self):
		return self.numberOfPoints

	def stScanLineStart(self):
		sleep(10)
	
	def getDiode(self):
		return self.diode
	
	""" This dummy device is never busy"""
	def isBusy(self):
		return 0

	""" Return the normalised Flux value"""
	def getPosition(self):					
		average = 0.0
		for i in range (self.numberOfPoints):
			topupTime = topup.getPosition()
			n = 0
			while( topupTime != -1 and ( topupTime < topup.secsBefore or topupTime > topup.secsAfter )):
				if ( n == 0 ):
					print "Topup starts in "+ str(topup.secsBefore)+ "s"
					print "Data collection will be resumed in "+ str(600-topup.secsAfter)+ "s"
					n = 1
				sleep(1)
				topupTime = topup.getPosition()

			sleep(0.2)
			readout = self.diode.getPosition()
			average = average + readout
		average = average/ self.numberOfPoints
		return average	 

	""" we are not moveable """
	def asynchronousMoveTo(self,newPosition):
		return


