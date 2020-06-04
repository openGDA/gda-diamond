from gda.device.scannable import ScannableMotionBase
from gda.device import Scannable
from gda.factory import Finder

import __main__ as gdamain

#####################################################################################
#
#The Class is for creating a device function based on two scannable devices  
#Usage:
#	DeviceFunctionClass(name, refObj1, refObj2, deviceFun)
#
#Parameters:
#   name:   Name of the new device
#	refObj1: Name of the device1 (for example: "s1x")
#	refObj2: Name of the device2 (for example: "s1y")
#	deviceFun: Name of the function to calculate the new position based on refObj1 and refObj2 positions
#
#Example: When calculate the distance of two motors
#	name = tm2
#	refObj1 = testMotor1
#	refObj2 = testMotor2
#	distance = deviceFun(testMotor1, testMotor2)
#
#####################################################################################
class DeviceFunctionClass(ScannableMotionBase):
#	def __init__(self, name, strUnit, strFormat):
	def __init__(self, name, refObj1, refObj2, deviceFunName):
		self.setName(name);
		self.setInputNames([]);
		self.setExtraNames([name]);
		self.Units=[""];
		#self.setOutputFormat([strFormat])
		#self.setOutputFormat(['%6.2f'])
		#self.setLevel(7);
		self.x1 = 0.0;
		self.x2 = 0.0;
		self.y = 0.0;

		self.refObj1 = vars(gdamain)[refObj1];
		self.refObj2 = vars(gdamain)[refObj2];
		self.deviceFunName = deviceFunName;


	def getPosition(self):
#		self.X=eval(self.refObjName + ".getPosition()");
		self.x1=self.refObj1.getPosition();
		self.x2=self.refObj2.getPosition();
		self.y = self.funForeward(self.x1, self.x2);
		return self.y;
	
	def funForeward(self, x1, x2):
		#return eval(self.deviceFun + "("+ str(x1) + " , " + str(x2) + ")");
		y=vars(gdamain)[self.deviceFunName](x1, x2);
		return y;


	def asynchronousMoveTo(self, new_position):
		print "Can not set position for this calculation type device";
		self.getPosition();

	def isBusy(self):
		return (self.refObj1.isBusy() & self.refObj2.isBusy());


	def toString(self):
		format= '%s: ' + self.getOutputFormat()[0]+' %s';
		s=format % (self.getName(), self.getPosition(), self.getUnits()[0]);
		return s;

#	def __repr__(self):
#		values=self.getPosition();
#		names=self.getInputNames()+self.getExtraNames();
#		outformat=self.getOutputFormat();
#
#		s='';
#		for i in range(len(outformat)):
#			format= '%20s  :  ' + outformat[i]+'  %s \n';
#			s=s + format % (names[i], values, self.getUnits());
#		return s;


	
	def setUnits(self, units):
		self.Units=units;

	def getUnits(self):
		return self.Units;

	

#Example:
#tm2 = DeviceFunctionClass("tm2", "testMotor1","testMotor2", "testFun");
#
#def testFun(x1, x2):
#	y=x1+x2;
#	return y;

