import java
import gda.device.scannable.ScannableBase
from math import log
from time import sleep

"""
    Purpose:		A pseudo device for sleeping before returning readout of the diode. Sleeping time is user defined.
    				To be used when the motor are moving faster than the diode readout like idgap_mm, perp etc...
    Author:        M. Malfois
    Date:          May 20 2013

    This dummy scannable acts like a diode might, except rather than moving a physical axis, it simply moves an internal variable called currentPosition.

	To use this script first run the script with the run button then in the Jython Terminal type diodeSleep=DiodeSleep( d10d1, 0.1)
    	where d10d1 is the variables used to create norm. In this example it will sleep 0.1s before returning the readout. 
	This can be used to set up other diodes etc as required.

"""

class DiodeSleep(gda.device.scannable.PseudoDevice):

	def __init__(self, femto, sleepTime):
		self.name = "ds"+femto.getName()
		self.femto = femto
		self.sleepTime = sleepTime
		self.setInputNames([femto.getName()])
		self.setOutputFormat(["%5.3e"])
		
	def setSleepingTime(self, sleepTime):
		self.sleepTime = sleepTime

	def getSleepingTime(self):
		return self.sleepTime

	def setDiode(self, femto):
		self.femto = femto
		self.name = "ds_"+femto.getName()
		self.setInputNames([femto])		
		
	def stScanLineStart(self):
		sleep(10)
	
	def getFemto(self):
		return self.femto
	
	""" This dummy device is never busy"""
	def isBusy(self):
		return 0

	""" Return the readout of the femto"""
	def getPosition(self):
		sleep(self.sleepTime)
		return [ self.femto.getPosition()] 

	""" we are not moveable """
	def asynchronousMoveTo(self,newPosition):
		return

ds = DiodeSleep( d10d2, 0.1 )
