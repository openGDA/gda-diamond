from gda.device.scannable import ScannableBase
from gda.device import Scannable

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
class DeviceFunctionClass(ScannableBase):
#	def __init__(self, name, strUnit, strFormat):
	def __init__(self, name, refObj1, refObj2, deviceFun):
		self.setName(name);
		self.setInputNames([name]);
		self.setExtraNames([name]);
		#self.Units=[strUnit]
		#self.setOutputFormat([strFormat])
		#self.setLevel(8);
		self.x1 = 0.0;
		self.x2 = 0.0;
		self.y = 0.0;
		self.refObj1 = globals()[refObj1];
		self.refObj2 = globals()[refObj2];
		self.deviceFun = deviceFun;

	def getPosition(self):
#		self.X=eval(self.refObjName + ".getPosition()");
		self.x1=self.refObj1.getPosition();
		self.x2=self.refObj2.getPosition();
		self.y = self.funForeward(self.x1, self.x2);

		return self.y;

	def funForeward(self, x1, x2):
		return eval(self.deviceFun + "("+ str(x1) + " , " + str(x2) + ")");

	def asynchronousMoveTo(self, new_position):
		print "Can not set position for this calculation type device";
		self.getPosition();

	def isBusy(self):
		return (self.refObj1.isBusy() & self.refObj2.isBusy());

#Example:
ratio = DeviceFunctionClass("ratio", "Im","I0", "testFun");

def testFun(x1, x2):
	y=x1/x2;
	return y;

