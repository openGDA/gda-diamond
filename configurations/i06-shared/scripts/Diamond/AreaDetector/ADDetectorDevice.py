from time import sleep, time;
import os;
from java.io import File;

from javax.imageio import ImageIO;
from java.awt.image import BufferedImage


#import java
from math import *


from gda.data import NumTracker
from gda.jython import InterfaceProvider

from gda.device.detector import DetectorBase
from gda.device.detector.areadetector.v17 import NDPluginBase;
from gda.device import Detector

from gda.analysis.datastructure import *
from gda.analysis import *
#from gda.analysis import DataSet
from uk.ac.diamond.scisoft.analysis import SDAPlotter 
from gda.analysis.io import PNGLoader, PNGSaver;



from gov.aps.jca.event import PutEvent;
from gov.aps.jca.event import PutListener;
from gov.aps.jca import CAStatus;
from gov.aps.jca.dbr import DBRType;

import scisoftpy as dnp;

from Diamond.Utility.Threads import BackgroundRunningTask

class ADDetectorDeviceClass(DetectorBase):
	DETECTOR_STATUS_IDLE, DETECTOR_STATUS_BUSY, DETECTOR_STATUS_PAUSED, DETECTOR_STATUS_STANDBY, DETECTOR_STATUS_FAULT, DETECTOR_STATUS_MONITORING = range(6);
	def __init__(self, name, adDetector, panelName="Fleacam"):

		self.setName(name);
		self.detector=adDetector

		self.level = self.detector.getLevel() + 1;

		self.panel = panelName;
		
		self.filePrefix = None;
		self.pathPostfix = None;
		self.fileName=None;
		self.filePath = name+"Image";
		self.fileFormat='%s%s%.5d.tif';
		self.delay = 0;

		self.dataHolder = None;
		self.dataset = None;

		self.width = 1024;
		self.height = 768;
		
		self.exposureTime = 1;

		self.alive = False;
		self.save = True;
		self.logScale = False;
		self.shifting = False;
		self.previewThread = None;
		
		self.stats = False;

		self.previouseImageMode=0;
		self.previouseAcquireStatus=0;

		self.extras=[];
		self.setup();

	def setup(self):
#		self.ndFile=self.detector.getNdFile();
#		self.ndArray=self.detector.getNdArray();
#		self.ndStats=self.detector.getNdStats();
		
		self.setInputNames([]);
		extraNames = ['ExposureTime', 'file'];
		extraNames.extend( self.extras );
		outputFormat = ['%f', '%s'];
		outputFormat.extend( ['%10.4f']*len(self.extras) );

		self.setExtraNames(extraNames);
		self.setOutputFormat(outputFormat);

	def setAlive(self, alive=True):
		self.alive = alive

	def setStats(self, stats=True):
		self.stats = stats;
		
		if self.stats == True:
			self.detector.setComputeCentroid(True);
			self.detector.setComputeStats(True);
			self.extras=['cen_x','cen_y','cen_sx','cen_sy', 'cen_sxy', 'mean','sigma', 'max','min','sum'];
			self.centroid=[None]*5;
			self.statistics=[None]*5;
		else:
			self.extras=[];

		self.setup();
		
	def setAcquirePeriod(self, newap):
		self.detector.getAdBase().setAcquirePeriod(newap)

	def getAcquirePeriod(self):
		return self.detector.getAdBase().getAcquirePeriod_RBV();

# Detector Implementation
	def getCollectionTime(self):
		self.exposureTime=self.detector.getCollectionTime();
		return self.exposureTime;

	def setCollectionTime(self, newExpos):
		self.exposureTime = newExpos;
		self.detector.setCollectionTime(self.exposureTime);
		adBase=self.detector.getAdBase();

		if (adBase.getAcquirePeriod_RBV() < self.exposureTime + 0.1 ):
			adBase.setAcquirePeriod(self.exposureTime + 0.1)
		adBase.setAcquireTime(self.exposureTime);


	def prepareForCollection(self):
		self.backupImageMode();
		self.setNewImagePath()
		self.detector.prepareForCollection();
		self.detector.getAdBase().setImageMode(0);
		self.prepareForSingleShot();
		
	def collectData(self):
		self.detector.collectData();

#	def asynchronousMoveTo(self,newExpos):
#		print "Please use .singleShot(newExposureTime)";
			
	def getStatus(self):
		return self.detector.getStatus();
	
	def readout(self):
#		print "Debug: "+  sys._getframe().f_code.co_name +" is called";

#		self.fileName=self.getFullFileName();
#		print "First attemp: " + self.fileName;
		if self.stats:
			self.getStatistics();
			self.getCentroid();

		sleep(self.delay);

		self.fileName=self.getFullFileName();
#		print "Second attemp: " + self.fileName;
			
		if self.alive:
			self.loadImageFile(self.fileName)
			self.display();
		
		result=[self.exposureTime, self.fileName];

		if self.stats:
			result.extend( self.centroid );
			result.extend( self.statistics );

		return result;

	def endCollection(self):
#		print "Debug: "+  sys._getframe().f_code.co_name +" is called";
		self.enableNdFilePlugin(False, False);
		self.restoreImageMode();

	def stop(self):
		self.stopIt()
		self.endCollection();

	def atCommandFailure(self):
		self.stop();


#General camera operations:
	def display(self,dataset=None):
		if dataset is None:
			dataset=self.dataset;
			
		if dataset is None:
			print "No dataset to display";
			return;

		if self.panel:
			SDAPlotter.imagePlot(self.panel, dataset);
		else:
			print "No panel set to display"
			raise Exception("No panel_name set in %s. Set this or set %s.setAlive(False)" % (self.name, self.name));

	def stopIt(self):
		self.previewThread.stop();
		self.previewThread=None;

	def preview(self, expo, acq):
		if self.previewThread is not None:
			self.stopIt();
			
		self.previewThread=BackgroundRunningTask(self.previewLoop, [expo, acq]);
		self.previewThread.start();

	def previewLoop(self, t):
		newExpos, acquirePeriod=t;
		self.setCollectionTime(newExpos);
		self.prepareForPreview();
		
#		self.prepareForCollection();
#		self.collectData();
		
		while True:
			t0=time();
			self.getCameraData();#To get the dataset
			self.display();
			lt= acquirePeriod - (time()-t0)/1000.;
			if lt >=0:
				sleep(lt);


	def prepareForPreview(self):
		#turn on the continuous viewing mode
		self.detector.prepareForCollection();
		self.detector.getAdBase().setImageMode(2);
		#turn off the NdFile plugin
		self.enableNdFilePlugin(False, False);
		#turn on the NdArray plugin
		self.enableNdArrayPlugin()

		self.detector.getAdBase().startAcquiring();

	def prepareForSingleShot(self):
		ndFile=self.detector.getNdFile();
		ndFile.setNumCapture(1);
		ndFile.setFileWriteMode(0);#Capture Mode: Single

		self.enableNdFilePlugin();

	def prepareForMultiShot(self, numberOfImages):
		ndFile=self.detector.getNdFile();
		self.enableNdFilePlugin();
		ndFile.setNumCapture(numberOfImages);
		ndFile.setFileWriteMode(1);#Capture Mode: Capture
		ndFile.startCapture()

	def singleShot(self, newExpos):
		self.setCollectionTime(newExpos);
		self.prepareForCollection();
		self.collectData();
		sleep(self.exposureTime);
		while self.getStatus() != Detector.IDLE:
			sleep(self.exposureTime/10.0);

		result=self.readout();
		self.endCollection();
		
		return result;

	def multiShot(self, newExpos, numberOfShots):
		self.setCollectionTime(newExpos);
		self.prepareForCollection();
		self.collectData();
		sleep(self.exposureTime);
		while self.getStatus() != Detector.IDLE:
			sleep(self.exposureTime/10.0);

		result=self.readout();
		self.endCollection();
		
		return result;


#AdBase operation
	def getDimensions(self):
		adBase=self.detector.getAdBase();
#		x=adBase.getMaxSizeX_RBV();
#		y=adBase.getMaxSizeY_RBV();
		x=adBase.getArraySizeX_RBV();
		y=adBase.getArraySizeY_RBV();
		z=adBase.getArraySizeZ_RBV();
		
		if x == 0:
			x=adBase.getMaxSizeX_RBV();
		if y == 0:
			y=adBase.getMaxSizeY_RBV();
			
		return x,y,z;
		
#NdArray operations:
	def getCameraData(self):
		adBase=self.detector.getAdBase();
		self.width, self.height, z = self.getDimensions();

		ndArray=self.detector.getNdArray();
		self.dataType=ndArray.getPluginBase().getDataType_RBV();
		
		t0=time();
		if self.dataType==NDPluginBase.UInt8:
#			print "Debug: Fetching UInt8 data started"
			self.rawData=ndArray.getByteArrayData( self.width*self.height )
			if self.shifting: #Need to cast the byte array to unsigned byte array  
				tempDoubleList = [ float(x&0xFF) for x in self.rawData[0:self.width*self.height] ];
			else:
				tempDoubleList = self.rawData[0:self.width*self.height];
		elif NDPluginBase.UInt16:
#			print "Debug: Fetch UInt16 data started"
			self.rawData=ndArray.getShortArrayData( self.width*self.height )
			if self.shifting: #Need to cast the short array to unsigned short array  
				tempDoubleList = [ float(x&0xFFFF) for x in self.rawData[0:self.width*self.height] ];
			else:
				tempDoubleList = self.rawData[0:self.width*self.height];
		else:
			print "Unknown data type"

#		print "Dubug: Fetching data finished within %d seconds" %(time()-t0);

		da = dnp.array(tempDoubleList);
		self.dataset = da.reshape([self.height, self.width]);

		return self.dataset;


	def enableNdArrayPlugin(self, callback=True, blocking=True):
		ndArray=self.detector.getNdArray();
		
		if callback:
			ndArray.getPluginBase().enableCallbacks();
		else:
			ndArray.getPluginBase().disableCallbacks();
		
		ndArray.getPluginBase().setBlockingCallbacks(blocking);

#NdFile operations:		
	def setFile(self, newPathPostfix, newFilePrefix):
		self.pathPostfix = newPathPostfix;
		self.filePrefix = newFilePrefix
		self.setNewImagePath();

	def resetImageNumber(self):
		self.imageNumber=0;#To reset the image number
		ndFile=self.detector.getNdFile();
		ndFile.setFileNumber(0);

	def enableNdFilePlugin(self, callback=True, blocking=True):
		ndFile=self.detector.getNdFile();
		
		if callback:
			ndFile.getPluginBase().enableCallbacks();
		else:
			ndFile.getPluginBase().disableCallbacks();
		
		ndFile.getPluginBase().setBlockingCallbacks(blocking);
			
		
	def setNewImagePath(self):
		"""Set file path and name based on current scan run number"""
		nextNum = NumTracker("tmp").getCurrentFileNumber();
		
		basePath=InterfaceProvider.getPathConstructor().createFromDefaultProperty() + File.separator;
		subDir="%d_%s"%(nextNum, self.pathPostfix); 
		newImagePath = os.path.join(basePath, subDir);

		if not os.path.exists(newImagePath):
			#print "Path does not exist. Create new one."
			os.makedirs(newImagePath);
			self.resetImageNumber();
			
		if not os.path.isdir(newImagePath):
			print "Invalid path";
			return;
				
		self.filePath = newImagePath;
		#print "Image file path set to " + self.filePath;
		
		ndFile=self.detector.getNdFile();
		ndFile.setFilePath(self.filePath);
		ndFile.setFileName(self.filePrefix);
		ndFile.setFileTemplate(self.fileFormat);
		
		ndFile.setAutoIncrement(True);
		ndFile.setAutoSave(True);
		ndFile.setFileFormat(0);#Magic file format depending on the file extension
		return self.filePath;

	def backupImageMode(self):
		self.previouseImageMode=self.detector.getAdBase().getImageMode_RBV();
		self.previouseAcquireStatus = self.detector.getAdBase().getAcquireState();
		self.detector.getAdBase().stopAcquiring()
	
	def restoreImageMode(self):
		self.detector.getAdBase().setImageMode(self.previouseImageMode);
		if self.previouseAcquireStatus:
			self.detector.getAdBase().startAcquiring();

	def getFilePath(self):
		return self.detector.getNdFile().getFilePath_RBV();
#		return self.filePath;

	def getFullFileName(self):
		self.fileName=self.detector.getNdFile().getFullFileName_RBV();
		return self.fileName;

	def loadImageFile(self, fileName):
		if fileName is None:
			fileName=self.fileName;
			
		self.dataHolder=dnp.io.load(fileName);
		self.dataset = self.dataHolder[0];

		return self.dataset;

#NdStats operations:
	def getCentroid(self):
		self.ndStats=self.detector.getNdStats();
		centroidX=self.ndStats.getCentroidX_RBV()
		centroidY=self.ndStats.getCentroidY_RBV()
		centroidSigmaX=self.ndStats.getSigmaX_RBV()
		centroidSigmaY=self.ndStats.getSigmaY_RBV()
		centroidSigmaXY=self.ndStats.getSigmaXY_RBV()
		self.centroid=[centroidX, centroidY, centroidSigmaX, centroidSigmaY, centroidSigmaXY];

		return self.centroid;

	def getStatistics(self):
		self.ndStats=self.detector.getNdStats();
		statMax=self.ndStats.getMaxValue_RBV()
		statMin=self.ndStats.getMinValue_RBV()
		statTotal=self.ndStats.getTotal_RBV()
		statMean=self.ndStats.getMeanValue_RBV()
		statSigma=self.ndStats.getSigma_RBV()
		self.statistics=[statMean, statSigma, statMax, statMin, statTotal];
		
		return self.statistics;


#Usage
#import Diamond.AreaDetector.ADDetectorDevice; reload(Diamond.AreaDetector.ADDetectorDevice)
#from Diamond.AreaDetector.ADDetectorDevice import ADDetectorDeviceClass
#camp = ADDetectorDeviceClass('camp', peemcam_ad, "Plot 1");
#camp.setFile('CampImage', 'camp');
#camp.setStats(True);


