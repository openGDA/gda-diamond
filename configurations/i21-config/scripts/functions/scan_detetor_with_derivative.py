'''
This module provides a class definition for creating a scannable that returns the derivative of scannableY over scannableX
while scanning scannableX and scannableY.
Usage:
	>>>dr=DeviceDerivativeClass("dr", scannable1, scannable2, "derivative");
	>>>scan scannable1 1 10 1 scannable2 2 dr

Created on 24 Jun 2010

@author: fy65
'''
from gda.device.scannable import ScannableBase
#from gda.factory import Finder

class DeviceDerivativeClass(ScannableBase):
#	def __init__(self, name, strUnit, strFormat):
	def __init__(self, name, scannable1, scannable2, deviceFun="derivative"):
		'''constructor parameters:
				name:   Name of the new device
				scannable1: Name of the scannable on X-axis (for example: "energy")
				scannableY: Name of the scannable on Y-axis (for example: "mac15")
				deviceFun:  Name of the function to calculate the new position based on scannable1 and scannableY positions'''
		self.setName(name);
		self.setInputNames([name]);
		#self.Units=[strUnit]
		#self.setOutputFormat([strFormat])
		#self.setLevel(8);
		self.x1 = 0.0;
		self.x2 = 0.0;
		self.y = 0.0;
		self.refObj1 = scannable1
		self.refObj2 = scannable2
		self.deviceFun = deviceFun
		self.firstPoint=False
		
	def atScanStart(self):
		self.firstPoint=True
		
	def getPosition(self):
		'''return the derivative value of two scannables. The first value must be discarded as zeros are used for the starting point. '''
		global lastx1
		lastx1 = self.x1
		global lastx2
		lastx2 = self.x2
		self.x1=self.refObj1.getPosition();
		self.x2=self.refObj2.getPosition();
		if self.firstPoint:
			self.firstPoint=False
			return self.x2/self.x1
		self.y = self.funForeward(self.x1, self.x2);
		return self.y;

	def funForeward(self, x1, x2):
		return eval(self.deviceFun + "("+ str(x1) + " , " + str(x2) + ")");

	def asynchronousMoveTo(self, new_position):
		print "Can not set position for this derivative type device";

	def isBusy(self):
		'''returns busy if the two scannables are busy'''
		return (self.refObj1.isBusy() or self.refObj2.isBusy());

lastx1 = 0
lastx2 = 0

def derivative(x1, x2):
	'''returns the differential ratio of two scannables'''
	y=-(x2-lastx2)/(x1-lastx1);
	return y;

