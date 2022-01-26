
from time import sleep;

from gda.device.scannable import ScannableBase

class EuroThermoLoopOutputClass(ScannableBase):
	def __init__(self, name, controller):
		self.setName(name);
		self.setInputNames([name]);
		self.setExtraNames([]);

#		self.refObj1 = vars(gdamain)[refObj1];
		self.controller = controller;


	def getPosition(self):
		y = self.controller.getOutput();
		return y;

	def asynchronousMoveTo(self, newPosition):
		self.controller.setOutput(newPosition);
		sleep(2);
		

	def isBusy(self):
		result = False;
		return result;

	def toString(self):
		format= '%s: ' + self.getOutputFormat()[0];
		s=format % (self.getName(), self.getPosition());
		return s;

	def toFormattedString(self):
		return self.toString();

#####################################################################################
#The Class is for creating a device to get/set the Output field of a EuroThermo loop based on the EuroThermo controller
#from Diamond.PseudoDevices.EuroThermo import EuroThermoLoopOutputClass

#etc11=Finder.find("etcontroller11");

#etoutput11 = EuroThermoLoopOutputClass("etoutput11", etc11);
