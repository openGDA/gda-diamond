from gda.device.scannable import ScannableMotionBase

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
class FunctionAliasClass(ScannableMotionBase):
#	def __init__(self, name, strUnit, strFormat):
	def __init__(self, name, funName, funParameter = None):
		self.setName(name);
		self.setInputNames([]);
		self.setExtraNames([name]);

		self.fun = funName;
		self.parameter = funParameter;


	def getPosition(self):
		return self.fun(self.parameter);


	def asynchronousMoveTo(self, new_position):
		print "Can not set position for this calculation type device";
		return self.getPosition();

	def isBusy(self):
		return False;

 	def toString(self):
 		return self.getPosition();

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

#Example:
tf = FunctionAliasClass("tf", "testFun");
#
def testFun(x1, x2):
	y=x1+x2;
	return y;

