import java
from gda.device.scannable import ScannableMotionBase

import jreload
jreload.makeLoadSet("jscience",['C:\\GDAhead\\jars\\jscience.jar'])
from jscience.org.jscience.physics.quantities import Quantity as Quantity
from jscience.org.jscience.physics.units import SI as SI

def MM(distance):
	return Quantity.valueOf(distance, SI.MILLI(SI.METER))

class PD1(ScannableMotionBase):

	def __init__(self,name,value):
		self.name = name
		myfc = finder.find("FourCircle")
		myfc.moveTo("phi", MM(value))

	def asynchronousMoveTo(self,new_position):
		myfc.moveTo("phi", MM(new_position))

	def isBusy():
		return false

	def getPosition(self):
		return myfc.getPosition("phi")

	def atScanStart(self):
		print "doing atScanStart()!"

	def atScanEnd(self):
		print "doing atScanEnd()!"



