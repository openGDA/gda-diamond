from java import lang
from gda.factory import Finder
from gda.device.scannable import ScannableMotionBase
from gda.device import Scannable
from time import sleep

#The Class for creating a PEEM UView Detector as Psuedo Device
#For PEEM UView in I06 only.
class TfgDetectorClass(ScannableMotionBase):
	def __init__(self, name):
		self.setName(name);
		self.setInputNames([]);
		self.setExtraNames([name]);
#		self.Units=[strUnit];
		self.setLevel(7);
		self.tfgXs = Finder.find("counterTimer02");
		self.xs2 = Finder.find("xspress2system");
		self.tfg = Finder.find("tfg");

	def atScanStart(self):
#		self.tfgXs.countAsync(1000);
		self.xs2.clear();
		self.xs2.start();
		self.tfg.countAsync(1000);
		print "TfgXspress scan started";

	#Scannable Implementations
	def getPosition(self):
		self.disableXspress();
		print self.tfgXs.readout();
		return -1;
	
	def asynchronousMoveTo(self,newPos):
		self.tfgXs.setCollectionTime(newPos);
		self.tfgXs.collectData();

	def isBusy(self):
		if self.tfgXs.getStatus() == 1:
			return 1;
		else:
			return 0;

	def atScanEnd(self):
#		self.tfgEx.stop();
#		self.xs2.stop();
		print "TfgXspress scan completed";

	
	def getCollectionTime(self):
		print self.tfgXs.getCollectionTime();

	def setCollectionTime(self, newExpos):
		self.tfgXs.setCollectionTime(newExpos);

	def disableXspress(self):
		self.xs2.stop();
	
	def setXsReadoutMode (self, mode):
		self.xs2.setReadoutMode(mode);
		

tfgXp = TfgDetectorClass("tfgXp");

