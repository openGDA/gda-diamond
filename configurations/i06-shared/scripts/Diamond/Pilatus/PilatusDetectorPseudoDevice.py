from time import sleep;
import os, stat;

#from gda.device.detector import PseudoDetector
from gda.device.detector import DetectorBase
from gda.device import Detector


from gda.analysis.io import PilatusTiffLoader, JPEGLoader, TIFFImageLoader
from gda.analysis import ScanFileHolder
from gda.analysis import RCPPlotter;

from gda.jython import InterfaceProvider

from Diamond.Objects.Shutter import ShutterDeviceClass

#Introduce the script logger
from Diamond.Utility.ScriptLogger import ScriptLoggerClass;
logger=ScriptLoggerClass();


FILELOADERS={
			'TIF':TIFFImageLoader,
			'TIFF':TIFFImageLoader,
			'JPG':JPEGLoader,
			'JPEG':JPEGLoader,
			}


import __main__ as gdamain

# test = ScanFileContainer()
# test.loadPilatusData("/dls/i16/data/Pilatus/test1556.tif")
# test.plot()
# matrix = test.getImage().doubleMatrix()

#class Pilatus(ScannableMotionBase):
class PilatusPseudoDeviceClass(DetectorBase, ShutterDeviceClass):
	DETECTOR_STATUS_IDLE, DETECTOR_STATUS_BUSY, DETECTOR_STATUS_PAUSED, DETECTOR_STATUS_STANDBY, DETECTOR_STATUS_FAULT, DETECTOR_STATUS_MONITORING = range(6);

	def __init__(self, name, panelName, detectorName, shutterName=None):
		self.setName(name);
		self.setInputNames(['exposure']);
		self.setExtraNames([]);
#		self.setOutputFormat(['%.2f']);
		self.setLevel(7);
		
		self.panel = panelName;
		self.detector = vars(gdamain)[detectorName];

		self.detectorInfo = None;
		self.data = ScanFileHolder()
		self.exposureTime = 0
		self.sum = 0
		self.maxpix = 0

#		self.filePath = None;
#		self.filePrefix = None;
#		self.fileFormat = "%s%s%4.4d.tif";
#		self.fileNumber = self.detector.getFileNumber();
		self.logScale = False;
		self.alive=True;
		
		ShutterDeviceClass.__init__(self, shutterName);


# PseudoDetector Implementation
	def getPosition(self):
		return self.readout();
		
#	def asynchronousMoveTo(self,newExpos):
#		self.setCollectionTime(newExpos)
#		self.collectData();

	def getCollectionTime(self):
		self.exposureTime=self.detector.getCollectionTime();
		return self.exposureTime;

	def setCollectionTime(self, newExpos):
		self.exposureTime = newExpos;
		self.detector.setCollectionTime(self.exposureTime);

	def collectData(self):
		self.openShutter();
		self.detector.collectData();
		return;

	def readout(self):
		self.closeShutter()
		self.fileNumber = self.detector.readout();
		fileName = self.getFullFileName();
		
		if not self.fileExists(fileName, 100):
			logger.simpleLog( "PilatusDetectorPseudoDevice.readout(): File '" + fileName + "' does not exist!" );
			raise Exception("No File Found Error");
		
		if self.alive:
			self.display();
		
		return fileName;

	def getStatus(self):
		return self.detector.getStatus();
	
	def createsOwnFiles(self):
		return True;
	
	def toString(self):
		self.getPosition();
		return "Latest image file: " + self.getFullFileName();
	
	def stop(self):
		self.closeShutter();

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

	def display(self,file=None):
		if file==None:
			file = self.getFullFileName()
#		self.data.loadPilatusData(file)
		self.data.load(PilatusTiffLoader(file));
		dataset = self.data.getAxis(0);

		if self.panel:
			if self.logScale:
				RCPPlotter.imagePlot(self.panel, DatasetMaths.lognorm(dataset)); #For RCP GUI
			else:
				RCPPlotter.imagePlot(self.panel, dataset); #For RCP GUI
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
		self.detector.setFilePrefix(newFilePrefix);

	def getFilePath(self):
		return self.detector.getFilePath();

	def getFilePrefix(self):
		"""Get filename - not the path"""
		return self.detector.getFilePrefix();

	def getFileNumber(self):
		"""Get filenumber"""
		self.fileNumber = self.detector.getFileNumber();
		return self.fileNumber
	
	def getFullFileName(self):
		"""Returns file path of the LAST CREATED image"""
		return self.detector.getFullFileName();

	def setThreshold(self, newGain, newThresholdEnergy):
		self.detector.setThreshold(newGain, newThresholdEnergy);
		return;
	
	def getThreshold(self):
		return self.detector.getThreshold();
	
	def setExposurePeriod(self, newExpp):
		self.detector.setExposurePeriod(newExpp);
		return;

	def getExposurePeriod(self):
		return self.detector.getExposurePeriod();


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

