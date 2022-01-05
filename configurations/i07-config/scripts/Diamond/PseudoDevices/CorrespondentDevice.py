from gda.device.scannable import ScannableMotionBase
from gda.device import Scannable
from gda.factory import Finder

import __main__ as gdamain

#####################################################################################
#
#The Class is for creating a scannable device based on the other scannable device
#Usage:
#	CorrespondentDeviceClass(name, lowLimit, highLimit, refObj, funForeward, funBackward)
#
#Parameters:
#   name:   Name of the new device
#   unit:   Unit string
#	lowLimit: lower limit of the new device
#	highLimit: Upper limit of the new device
#	refObj: Name of the real motor (for example: "s4y")
#	funForeward: Name of the function to calculate the new position based on refObj position
#	funBackward: Name of the function to calculate back the refObj position based on new position
#
#Example: When calculate the yGap based on xMotor
#	name = yGap
#	refObj = xMotor
#	yGap = funForewardFun(xMotor)
#	xMotor = funBackward(yGap)
#
#####################################################################################
class CorrespondentDeviceClass(ScannableMotionBase):
	def __init__(self, name, unit, lowLimit, highLimit, refObjName, funNameForeward, funNameBackward):
		self.setName(name);
		self.setInputNames([name]);
		self.setExtraNames([]);
		self.Units=[unit];
		#self.setOutputFormat([strFormat])
		self.setLevel(5);
		self.x = 0.0;
		self.y = 0.0;
		self.lowLimitY = lowLimit;
		self.highLimitY = highLimit;
		self.refObj = vars(gdamain)[refObjName];
		self.funNameForeward = funNameForeward;
		self.funNameBackward = funNameBackward;

	def funBackward(self, y):
		#return eval(self.bFun + "("+ str(y) +")");
		x = vars(gdamain)[self.funNameBackward](y);
		return x;
		
	def funForeward(self, x):
		#return eval(self.fFun + "("+ str(x) +")");
		y=vars(gdamain)[self.funNameForeward](x);
		return y;
	

	def getPosition(self):
#		self.X=eval(self.refObjName + ".getPosition()");
		self.x=self.refObj.getPosition();
		self.y = self.funForeward(self.x);

		#strLo = self.refObj.getSoftLimitLower();
		#strHi = self.refObj.getSoftLimitUpper();
		#self.lowLimitYGap = self.funBladeToGap(float(strLo.split(' ',1)[0]));
		#self.highLimitYGap = self.funBladeToGap(float(strHi.split(' ',1)[0]));
		return self.y;
	
	def moveTo(self, new_position):
		printed = False;
		while self.isBusy():
			if not printed:
				print "Target object is busy, waiting...";
				printed = True;
			sleep(0.2);
			
		print "Target object is ready. Now moving...";
		self.refObj.moveTo(self.x);
	
	def asynchronousMoveTo(self, new_position):
		self.y = new_position;
		self.x=self.funBackward(self.y);
		self.refObj.asynchronousMoveTo(self.x);

	def isBusy(self):
		return self.refObj.isBusy();
	
	def stop(self):
		return self.refObj.stop();

	def atScanEnd(self):
		return self.refObj.atScanEnd();


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
#import math;
#from Diamond.PseudoDevices.CorrespondentDevice import CorrespondentDeviceClass;
#s6ygap = CorrespondentDeviceClass("s6ygap","micron", 0.0, 600.0, "s6x","s6_x_ygap", "s6_ygap_x");

#Calculate Exit Slit S6 X negative motor position from the YGap
#input: slit gap opening (um)
#output: motor position (mm)
#def s6_ygap_x(ygap):
#	P0=-11.7279301227
#	P1=0.0194152929711
#	P2=-1.12948978658E-4
#	P3=7.40297574845E-7
#	P4=-3.46976646360E-9
#	P5=1.09905068661E-11
#	P6=-2.28882018062E-14
#	P7=2.98659435609E-17
#	P8=-2.20413687142E-20
#	P9=6.99833786007E-24
#	x = P0+P1*ygap+P2*ygap**2+P3*ygap**3+P4*ygap**4+P5*ygap**5+P6*ygap**6+P7*ygap**7+P8*ygap**8+P9*ygap**9;
#	return x;

