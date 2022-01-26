from time import sleep
import os, stat, time;



from gda.factory import Finder
from gda.device.detector import DetectorBase
from gda.device.detector.uviewnew.UViewController.ImageFile import ImageFormat
from gda.device.detector.uviewnew.UViewController.ImageFile import ImageContentsType
from gda.device.detector.uviewnew.UViewImageDetector import TriggerMode
#import java.io.FileNotFoundException
from gda.configuration.properties import LocalProperties
from gda.device import Detector


from gda.analysis.io import JPEGLoader, TIFFImageLoader, PNGLoader
from gda.analysis import ScanFileHolder
from gda.analysis.functions.dataset import MakeMask;
from gda.jython import InterfaceProvider

from gda.analysis import DataSet;
from gda.analysis.utils import DatasetMaths;

from gda.analysis import RCPPlotter;

import __main__ as gdamain

from gda.data import NumTracker



#The Class for creating a PEEM UView Detector as Psuedo Device
#For PEEM UView in I06 only.
class UViewDetectorClass(DetectorBase):
	DETECTOR_STATUS_IDLE, DETECTOR_STATUS_BUSY, DETECTOR_STATUS_PAUSED, DETECTOR_STATUS_STANDBY, DETECTOR_STATUS_FAULT, DETECTOR_STATUS_MONITORING = range(6);
	ImageFileLoaders={  'TIF' : TIFFImageLoader,
						'TIFF': TIFFImageLoader,
						'JPG' : JPEGLoader,
						'JPEG': JPEGLoader,
						'PNG' : PNGLoader };

	def __init__(self, name, panelName, detector):
		self.setName(name);
		self.setInputNames([name]);
		self.setExtraNames([]);
#		self.Units=[strUnit];
		self.setLevel(7);

		self.panel = panelName;
		self.detector = detector;
		self.scanNumberTracker = NumTracker("tmp");

		self.fileName=None;
		self.data = ScanFileHolder()
		self.exposureTime = 0

		self.logScale = False;
		self.alive=True;

#		To setup the image folder according to I06 requirement
		self.scanImageDirectory();
		self.fastMode=False;
		self.protection=True;
#		self.protectCamera();

		self.verbose = False

	#DetectorBase Implementation
	def getPosition(self):
		return self.readout();

	def asynchronousMoveTo(self,newPos):
		self.setCollectionTime(newPos);
		self.collectData();

	def getCollectionTime(self):
		self.exposureTime=self.detector.getCollectionTime();
		return self.exposureTime;

	def setCollectionTime(self, newExpos):
		self.exposureTime = newExpos;
		self.detector.setCollectionTime(self.exposureTime);

	def collectData(self):
		#self.detector.setCollectionTime(self.exposureTime)
		self.detector.collectData();
		return;

	def prepareForCollection(self):
		#To put camera in the "camera mode"
		self.detector.setCameraInProgress(False);
		self.detector.prepareForCollection();

	def endCollection(self):
#		self.detector.endCollection();
		if self.protection:
			self.protectCamera();
		return;

	def readout(self):
		self.fileName  = self.detector.readout();
		if self.alive:
			self.display();
		return self.fileName;

	def getStatus(self):
		return self.detector.getStatus();

	def createsOwnFiles(self):
		return True;

	def toString(self):
		self.getPosition();
		return "Latest image file: " + self.getFullFileName();

	def isBusy(self):
		return self.detector.getStatus() == Detector.BUSY

## Extra Implementation

	def setFileFormat(self, fileExt, contents=2):
		'''
		fileExtension: 	dat: Raw data uncompressed
			 			png: PNG compressed
			 			tiff: TIFF compressed
			 			bmp: BMP uncompressed
			 			jpg: JPG compressed
			 			tif: TIFF uncompressed
		imagecontents: 	0: RGB 8+8+8 bits x,y,z, as seen on screen
			 			1: RGB 8+8+8 bits,x,y raw, z as seen on screen
			 			2: RAW 16 bits graylevel x, y, z raw data
		'''
		self.detector.setFileFormat(fileExt, contents);

	def setImageAverage(self, averageParameter):
		'''
		 averageParameter:	-1: Sliding average. Current does NOT work!
		 					0: No average
		 					1 ~ 99: Number of frames to be averaged
		'''
		self.detector.setImageAverageNumber(averageParameter);

	def getImageAverage(self):
		iv=self.detector.getImageAverageNumber();
		return iv;

	def protectCamera(self):
		#self.detector.setCollectionTime(0.1);
		self.detector.setCameraInProgress(True);
		if self.verbose:
			print "Camera is set to 'Recorder Mode' for protection.";
		return;


	def setAlive(self, newAlive=True):
		self.alive = newAlive;

	def setLogScale(self, newLogScale=True):
		self.logScale = newLogScale;

	def setPanel(self, newPanelName):
		self.panel = newPanelName;

	def getDetectorInfo(self):
		return self.detectorInfo;

	def singleFastShot(self, newExpos=None):
		if newExpos is not None: # New exposure time given
			self.exposureTime = newExpos;
			self.setCollectionTime(newExpos);
		return self.detector.shotSingleImage();


	def singleShot(self, newExpos=None):
		"""Shot single image with given exposure time""";

		#To put camera in the "camera mode"
		self.detector.setCameraInProgress(False);

		if self.getStatus() != Detector.IDLE:
			print 'Camera not available, please try later';
			return;

		if newExpos is not None: # New exposure time given
			self.exposureTime = newExpos;

		self.setCollectionTime(self.exposureTime);

		self.detector.setCameraSequentialMode(True);
		#self.setNumOfImages(1);
		self.collectData();

		sleep(self.exposureTime);
		while self.getStatus() != Detector.IDLE:
			sleep(self.exposureTime/10.0);

		if self.protection:
			self.protectCamera();

		return self.readout();

	def multiShot(self, numberOfImages, newExpos=None, newDir=True):
		"""Shot multiple images with given exposure time""";

		#To put camera in the "camera mode"
		self.detector.setCameraInProgress(False);

		if self.getStatus() != Detector.IDLE:
			print 'Camera not available, please try later';
			return;

		if newExpos is not None: # New exposure time given
			self.exposureTime = newExpos;

		self.setCollectionTime(self.exposureTime);

		if newDir:
			self.newImageDirectory();
			self.scanImageDirectory();
		else:
			self.detector.setCameraSequentialMode(True);


		temp=self.alive;
		self.alive=False;#To turn off the display

		if self.fastMode:
			fn=self.multiFastShot(numberOfImages);
		else:
			fn=self.multiSafeShot(numberOfImages);

		self.alive=temp; #To restoru the display setting

		if self.protection:
			self.protectCamera();

		return fn;

	def multiSafeShot(self, numberOfImages):
		fn=[];
		#self.setNumOfImages(numberOfImages);
		for n in range(numberOfImages):
			self.collectData();
			sleep(self.exposureTime);
			while self.getStatus() != Detector.IDLE:
				sleep(self.exposureTime/10.0);
			fn.append( self.readout() );

		return fn;

	def multiFastShot(self, numberOfImages):
		fn=[];
		#To take the first image
		self.collectData()
		sleep(self.exposureTime + 0.15);
		i=0;
		while i<numberOfImages-1:
			self.collectData();#To trigger a new acquisition
			t0=time.time();
			fn.append( self.readout() );#To save the previous picture
			t1=time.time();
			td=t1-t0;
			if td < self.exposureTime+0.15:#To wait the exposure time, plus a 150ms delay?
				sleep(self.exposureTime+0.15-td);
			i+=1;

		fn.append( self.readout() );#To save the last previous triggered picture
		return fn;

	def display(self,file=None):
		if file==None:
			file = self.getFullFileName()

		fileLoader = UViewDetectorClass.ImageFileLoaders[os.path.splitext(file)[-1].split('.')[-1].upper()];

		self.data.load( fileLoader(file) );

		dataset = self.data.getAxis(0);

		if self.panel:
			if self.logScale:
				RCPPlotter.imagePlot(self.panel, DatasetMaths.lognorm(dataset)); #For RCP GUI
			else:
				RCPPlotter.imagePlot(self.panel, dataset); #For RCP GUI
		else:
			print "No panel set to display"
			raise Exception("No panel_name set in %s. Set this or set %s.setAlive(False)" % (self.name,self.name));


	def setNumOfImages(self, number):
#		self.detector.setNumOfImages(number);
		return;

	def getNumOfImages(self):
		return 1
#		return self.detector.getNumOfImages();

#	To use the directory with scan number to save image, like what scan command does.
	def scanImageDirectory(self):
		#increase the scan number for one
		self.scanNumberTracker.incrementNumber();
		self.prepareForCollection();

#	To create a new directory following the PEEM image directory rules
	def newImageDirectory(self, newDir=None):
		if newDir is not None:
			self.detector.setImageDir(newDir);
		self.detector.prepare();

	def getFullFileName(self):
		"""Returns file path of the LAST CREATED image"""
		return self.fileName;
#		return self.detector.getFullFileName();


#The Class for creating a UView Region Of Interests Detector as Psuedo Detector
class UViewDetectorRoiClass(DetectorBase):
	def __init__(self, name, roi):
		self.setName(name);
		self.setInputNames([name]);
		self.setExtraNames([]);
#		self.Units=[strUnit];
		self.setLevel(7);
		self.roi = roi;
		self.cacheExistingValue=False
	#DetectorBase Implementation
#	def getPosition(self):
#		return self.readout();
	def atScanStart(self):
		self.cacheExistingValue=self.roi.getUViewImageDetector().isROIActive(self.roi.getName())
		if not self.cacheExistingValue:
			#ensure ROI is activated
			self.roi.getUViewImageDetector().activateROI(self.roi.getName())
			
	def atScanEnd(self):
		#set the original ROI state back
		if self.cacheExistingValue != self.roi.getUViewImageDetector().isROIActive(self.roi.getName()):
			if self.cacheExistingValue:
				self.roi.getUViewImageDetector().activateROI(self.roi.getName())
			else:
				self.roi.getUViewImageDetector().deactivateROI(self.roi.getName())
			
	def asynchronousMoveTo(self,newPos):
		self.collectData();

	def collectData(self):
		#self.roi.collectData();
		#do nothing - ROI should not cause the camera to take a new image when called via scan
		#may uncomment in future and move the "do nothing" step to lower down
		pass

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

class UViewDetectorClassNew( UViewDetectorClass ):
	_discards = 0
	def setFileFormat(self, fileExt, contents=2):
		'''
		fileExtension: 	dat: Raw data uncompressed
						png: PNG compressed
						tiff: TIFF compressed
						bmp: BMP uncompressed
						jpg: JPG compressed
						tiff16: TIFF uncompressed
		imagecontents: 	0: RGB 8+8+8 bits x,y,z, as seen on screen
						1: RGB 8+8+8 bits,x,y raw, z as seen on screen
						2: RAW 16 bits graylevel x, y, z raw data
		'''
		enumFileExt = ImageFormat.TIFF_UNCOMPRESSED
		fileExtLower = fileExt.lower()
		if fileExtLower == "dat":
			enumFileExt = ImageFormat.DAT
		elif fileExtLower == "png":
			enumFileExt = ImageFormat.PNG
		elif fileExtLower == "tiff" or fileExtLower == "tif":
			enumFileExt = ImageFormat.TIFF
		elif fileExtLower == "bmp":
			enumFileExt = ImageFormat.BMP
		elif fileExtLower == "jpg" or fileExtLower == "jpeg":
			enumFileExt = ImageFormat.JPG
		elif fileExtLower == "tiff16" or fileExtLower == "tif16":
			enumFileExt = ImageFormat.TIFF_UNCOMPRESSED

		enumContents = ImageContentsType.RGB_XYZ
		if contents == 1:
			enumContents = ImageContentsType.RGB_XYZ_RAW
		if contents == 2:
			enumContents = ImageContentsType.GRAYLEVEL16
		self.detector.setFileFormat(enumFileExt, enumContents);

	def collectData(self):
		if self._discards < 0:
			#self.getCollectionTime()
			self.setCollectionTime( self.exposureTime )
			self.detector.collectData()
			return
		for x in xrange(0, self._discards):
			self.detector.collectData()
			while self.isBusy():
				sleep(0.1)
		self.detector.collectData()

	def atScanStart(self):
		self.detector.setPixelClock(10)
		self.detector.setCameraADC(1)
		averaging = self.detector.getImageAverageNumber()
		#if sliding average, set to no average
		if averaging == 1:
			self.detector.setImageAverageNumber(0)
			averaging = 0
		triggerMode = TriggerMode.SOFT if averaging == 0 else TriggerMode.AUTO
		self.detector.setTriggerMode( triggerMode )

	def atScanEnd(self):
		self.detector.setTriggerMode( TriggerMode.AUTO )
		self.detector.setCameraADC(2)

	def reconnect(self):
		self.detector.reconnect()

	def setPixelClock(self, MHz):
		self.detector.setPixelClock( MHz )

	def setToSoft(self):
		self.detector.setTriggerMode( TriggerMode.SOFT )
	
	def setToAuto(self):
		self.detector.setTriggerMode( TriggerMode.AUTO )
