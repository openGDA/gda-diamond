from time import sleep;
import sys, os, stat;

from gda.device import Detector
from gda.device.detector import DetectorBase
from gda.device.detector import NXDetectorDataWithFilepathForSrs

from gda.device.detector.areadetector.v17.ADDriverPilatus import Gain;

from gda.analysis.io import PilatusTiffLoader, JPEGLoader, TIFFImageLoader
from gda.analysis import ScanFileHolder
#from gda.analysis import RCPPlotter;
from uk.ac.diamond.scisoft.analysis import SDAPlotter

from gda.jython import InterfaceProvider

import scisoftpy as dnp;

from Diamond.Objects.Shutter import ShutterDeviceClass
from Diamond.PseudoDevices.MetadataHeaderDevice import MetadataHeaderDeviceClass
from Diamond.PseudoDevices.MetadataHeaderDevice import MetadataConsumerClass


#Introduce the script logger
from Diamond.Utility.ScriptLogger import ScriptLoggerClass;
logger=ScriptLoggerClass();

import __main__ as gdamain

# test = ScanFileContainer()
# test.loadPilatusData("/dls/i16/data/Pilatus/test1556.tif")
# test.plot()
# matrix = test.getImage().doubleMatrix()

#class Pilatus(ScannableMotionBase):
class PseudoAreaDetectorClass(DetectorBase, ShutterDeviceClass, MetadataConsumerClass):
	DETECTOR_STATUS_IDLE, DETECTOR_STATUS_BUSY, DETECTOR_STATUS_PAUSED, DETECTOR_STATUS_STANDBY, DETECTOR_STATUS_FAULT, DETECTOR_STATUS_MONITORING = range(6);

	def __init__(self, name, panelName, detectorName, shutterName=None):
		self.setName(name);
		self.setInputNames(['exposure']);
		self.setExtraNames([]);
#		self.setOutputFormat(['%.2f']);
		self.setLevel(7);
		
		self.panel = panelName;
		self.detector = vars(gdamain)[detectorName];
		self.epicsDriver=self.detector.getAdDriverPilatus();

		self.detectorInfo = None;
#		self.dataHolder = ScanFileHolder()
		self.dataHolder = None;
		self.exposureTime = 0
		self.sum = 0
		self.maxpix = 0

#		self.filePath = None;
#		self.filePrefix = None;
#		self.fileFormat = "%s%s%4.4d.tif";
#		self.fileNumber = self.detector.getFileNumber();
		
		self.fileName = None;
		self.logScale = False;
		self.alive=True;
		
		ShutterDeviceClass.__init__(self, shutterName);
		MetadataConsumerClass.__init__(self);

	def getCollectionTime(self):
		self.exposureTime=self.detector.getCollectionTime();
		return self.exposureTime;

	def setCollectionTime(self, newExpos):
		self.exposureTime = newExpos;
		self.detector.setCollectionTime(self.exposureTime);

	def collectData(self):
		self.openShutter();
		self.getMetadata();
		self.detector.collectData();
		return;

	def endCollection(self):
#		print "Debug: "+  sys._getframe().f_code.co_name +" is called";
		self.closeShutter();


	def readout(self):
#		self.getMetadata();
		
		nxDetectorReturn=self.detector.readout();
		
		if isinstance(nxDetectorReturn, NXDetectorDataWithFilepathForSrs):
			self.fileName=nxDetectorReturn.getFilepath();
		else:
			self.fileName=str(nxDetectorReturn);
		
		if not self.fileExists(self.fileName, 100):
			logger.simpleLog( "PilatusDetectorPseudoDevice.readout(): File '" + self.fileName + "' does not exist!" );
			raise Exception("No File Found Error");
		
		self.createMetadataFiles( str(self.fileName) );
			
		if self.alive:
			self.display();
		
		return self.fileName;

	def getStatus(self):
		return self.detector.getStatus();
	
	def createsOwnFiles(self):
		return True;
	
	def endCollection(self):
		print "Debug: "+  sys._getframe().f_code.co_name +" is called";
		self.closeShutter();

# Scannable implementations
	def getPosition(self):
		return self.readout();
		
#	def asynchronousMoveTo(self,newExpos):
#		self.setCollectionTime(newExpos)
#		self.collectData();

	def atPointEnd(self):
		self.closeShutter();
#		print "Debug: "+  sys._getframe().f_code.co_name +" is called";

	def stop(self):
		self.closeShutter();

	def toString(self):
		self.getPosition();
		return "Latest image file: " + self.getFullFileName();
	
## Extra Implementation

	def setAlive(self, newAlive=True):
		self.alive = newAlive;
		
	def setLogScale(self, newLogScale=True):
		self.logScale = newLogScale;

	def setPanel(self, newPanelName):
		self.panel = newPanelName;
		
	def getDetectorInfo(self):
		return self.detectorInfo;

	def singleShot(self, newExpos):
		"""Shot single image with given exposure time""";
		if self.getStatus() != Detector.IDLE:
			print 'Pilatus not available, please try later';
			return;
		
		self.openShutter();
		self.setCollectionTime(newExpos);
		self.setNumOfImages(1);
		self.collectData();
		while self.getStatus() != Detector.IDLE:
			sleep(self.exposureTime/2.0);
		return self.readout();

	def multiShot(self, newExposureTime, newExposurePeirod, newNumberOfImages):
		"""Shot single image with given exposure time""";
		if self.getStatus() != Detector.IDLE:
			print 'Pilatus not available, please try later';
			return;
		
		self.openShutter();
		self.setCollectionTime(newExposureTime);
		self.setExposurePeriod(newExposurePeirod)
		self.setNumOfImages(newNumberOfImages);
		
		self.collectData();

		while self.getStatus() != Detector.IDLE:
			sleep(self.exposureTime * newNumberOfImages/5.0);
		self.closeShutter()
		print 'Done, file number is: ' + str( self.getFileNumber() );
		return self.detector.getMultipleFullFileNames();

	def display(self, file=None):
		if file is None:
			file = self.fileName;
			
#		self.dataHolder.loadPilatusData(file)
#		self.dataHolder.load(PilatusTiffLoader(file));
#		dataset = self.dataHolder.getAxis(0);
		self.dataHolder=dnp.io.load(file);
		dataset = self.dataHolder[0];

		if self.panel:
			if self.logScale:
				SDAPlotter.imagePlot(self.panel, DatasetMaths.lognorm(dataset)); #For RCP GUI
			else:
				SDAPlotter.imagePlot(self.panel, dataset); #For RCP GUI
		else:
			print "No panel set to display"
			raise Exception("No panel_name set in %s. Set this or set %s.setAlive(False)" % (self.name,self.name));

			
	def triggerOn(self, interval):
#		self.detector.start();
		self.detector.trigger();
		self.triggerFlag=True;
		
		while self.triggerFlag:
			sleep(interval);
			self.readout();

	def triggerOff(self):
		self.triggerFlag=False;
		self.detector.stop();

## Pilatus Implementation
	def setFile(self, subDir, newFilePrefix):
		"""Set file path and name"""
		pilatusDataDir = InterfaceProvider.getPathConstructor().createFromDefaultProperty();
#		pilatusDataDir = InterfaceProvider.getPathConstructor().createFromProperty("gda.pilatus.datadir");
		
		
		fullPath = os.path.join(pilatusDataDir, subDir);
		
		if not os.path.exists(fullPath):
			print "Warning: Pilatus image path does not exist. Create new"
			print "OS Command: " + "umask 0002; mkdir -p " + fullPath;
			os.system("umask 0002; mkdir -p " + fullPath);
			
#		Check the new path created.		
		if not os.path.exists(fullPath):
			print "Error: Pilatus image path does not exist and can not be created"
			return;

		print "Note: Current Pilatus image path: " + fullPath;
		self.detector.setFilePath(fullPath);
		self.detector.setFileName(newFilePrefix);

	def getFilePath(self):
		return self.detector.getFilePath();

	def getNextFileName(self):
		"""Returns file path of the Next image"""
		fileNumber = self.detector.getNdFile().getFileNumber_RBV();
		fileTemplate=self.detector.getFileTemplate();
		fileprefix =self.detector.getFileName();
		filePath=self.detector.getFilePath();
		fn=fileTemplate %(filePath, fileprefix, fileNumber)
		return fn
	
	def getFullFileName(self):
		"""Returns file path of the Next image"""
		return self.getNextFileName();

	def setThreshold(self, newGain, newThresholdEnergy):
		if newThresholdEnergy >100:
			newThresholdEnergy /=1000.
		self.epicsDriver.setGain( PilatusGain[ str.lower(newGain) ] );
		self.epicsDriver.setThresholdEnergy(newThresholdEnergy);
		return;
	
	def getThreshold(self):
		return [self.epicsDriver.getGain(), self.epicsDriver.getThresholdEnergy_RBV()];
	
	def setExposurePeriod(self, newExpp):
		self.detector.setExposurePeriod(newExpp);
		return;

	def getExposurePeriod(self):
		return self.detector.getExposurePeriod();

	def reset(self):
		self.epicsDriver.reset();

	def setNumOfImages(self, number):
		self.detector.setNumOfImages(number);
		
	def getNumOfImages(self):
		return self.detector.getNumOfImages();

#Additional DLS Luster fix to deal with delay
	def fileExists(self, fileName, numberOfTry):
		result = False;
	
		for i in range(numberOfTry):
			if (not os.path.exists(fileName)) or (not os.path.isfile(fileName)):
				if i>1:#To make a note if tried more than twice
					print "File does not exist on try " + str(i+1);
					logger.simpleLog( "DetectorAnalyser: File does not exist on try " + str(i+1) );
				#check again:
				sleep(1);
				os.system("ls -la " + fileName);#To try to update the file system
			else:
				#To touch the file will change the timestamps on the directory, which in turn causes the client to refetch the file's attributes. 
				os.system("touch -c " + fileName);
				
				#To check the file size non zero
				fsize = os.stat(fileName)[stat.ST_SIZE];
				if i>1:#To make a note if tried more than twice
					print "File exists on try " + str(i+1) + " with size " + str(fsize);
					logger.simpleLog( "DetectorAnalyser: File '" + fileName + "' exists on try " + str(i+1) + " with size " + str(fsize) );
					
				sizeP100K = 383956L; sizeP2M=9910196L;
				if fsize!=sizeP100K and fsize!=sizeP2M:
					print "Wrong file size: " + str(fsize);
					logger.simpleLog( "DetectorAnalyser: File '" + fileName + "' has wrong file size: " + str(fsize) );
					sleep(1);
					continue;
				#The file seems exist with some content inside. Double check to make sure it's available
				try:
					#To touch the file will change the timestamps on the directory, which in turn causes the client to refetch the file's attributes. 
					os.system("touch -c " + fileName);
					tf = open(fileName,"rb");
					tf.close();
					result = True;
					break;
				except:
					print "There are something wrong on the file system !!!"
					logger.simpleLog( "DetectorAnalyser: There are something wrong on the file system !!!");
		return result;



#Usage 
#ps100k = PilatusPseudoDeviceClass('ps100k', 'p1');
#ps100k.setFile('/home/xr56/Dev/users/data/','p100k');
#ps100k.setAlive(True);

#ps2m = PilatusPseudoDeviceClass('ps2m', 'p1');
#ps2m.setFile('/home/xr56/Dev/users/data/',  'p2m');
#ps2m.setAlive(True);

