from time import sleep
from java import lang
from gda.factory import Finder
from gda.device.scannable import ScannableMotionBase
from gda.device import Scannable

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
class PEEMModuleClass(ScannableMotionBase):
	def __init__(self, name, index):
		self.setName(name);
		self.setInputNames([]);
		self.setExtraNames([name]);
#		self.Units=[strUnit];
		self.setLevel(7);
		finder = Finder.getInstance();
		self.peem = finder.find("leem");
		self.index = index;
		self.value = 0;

	def atScanStart(self):
		self.getPosition();


	def getPosition(self):
		self.value =self.peem.getPSValue(self.index);
		return self.value;
	
	
	def asynchronousMoveTo(self, new_position):
		self.value = new_position;
		self.peem.setPSValue(self.index, self.value)


	def isBusy(self):
		sleep(1)
		return 0;
