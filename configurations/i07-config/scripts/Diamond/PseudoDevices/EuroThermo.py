
from gda.device.scannable import ScannableBase

class EuroThermoLoopOutputClass(ScannableBase):
	def __init__(self, name, controller):
		self.setName(name);
		self.setInputNames([name]);
		self.setExtraNames([]);
		self.setOutputFormat(["%.1f"])
		self.controller = controller;
		self.is_busy = False;
		self.target = None

	def getPosition(self):
		return self.controller.getOutput()

	def asynchronousMoveTo(self, newPosition):
		self.controller.setOutput(newPosition);
		self.target = newPosition
		self.is_busy = True

	def isBusy(self):
		if self.is_busy :
			self.is_busy = abs(self.getPosition() - self.target) >= 0.01
		return self.is_busy

	def toString(self):
		format_str= '%s: ' + self.getOutputFormat()[0];
		s=format_str % (self.getName(), self.getPosition());
		return s;

	def toFormattedString(self):
		return self.toString();

#####################################################################################
#The Class is for creating a device to get/set the Output field of a EuroThermo loop based on the EuroThermo controller
#from Diamond.PseudoDevices.EuroThermo import EuroThermoLoopOutputClass

#etc11=Finder.find("etcontroller11");

#etoutput11 = EuroThermoLoopOutputClass("etoutput11", etc11);
