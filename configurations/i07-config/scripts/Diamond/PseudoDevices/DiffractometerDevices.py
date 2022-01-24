from gda.device.scannable import ScannableBase
from gda.device.scannable import ScannableMotor
from gda.device.scannable.component import MotorLimitsComponent

import __main__ as gdamain


#The Class for record and change the Diffractometer Mode in Horizontal or Vertical mode
class DiffractometerModeClass(ScannableBase):
	HORIZONTAL, VERTICAL, DUMMY, EH2DIFF= range(4);
	MODE_STRING = ['Horizontal', 'Vertical', 'Dummy', 'EH2DIFF']
	
	def __init__(self, name, diffGroup):
		self.setName(name);
		self.setInputNames([name]);
		self.setExtraNames([]);
		self.setLevel(5);
		self.setOutputFormat(["%11.7f"]);

		self.diffGroup = diffGroup;
		
#		self.mode = DiffractometerModeClass.HORIZONTAL;
		self.mode = DiffractometerModeClass.VERTICAL;
	
	def getMode(self):
		print DiffractometerModeClass.MODE_STRING[self.mode];
		return self.mode;
	
	def setMode(self, newMode):
		if type(newMode).__name__ == 'str':
			if newMode.lower() == DiffractometerModeClass.MODE_STRING[0].lower():#Horizontal mode
				self.mode = 0;
			elif newMode.lower() == DiffractometerModeClass.MODE_STRING[1].lower():#Vertical mode
				self.mode = 1;
			elif newMode.lower() == DiffractometerModeClass.MODE_STRING[2].lower():#Vertical mode
				self.mode = 2;
			elif newMode.lower() == DiffractometerModeClass.MODE_STRING[3].lower():#Vertical mode
				self.mode = 3;
			else:
				print "Please give a number 0/1/2/3 for Horizontal/Vertical/Dummy/EH2DIFF Mode"
				return;
		elif type(newMode).__name__ == 'int':
			self.mode =  newMode;
		else: #wrong type
			print "The mode should be set to 'Horizontal' , 'Vertical' or 'Dummy' Mode"
			return;
		
		for axis in self.diffGroup.getGroupMembers():
			axis.setAttribute('mode', self.mode);
			#do it again for sure?	
			theOne=vars(gdamain)[axis.getName()];
			theOne.setAttribute('mode', self.mode);

		return

	#Scannable Implementations
	def getPosition(self):
		return self.getMode();
	
	def asynchronousMoveTo(self,newPos):
		return self.setMode(newPos);

	def isBusy(self):
		return False;

	def toString(self):
		return self.getName() + " : " + DiffractometerModeClass.MODE_STRING[self.mode];

#The Class for picking up right diffractometer axis based on diffractormeter mode
class DiffractometerAxisClass(ScannableMotor):
	def __init__(self, name, axis0, axis1, axis2, axis3):
		self.setName(name);
		self.setInputNames([name]);
		self.setExtraNames([]);
		self.setLevel(5);
		self.setOutputFormat(["%8.4f"]);

		self.axis0 = axis0;
		self.axis1 = axis1;
		self.axis2 = axis2;
		self.axis3 = axis3;

		self.mode = DiffractometerModeClass.HORIZONTAL;
#		self.axis = self.axis0;
		self.setMotor(self.axis0.getMotor());
		self.configure();
		
		
	def getMode(self):
		return DiffractometerModeClass.MODE_STRING[self.mode];
	
	def setMode(self, newMode):
		if newMode in [DiffractometerModeClass.HORIZONTAL, DiffractometerModeClass.VERTICAL, DiffractometerModeClass.DUMMY, DiffractometerModeClass.EH2DIFF]:
			self.mode =  newMode;
		else:
			print "Wrong mode!";
			return;
			
		print "Changing " + self.getName() + " to " + DiffractometerModeClass.MODE_STRING[self.mode] + " mode";
		if self.mode == "Horizontal" or self.mode == 0:
			newMotor = self.axis0.getMotor();
#			newLimitComponent = self.axis0.getMotorLimitsComponent();
		elif self.mode == "Vertical" or self.mode == 1:
			newMotor = self.axis1.getMotor();
#			newLimitComponent = self.axis1.getMotorLimitsComponent();
		elif self.mode == "Dummy" or self.mode == 2:
			newMotor = self.axis2.getMotor();
#			newLimitComponent = self.axis2.getMotorLimitsComponent();
		elif self.mode == "EH2DIFF" or self.mode == 3:
			newMotor = self.axis3.getMotor();
#			newLimitComponent = self.axis2.getMotorLimitsComponent();
			
		if self.getMotor() != newMotor: # motor is not correct
			self.setMotor( newMotor );
			self.getAdditionalPositionValidators().clear();#A hack to clear the old limit component
			self.setMotorLimitsComponent(MotorLimitsComponent(newMotor));
#			self.setMotorLimitsComponent(newLimitComponent);

			self.configure();


	#Scannable Implementations
	def setAttribute(self, attributeName, value):
		if attributeName == 'mode':
			self.setMode(value);
		else:
			super.setAttribute(attributeName, value);
	

#diff1mode = DiffractometerModeClass('diff1mode', CDIFF1);
#tt = DiffractometerAxisClass('alpha', testMotor1, testMotor2);
