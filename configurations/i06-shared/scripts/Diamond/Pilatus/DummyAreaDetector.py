import time;
import os;
import sys;

#import java.io.FileNotFoundException

from gda.device import Detector
from gda.device.detector import DetectorBase


#from gda.device.detector import NXDetectorDataWithFilepathForSrs

from gda.jython import InterfaceProvider

from gda.analysis.io import JPEGLoader, TIFFImageLoader, PilatusTiffLoader
import scisoftpy as dnp;

from uk.ac.diamond.scisoft.analysis import SDAPlotter

from java.io import File;


from Diamond.Pilatus.ZipImageProducer import ZipImageProducerClass;

from Diamond.Objects.Shutter import ShutterDeviceClass
from Diamond.PseudoDevices.MetadataHeaderDevice import MetadataConsumerClass

FILELOADERS={
			'TIF':TIFFImageLoader,
			'TIFF':TIFFImageLoader,
			'JPG':JPEGLoader,
			'JPEG':JPEGLoader,
			}

from gda.observable import IObserver
from gda.data.metadata import MetadataBlaster
		
#class DummyAreaDetectorClass(PseudoDetector):
class DummyAreaDetectorClass(DetectorBase, ShutterDeviceClass, MetadataConsumerClass, IObserver):
	def __init__(self, name, panelName, zippedImageSource, fileImageExtension):
		self.setName(name);
#		self.setInputNames([]);
		self.setLevel(7);
		
		self.panel = panelName;
		self.dataHolder = None;
		self.triggerTime = 0;

		self.filePath = None;
		self.filePrefix = None;
		self.subDir = None;
		self.logScale = False;
		self.alive=True;

#		self.imageProducer=ZipImageProducerClass('/scratch/Dev/gdaDev/gda-config/i07/scripts/Diamond/Pilatus/images100K.zip', 'tif');
		self.imageProducer=ZipImageProducerClass(zippedImageSource, fileImageExtension);
		self.fullImageFileName = None;

		MetadataConsumerClass.__init__(self);
		ShutterDeviceClass.__init__(self);

#Observer Implementation
	def update(self, source, arg):
		if isinstance(source, MetadataBlaster):
			print "To update the image file path for %s:" %( self.getName() );
			self.setFile();
		return;
		
# DetectorBase Implementation
	def collectData(self):
#		print "Debug: "+  sys._getframe().f_code.co_name +" is called";
		self.getMetadata()
		self.openShutter()
			
		self.triggerTime = time.time();
		self.fullImageFileName = self.imageProducer.getNextImage();
		return;

	def prepareForCollection(self):
		self.checkPath();

	def readout(self):
#		print "Debug: "+  sys._getframe().f_code.co_name +" is called";
		self.closeShutter();
		self.createMetadataFiles(self.fullImageFileName);
			
		if self.alive:
			self.display();
			
		return self.fullImageFileName;

	def getStatus(self):
		currenttime = time.time();
		
		if currenttime<self.triggerTime + self.getCollectionTime():
			return Detector.BUSY
		else:
			return Detector.IDLE;

	def createsOwnFiles(self):
		return True;
		
	def endCollection(self):
#		print "Debug: "+  sys._getframe().f_code.co_name +" is called";
		return;

# Scannable Implementation
	def stop(self):
#		print "Debug: "+  sys._getframe().f_code.co_name +" is called";
		self.closeShutter();

	def atPointEnd(self):
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

	def singleShot(self, newExpos):
		"""Shot single image with given exposure time""";
		if self.getStatus() != Detector.IDLE:
			print 'Area Detector not available, please try later';
			return;
		
		self.setCollectionTime(newExpos);
		self.collectData();
		while self.getStatus() != Detector.IDLE:
			time.sleep(self.getCollectionTime()/2.0);
		return self.readout();

	def multiShot(self, numberOfImages, newExpos=None):
		"""Shot multiple images with given exposure time""";
		if self.getStatus() != Detector.IDLE:
			print 'Camera not available, please try later';
			return;
		
		if newExpos is not None: # New exposure time given
			exposureTime=newExpos;
			self.setCollectionTime(exposureTime);
			
		exposureTime=self.getCollectionTime();
		fn=[];
		#self.setNumOfImages(numberOfImages);
		for n in range(numberOfImages):
			self.collectData();
			time.sleep(exposureTime);
			while self.getStatus() != Detector.IDLE:
				time.sleep(exposureTime/10.0);
			fn.append( self.readout() );

		return fn;


	def display(self,file=None):
		if file==None:
			file = self.getFullFileName()
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


## Area Detector Implementation
	def checkPath(self):
#			self.subDir=str(subDir);
#			self.filePrefix = str(newFilePrefix);
		imagePath=InterfaceProvider.getPathConstructor().createFromDefaultProperty();
		fullPath = os.path.join(imagePath, self.subDir);
		if fullPath != self.getFilePath():
			self.setFile();
		return;

	def setFile(self, subDir=None, newFilePrefix=None):
		"""Set file path and name"""
		if subDir is not None:
			self.subDir=str(subDir);
		if newFilePrefix is not None:
			self.filePrefix = str(newFilePrefix);
			
#		imagePath = InterfaceProvider.getPathConstructor().createFromProperty("gda.data.scan.datawriter.datadir");
#		imagePath=InterfaceProvider.getPathConstructor().createFromDefaultProperty() + File.separator;
		imagePath=InterfaceProvider.getPathConstructor().createFromDefaultProperty();
		
		fullPath = os.path.join(imagePath, self.subDir);
		print "Image path for %s is set to %s." %(self.getName(), fullPath);
		
		self.imageProducer.setFilePath(fullPath);
		self.imageProducer.setFilePrefix(self.filePrefix);
		
	def getFilePath(self):
		return self.imageProducer.getFilePath();

	def getFilePrefix(self):
		return self.imageProducer.getFilePrefix();

	def getFileNumber(self):
		"""Get filenumber"""
		self.fileNumber = self.imageProducer.getFileNumber();
		return self.fileNumber

	def getFullFileName(self):
		return self.fullImageFileName;

#Usage 
#from Diamond.Pilatus.DummyAreaDetector import DummyAreaDetectorClass
#dummyCamera = DummyAreaDetectorClass("dummyCamera", "PEEM Image");
#dummyCamera.setFile('dummycam', 'dummyCam');
#dummyCamera.setAlive(True);
