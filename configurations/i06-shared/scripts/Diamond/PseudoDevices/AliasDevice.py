from gda.device.scannable import ScannableMotionBase

import __main__ as gdamain;

#The Class for creating a scannable Motor directly from EPICS PV
#The motor status is reflected in the DMOV flag
class AliasDeviceClass(ScannableMotionBase):
	def __init__(self, name, gdaCommandString):
		self.setName(name);
		self.setInputNames([name]);
		self.expression = gdaCommandString;
		
	def setExpression(self, gdaCommandString):
		self.expression = gdaCommandString;
		print "New alias of GDA expression: '" + self.expression + "': " + self.getName();
		
	def getPosition(self):
		try:
			exec(self.expression) in vars(gdamain), vars(gdamain);
		except:
			raise;

		return;

	def asynchronousMoveTo(self,new_position):
		print self.getName() + " is an alias of GDA expression: '" + self.expression + "'.";
		print "Please just type " + self.getName(); 
	
	def isBusy(self):
		return False;

	def toString(self):
		try:
			self.getPosition();
		except:
			return "Command failed. Please check this expression: " + self.expression;
		return self.getName() + ", the alias of GDA expression: '" + self.expression + "', has been executed."


#a1 = AliasDeviceClass('a1', "testMotor1.moveTo(99)");

