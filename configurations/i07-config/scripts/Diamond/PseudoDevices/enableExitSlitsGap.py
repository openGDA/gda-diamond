from gda.device.scannable import ScannableMotionBase
from gda.device import Scannable

#####################################################################################
#
#The Class is for creating a scannable Exit Slits Gap
#Usage:
#	EixtSlitsGapClass(name, lowLimit, highLimit, refObj, gapFun, bladeFun)
#
#Parameters:
#   name:   Name of the exit slits gap
#	lowLimit: lower limit of slits gap
#	highLimit: Upper limit of slits gap
#	refObj: Name of the real motor (for example: s4y)
#	gapFun: Name of the function to calculate the slits gap based on blade position
#	bladeFun: Name of the function to calculate the real blade position based on gap
#
#####################################################################################
class EixtSlitsGapClass(ScannableMotionBase):
#	def __init__(self, name, strUnit, strFormat):
	def __init__(self, name, lowLimit, highLimit, refObj, gapFun, bladeFun):
		self.setName(name);
		self.setInputNames([name]);
		self.setExtraNames([name]);
		#self.Units=[strUnit]
		#self.setOutputFormat([strFormat])
		self.setLevel(5);
		self.X = 0.0;
		self.YGap = 0;
		self.lowLimitYGap = lowLimit;
		self.highLimitYGap = highLimit;
		self.refObj = globals()[refObj];
		self.gapFun = gapFun;
		self.bladeFun = bladeFun;

	def getPosition(self):
#		self.X=eval(self.refObjName + ".getPosition()");
		self.X=self.refObj.getPosition();
		self.YGap = self.funBladeToGap(self.X);

		#strLo = self.refObj.getSoftLimitLower();
		#strHi = self.refObj.getSoftLimitUpper();
		#self.lowLimitYGap = self.funBladeToGap(float(strLo.split(' ',1)[0]));
		#self.highLimitYGap = self.funBladeToGap(float(strHi.split(' ',1)[0]));
		return self.YGap;
	
	def funGapToBlade(self, gap):
		return eval(self.bladeFun + "("+ str(gap) +")");
		
	def funBladeToGap(self, blade):
		return eval(self.gapFun + "("+ str(blade) +")");

	
	def asynchronousMoveTo(self, new_position):
		self.YGap = new_position;
		self.X=self.funGapToBlade(self.YGap);
		self.refObj.asynchronousMoveTo(self.X);

	def isBusy(self):
		return self.refObj.isBusy();
	
	def stop(self):
		return self.refObj.stop();

	def atScanEnd(self):
		return self.refObj.atScanEnd();

 	def toString(self):
 		ygap = self.getPosition();
		ss="S4.s4ygap : " + str(ygap) + " um (" + str(self.lowLimitYGap) + " : "+ str(self.highLimitYGap) + ")";
		return ss;

