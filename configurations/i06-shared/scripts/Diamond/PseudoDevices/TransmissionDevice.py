#New style Pseudo devices use gda.device.scannable.ScannableMotionBase 
from gda.device.scannable import ScannableMotionBase

import __main__ as gdamain

#A Transmission Device that drives the slave device based on the master device's position using user defined function
class TransmissionDeviceClass(ScannableMotionBase):
	def __init__(self, name, masterObj, slaveObj, deviceFunName):
		self.setName(name);
		self.setInputNames([name]);
		self.setExtraNames([]);
		self.setLevel(9);

		self.masterObj = vars(gdamain)[masterObj];
		self.slaveObj = vars(gdamain)[slaveObj];
		self.deviceFunName = deviceFunName;

		self.x = 0.0;#master object position
		self.y = 0.0;#desired slave object position
		self.y0 = 0.0;#slave object real position

	def setMaster(self, masterObj):
		self.masterObj = vars(gdamain)[masterObj];
		
	def setSlave(self, slaveObj):
		self.slaveObj = vars(gdamain)[slaveObj];


	def getPosition(self):
#        self.X=eval(self.masterObjName + ".getPosition()");
		self.x=self.masterObj.getPosition();
		self.y0=self.slaveObj.getPosition();
		self.y = self.funForeward(self.x);
		return self.y;
    
	def funForeward(self, x):
		#return eval(self.deviceFun + "("+ str(x1) + " , " + str(x2) + ")");
		y=vars(gdamain)[self.deviceFunName](x);
		return y;

	def asynchronousMoveTo(self, newPosition):
		if newPosition == False:
			print "Transmission disabled"
			return;
		#print "Note that this device drives the slave device " + self.slaveObj.getName() + " based on the master "  + self.masterObj.getName() + " using user defined function" + self.deviceFunName;
		#print "Master Poistion: " + str(self.masterObj.getPosition());
		#print "Slave Position: "  + str(self.slaveObj.getPosition());
		#print "Slave Position to be: "  + str(self.getPosition());
		self.slaveObj.moveTo(self.getPosition());

	def isBusy(self):
#		return (self.masterObj.isBusy() | self.slaveObj.isBusy());
		return self.slaveObj.isBusy();

	def toString(self):
		ss = 'Master Poistion: ' + str(self.masterObj.getPosition() )+ '  --- > Slave Position: '  + str(self.slaveObj.getPosition());
		return ss;

#Example:
#gear = TransmissionDeviceClass("gear", "testMotor1", "testMotor2", "myFunction");
#
#def myFunction(x):
#	y=x+500;
#	return y;

#Example Usage:
#scan testMotor1 0 10 1 gear 1 testMotor2

