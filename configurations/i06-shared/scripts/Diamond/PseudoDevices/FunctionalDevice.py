
import new;

import gda;
from gda.device.scannable import ScannableBase

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
class FunctionalDeviceClass(ScannableBase):
	def __init__(self, name, deviceList, getPositionFunctionName, setPositionFunctionName=None):
		self.setName(name);
		self.setInputNames([name]);
		self.setExtraNames([]);

#		self.refObj1 = vars(gdamain)[refObj1];
		self.deviceList = deviceList;
		self.getPositionFunctionName = getPositionFunctionName;
		self.setPositionFunctionName = setPositionFunctionName;


	def getPosition(self):
		y = vars(gdamain)[self.getPositionFunctionName](self.deviceList);
		return y;

	def asynchronousMoveTo(self, newPosition):
		if self.setPositionFunctionName is not None:
			vars(gdamain)[self.setPositionFunctionName](self.deviceList, newPosition);
		return;

	def isBusy(self):
		result = False;
		for device in self.deviceList:
			if isinstance(device, gda.device.Scannable):
				if device.isBusy():
					result = True;
					break;

		return result;

	def toString(self):
		format= '%s: ' + self.getOutputFormat()[0];
		s=format % (self.getName(), self.getPosition());
		return s;





#####################################################################################
#
#The Class is for creating a device function based on a other scannable devices  
#Usage:
#	AnotherFunctionalDeviceClass(name, [listOfScannables, getPositionFunction, setPositionFunction)
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
class AnotherFunctionalDeviceClass(ScannableBase):
#	def __init__(self, name, strUnit, strFormat):
	def __init__(self, name, deviceList, getPositionFunction, setPositionFunction=None):
		self.setName(name);
		self.setInputNames([name]);
		self.setExtraNames([]);

		self.deviceList = deviceList;
		
		self.addInstanceMethod(getPositionFunction, 'getPositionFun');
		
		self.noSetter = True;
		if setPositionFunction is not None:
			self.noSetter = False;
			self.addInstanceMethod(setPositionFunction, 'setPositionFun');

		
	#add a method to the class
	def addClassMethod(self, method, name=None):
		if name is None:
			name = method.func_name
		setattr(self.__class__, name, method)

		#add a method to the instance
	def addInstanceMethod(self, method, name=None):
		if name is None:
			name = method.func_name
		nm=new.instancemethod(method, self, self.__class__)
		setattr(self, name, nm)


	def getPosition(self):
#		y = vars(gdamain)[self.getPositionFunction](self.deviceList);
		y = self.getPositionFun();
		return y;

	def asynchronousMoveTo(self, newPosition):
		if not self.noSetter:
			self.setPositionFun(newPosition);
		return;

	def isBusy(self):
		result = False;
		for device in self.deviceList:
			if isinstance(device, gda.device.Scannable):
				if device.isBusy():
					result = True;
					break;

		return result;

	def toString(self):
		format= '%s: ' + self.getOutputFormat()[0];
		s=format % (self.getName(), self.getPosition());
		return s;


#Example:
#import math
#from Diamond.PseudoDevices.FunctionalDevice import FunctionalDeviceClass
#from Diamond.PseudoDevices.FunctionalDevice import AnotherFunctionalDeviceClass

#deviceList = [testMotor1, dummyCounter, testMotor2];
#def testFun1(deviceList):
#	x1=deviceList[0].getPosition();
#	x2=deviceList[1].getPosition();
#	y=x2/5.0 + (500 + 1000*math.sin(x1));
#	return y;

#def testFun2(deviceList, newPosition):
#	x=deviceList[2];
#	x.moveTo(newPosition);
#	return;

#def testFun3(self):
#	x1=self.deviceList[0].getPosition();
#	x2=self.deviceList[1].getPosition();
#	y=x2/5.0 + (500 + 1000*math.sin(x1));
#	return y;
#
#def testFun4(self, newPosition):
#	x=self.deviceList[2];
#	x.moveTo(newPosition);
#	return;

#tm1 = FunctionalDeviceClass("tm1", deviceList, getPositionFunctionName="testFun1", setPositionFunctionName="testFun2");
#tm2 = FunctionalDeviceClass("tm2", deviceList, getPositionFunctionName="testFun1");

#tm3 = AnotherFunctionalDeviceClass("tm3", deviceList, getPositionFunction=testFun3, setPositionFunction=testFun4);
#tm4 = AnotherFunctionalDeviceClass("tm4", deviceList, getPositionFunction=testFun3);

#scan testMotor1 -10 10 0.1 tm1 dummyCounter 0.1
#scan testMotor1 -10 10 0.1 tm3 dummyCounter 0.1
