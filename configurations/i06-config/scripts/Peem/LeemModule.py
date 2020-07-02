from time import sleep
from gda.factory import Finder
from gda.device.scannable import ScannableBase

#####################################################################################
#
#The Class is for creating a scannable Compound Energy that involves PGM, Undulator Gap and Row Phase
#Usage:
#	CompoundEnergyClass(name, lowLimit, highLimit, refObj, gapFun, bladeFun)
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

#Set the PEEM
class LeemModuleClass(ScannableBase):
	def __init__(self, name, leem, index):
		self.setName(name);
		self.setInputNames([name]);
		self.setExtraNames([]);
#		self.Units=[strUnit];
		self.setLevel(7);
		self.leem = leem;
		self.index = index;
		self.value = 0;

#	def atScanStart(self):
#		self.getPosition();

	def getPosition(self):
		self.value =self.leem.getPSValue(self.index);
		return self.value;
	
	def asynchronousMoveTo(self, new_position):
		self.value = new_position;
		self.leem.setPSValue(self.index, self.value)


	def isBusy(self):
		sleep(1)
		return 0;

class LeemFieldOfViewClass(ScannableBase):
	
	def __init__(self, name, msImpl):
		self.setName(name);
		self.setInputNames([name]);
		self.setExtraNames([]);
		self.setOutputFormat(['%s'])
		self.setLevel(7);

#		peemBridge = Finder.find("peemBridge");
#		msImpl=peemBridge.connect()
		self.msImpl = msImpl;
		self.fov = None;
		self.defaultGroup='A';
		
	def changeGroup(self, newGroup='A'):
		if newGroup not in ['A', 'B']:
			print "LEEM power supply presets set should be 'A' or 'B'"
			return
		self.defaultGroup=newGroup;

	def isBusy(self):
		sleep(0.5);
		return False

	def getPosition(self):
		fov=str(self.msImpl.GetPresetLabel())
		self.fov=fov.decode('utf-8');
		return self.fov;

	def asynchronousMoveTo(self,new_position):
		if str(new_position) in ['LEED']:
			labelInUnicode=str(new_position);
		elif int(new_position) in [80, 50, 40, 30, 20, 15, 6, 2]:
			labelInUnicode=u'%s\xb5m' %( int(new_position) );
		elif int(new_position) in [10]:
			labelInUnicode='10um';
		else:
			raise ValueError("Wrong preset value")
		
		groupNumber=65;
		if self.defaultGroup == 'B':
			groupNumber=66;
			
		result = self.msImpl.SelectPreset(groupNumber, labelInUnicode);
		
		if result == 0:
			sleep(5);
			return;
		if result == -2:
			raise ValueError("No such group found.");
		if result == -3:
			raise ValueError("No such name for preset found.");
		else:
			raise RuntimeError("Unknown error!");
		return;
	
	def toFormattedString(self):
		return 'fov: ' + self.getPosition();

