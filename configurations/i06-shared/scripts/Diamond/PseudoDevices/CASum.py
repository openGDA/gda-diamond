from gda.device.scannable import ScannableMotionBase
from gda.device import Scannable
from gda.factory import Finder

from time import sleep


#The Class is for creating a Psuedo Device to read the average current amplifier reading from RS232
#Usage:
#	CurrentAmplifierSumClass(name, refCA)
#
#Parameters:
#   name:   Name of the new device
#	refCA: Name of the current amplifier (for example: "ca32")
#	funForeward: Name of the function to calculate the new position based on refObj position
#	funBackward: Name of the function to calculate back the refObj position based on new position
#
#Example: When calculate the yGap based on xMotor
#	name = yGap
#	refObj = xMotor
#	yGap = funForewardFun(xMotor)
#	xMotor = funBackward(yGap)
#
#
#####################################################################################
class CurrentAmplifierSumClass(ScannableMotionBase):
	def __init__(self, name, refCA):
		self.setName(name);
		self.setInputNames([name+"_sum"]);
		self.setExtraNames([name+"_average"]);
#		self.Units=[strUnit];
		self.setLevel(7);
		
		self.sum = 0;
		self.average = 0;
		self.total = 1; #default number of counts

#		self.refCA = globals()[refCA];
		self.refCA = Finder.find(refCA);
		

	def atScanStart(self):
		self.sum = 0;
		self.average = 0;

	#Scannable Implementations
	def getPosition(self):
		self.sum =0;
		for i in range(self.total):
			self.sum += self.refCA.getPosition();
		self.average = self.sum/self.total;

#		return self.sum;
#		return self.average;
		return [self.sum, self.average];
	
	def asynchronousMoveTo(self,newPos):
		self.total = newPos;

	def isBusy(self):
		return 0;

