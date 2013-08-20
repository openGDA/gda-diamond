
import random, time, inspect;

from gda.device.scannable import ScannableBase
from gda.device.scannable import PseudoDevice
from gda.device.detector import PseudoDetector

import __main__ as gdamain


#####################################################################################
#
#The Class is for creating a device function based on a other scannable devices  
#Usage:
#	FunctionalDeviceClass(name, [listOfScannables, getPositionFunctionName, setPositionFunctionName)
#
#Parameters:
#   name:   Name of the new device
#	listOfScannables: A list of scannables involved in the operation
#	deviceFun: Name of the function to calculate the new position based on positions of a listOfScannables
#
#Example: When calculate the distance of two motors and use this distance to set the third motor
#	name = tm2
#	listOfScannables = [testMotor1, testMotor2, testMotor3]
#	getPositionFunction: A function that used to find the distance between two motors
#	setPositionFunction = A function to set the third motor
#
#####################################################################################
class TestDeviceClass(ScannableBase):
	def __init__(self, name):
		self.setName(name);
		self.setInputNames([name]);
		self.setExtraNames([]);

		self.myPosition=0;
#		self.refObj1 = vars(gdamain)[refObj1];


	def getInspect(self):
		return inspect.stack();


	def getPosition(self):
		return self.myPosition;

	def asynchronousMoveTo(self, newPosition):
		self.myPosition = float(newPosition) + random.random();
		time.sleep(0.6)
		return;

	def isBusy(self):
		return False;

	def toString(self):
		format= '%s: ' + self.getOutputFormat()[0];
		s=format % (self.getName(), self.getPosition());
		return s;

	def atPointStart(self):
		print "-----> Method called: %s." % inspect.stack()[0][3];
		
	def atPointEnd(self):
		print "-----> Method called: %s." % inspect.stack()[0][3];

	def atScanLineStart(self):
		print "----------> Method called: %s." % inspect.stack()[0][3];
		
	def atScanLineEnd(self):
		print "----------> Method called: %s." % inspect.stack()[0][3];
	
	def atScanStart(self):
		print "--------------------> Method called: %s." % inspect.stack()[0][3];
		
	def atScanEnd(self):
		print "--------------------> Method called: %s." % inspect.stack()[0][3];

	def stop(self):
		pass

#Example:
td = TestDeviceClass("td");

