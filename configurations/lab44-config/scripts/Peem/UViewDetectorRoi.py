from time import sleep

from gda.factory import Finder
from gda.device.scannable import PseudoDevice
from gda.device.detector import PseudoDetector
from gda.device import Scannable


#The Class for creating a PEEM UView Detector as Psuedo Device
#For PEEM UView in I06 only.
class UViewDetectorClass(PseudoDetector):
	def __init__(self, name):
		self.setName(name);
		self.setInputNames([name]);
		self.setExtraNames([]);
#		self.Units=[strUnit];
		self.setLevel(7);
		finder = Finder.getInstance();
		self.uview = finder.find("uview");

#def atScanStart(self):
#	self.uview.prepare();

	#Scannable Implementations

#	def isBusy(self):
#		return self.uview.getStatus();
#

	def singleShot(self, newExpos):
		self.setCollectionTime(newExpos);
		print self.uview.shotSingleImage();
		

	#PseudoDetector Implementation
	def asynchronousMoveTo(self,newPos):
		self.uview.setCollectionTime(newPos);
		self.collectData();

	def getCollectionTime(self):
		return self.uview.getCollectionTime();

	def setCollectionTime(self, newExpos):
		self.uview.setCollectionTime(newExpos);

	def collectData(self):
		self.uview.collectData();
		
	def prepareForCollection(self):
		self.uview.prepare();
	
	def readout(self):
#		print self.uview.readout();
#		return -1;
		return self.uview.readout();

	def getStatus(self):
		return self.uview.getStatus();


#The Class for creating a PEEM UView Region Of Interests Detector as Psuedo Device
#For PEEM UView in I06 only.
class UViewDetectorROIClass0(PseudoDevice):
	def __init__(self, name, roi):
		self.setName(name);
		self.setInputNames([]);
		self.setExtraNames([name]);
#		self.Units=[strUnit];
		self.setLevel(7);
		finder = Finder.getInstance();
		self.roi = finder.find(roi);

	def reset(self):
		finder = Finder.getInstance();
		self.roi = finder.find(roi);
		
	#PsuedoDevice Implementations
	def getPosition(self):
		temp = self.roi.readout();
		return temp;
	
	def asynchronousMoveTo(self,newPos):
		self.roi.setCollectionTime(newPos);
		self.roi.collectData();


	def isBusy(self):
		return self.roi.getStatus();

	def atScanEnd(self):
		return;

	def getCollectionTime(self):
		print self.roi.getCollectionTime();

	def setCollectionTime(self, newExpos):
		self.roi.setCollectionTime(newExpos);

	def setLocation(self, newX, newY):
		self.roi.setLocation(newX, newY);

	def setSize(self, newWidth, newHeight):
		self.roi.setSize(newWidth, newHeight);

#The Class for creating a PEEM UView Region Of Interests Detector as Psuedo Detector
#For PEEM UView in I06 only.
class UViewDetectorROIClass(PseudoDetector):
	def __init__(self, name, roi):
		self.setName(name);
		self.setInputNames([name]);
		self.setExtraNames([]);
#		self.Units=[strUnit];
		self.setLevel(7);
		finder = Finder.getInstance();
		self.roi = finder.find(roi);

	def reset(self):
		finder = Finder.getInstance();
		self.roi = finder.find(roi);
		
	#PseudoDetector Implementation
#	def getPosition(self):
#		return self.readout();
	
	def asynchronousMoveTo(self,newPos):
		self.setCollectionTime(newPos);
		self.collectData();

	def collectData(self):
		self.roi.collectData();
		
	def getStatus(self):
		return self.roi.getStatus();

	def getCollectionTime(self):
		 return self.roi.getCollectionTime();

	def setCollectionTime(self, newExpos):
		self.roi.setCollectionTime(newExpos);

	def readout(self):
		return self.roi.readout();

	def setLocation(self, newX, newY):
		self.roi.setLocation(newX, newY);

	def setSize(self, newWidth, newHeight):
		self.roi.setSize(newWidth, newHeight);
