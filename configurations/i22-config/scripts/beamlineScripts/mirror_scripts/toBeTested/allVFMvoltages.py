import java
import gda.device.scannable.ScannableBase
from math import sin
from math import asin

"""
    Purpose:       To enable raw keV to be supplied instead of Bragg i.e. no additional mono motor moves
    running:       type bkeV = BraggInkeV() in jython terminal at >>> prompt
    Author:        Nick Terrill
    Date:          April 14 2008
    
"""

class AllVFMVoltages(gda.device.scannable.PseudoDevice):

	""" Constructor method give the device a name - in this case bkeV"""
	def __init__(self):
		self.name = "allVfm"
		self.firstCall = 1
		self.fPoint = 218.8
		self.step = 20 
		
	""" This device is busy if Bragg is moving """
	def isBusy(self):
		return 0

	""" Return the keV value"""
	def getPosition(self):
		return float(caget("BL22I-OP-KBM-01:VFM:GET-VOUT00")) - self.fPoint

	""" Moves to the keV value supplied """
	def asynchronousMoveTo(self,X):
		if ( self.firstCall == 0 ):
			caput("BL22I-OP-KBM-01:VFM:SET-ALLSHIFT", self.step )
		if ( self.firstCall == 1 ):
			caput("BL22I-OP-KBM-01:VFM:SET-ALLSHIFT", X)
			self.firstCall = 0
			
		print "Voltages changed, sleeping 300s"
		sleep(300)
		print "Voltages changed, done"
		return

	def setFirstCall(self):
		self.firstCall = 1
	
	def setStep(self, step):
		self.step = step 

	def setInitialPoint(self, point):
		self.fPoint = point 
		
allVfm=AllVFMVoltages()
