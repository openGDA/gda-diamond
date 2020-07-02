from gda.device.scannable import ScannableMotionBase
from gda.device import Scannable
from gda.factory import Finder

import time;

#####################################################################################
#
#The Class is for creating a scannable Control Point
#Usage:
#	ScannableControlPointClass(name, lowLimit, highLimit, refObj, delay)
#
#Parameters:
#   name:   Name of scannable ControlPoint
#	lowLimit: lower limit
#	highLimit: Upper limit
#	refObj: Name of the Control Point Object
#	delay: time needed in milli-second to reach the new value
#
#####################################################################################
class ScannalbeControlPointClass(ScannableMotionBase):
#	def __init__(self, name, strUnit, strFormat):
	def __init__(self, name, lowLimit, highLimit, refObj, delay):
		self.setName(name);
		self.setInputNames([name]);
		self.setExtraNames([name]);
		#self.Units=[strUnit]
		#self.setOutputFormat([strFormat])
		self.setLevel(5);
		self.value = 0.0;
		self.lowLimit = lowLimit;
		self.highLimit = highLimit;
		self.refObj = Finder.find(refObj);
		self.delay = delay;

	def setDelay(self, newDelay):
		self.delay = newDelay;

	def getDelay(self):
		return self.delay;

	def getPosition(self):
		self.value=self.refObj.getValue();
		return self.value;

	def asynchronousMoveTo(self, new_position):
		self.value = new_position;
		self.refObj.setValue(new_position);
#		time.sleep(self.delay/1000.0)

	def isBusy(self):
		if(self.delay > 0.0):
			time.sleep(self.delay/1000.0);
		return;

 	def toString(self):
		ss="Control Point "+ self.getName() + " : " + str(self.getPosition()) + " (" + str(self.lowLimit) + " : "+ str(self.highLimit) + ")";
		return ss;

