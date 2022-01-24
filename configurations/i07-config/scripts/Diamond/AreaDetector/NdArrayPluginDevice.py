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


class NdArrayPluginDeviceClass(DetectorBase):
	DETECTOR_STATUS_IDLE, DETECTOR_STATUS_BUSY, DETECTOR_STATUS_PAUSED, DETECTOR_STATUS_STANDBY, DETECTOR_STATUS_FAULT, DETECTOR_STATUS_MONITORING = range(6);
	def __init__(self, name, adDetector, panelName="Fleacam"):

		self.setName(name);
		self.detector=adDetector

		self.level = self.detector.getLevel() + 1;

		self.panel = panelName;
		
		self.filePrefix = None;
		self.pathPostfix = None;
		self.fileName=name;
		self.filePath = name+"Image";

		self.dataHolder = None;
		self.rawData = None;
		self.dataset = None;
		self.dataType= None;

		self.width = 1024;
		self.height = 768;
		
		self.exposureTime = 1;

		self.alive = False;
		self.save = True;
		self.logScale = False;

		self.extras=[];
		self.scannableSetup();

	def scannableSetup(self):
		self.setInputNames([]);

		extraNames = ['ExposureTime'];
		extraNames.extend( self.extras );
		outputFormat = ['%f'];
		outputFormat.extend( ['%10.4f']*len(self.extras) );

		if self.save:
			extraNames.insert(1, 'file');
			outputFormat.insert(1, "%s");

		self.setExtraNames(extraNames);
		self.setOutputFormat(outputFormat);

	def setSave(self, save=True):
		self.save = save;
		self.scannableSetup();

	def setAlive(self, alive=True):
		self.alive = alive
		
	def setFile(self, newPathPostfix, newFilePrefix):
		self.pathPostfix = newPathPostfix;
		self.filePrefix = newFilePrefix
		self.setNewImagePath();
		
	def getDataSet(self):
		return self.dataset;

	def setNewImagePath(self):
		"""Set file path and name based on current scan run number"""
		nextNum = NumTracker("tmp").getCurrentFileNumber();
		
		basePath=InterfaceProvider.getPathConstructor().createFromDefaultProperty() + File.separator;
		subDir="%d_%s"%(nextNum, self.pathPostfix); 
		newImagePath = os.path.join(basePath, subDir);

		if not os.path.exists(newImagePath):
			#print "Path does not exist. Create new one."
			os.makedirs(newImagePath);
			self.imageNumber=0;#To reset the image number
			
		if not os.path.isdir(newImagePath):
			print "Invalid path";
			return;
				
		self.filePath = newImagePath;
		#print "Image file path set to " + self.filePath;
		return self.filePath;

	def getFilePath(self):
		return self.filePath;

	def getDimensions(self):
		adBase=self.detector.getAdBase();
		x=adBase.getMaxSizeX_RBV();
		y=adBase.getMaxSizeY_RBV();
#		x=adBase.getArraySizeX_RBV();
#		y=adBase.getArraySizeY_RBV();
		z=adBase.getArraySizeZ_RBV();
		return x,y,z;

	def getCameraData(self):
		adBase=self.detector.getAdBase();
		self.width, self.height, z = self.getDimensions();

		ndArray=self.detector.getNdArray();
		self.dataType=ndArray.getPluginBase().getDataType_RBV();
		
		t0=time();
		if self.dataType==NDPluginBase.UInt8:
#			print "Debug: Fetching UInt8 data started"
			self.rawData=ndArray.getByteArrayData()
			#cast the byte array to unsigned then double array  
			tempDoubleList = [ float(x&0xFF) for x in self.rawData ];
		elif NDPluginBase.UInt16:
#			print "Debug: Fetch UInt16 data started"
			self.rawData=ndArray.getShortArrayData()
#			tempDoubleList = [ float(x&0xFFFF) for x in self.rawData ];
			tempDoubleList = self.rawData;
		else:
			print "Unknown data type"

#		print "Dubug: Fetching data finished within %d seconds" %(time()-t0);

		da = dnp.array(tempDoubleList);
		self.dataset = da.reshape([self.height, self.width]);

		return self.dataset;
	
	def saveImageFile(self, fileName, width=None, height=None, rawData=None):
		if width == None:
			width = self.width;
		if height == None:
			height = self.height;
		if rawData == None:
			rawData = self.rawData;


#		Rend an image
#		Create a buffered image in which to draw
#		bufferedImage =  BufferedImage(width, height, BufferedImage.TYPE_INT_RGB);
#		bufferedImage.setRGB(0, 0, width, height, rawData, 0, width);

		if self.dataType==NDPluginBase.UInt8:
			bufferedImage =  BufferedImage(width, height, BufferedImage.TYPE_BYTE_GRAY);
		elif NDPluginBase.UInt16:
			bufferedImage =  BufferedImage(width, height, BufferedImage.TYPE_USHORT_GRAY);
		else:
			print "Unknown data type"

#		bufferedImage =  BufferedImage(width, height, BufferedImage.TYPE_BYTE_INDEXED);
#		bufferedImage =  BufferedImage(width, height, BufferedImage.TYPE_BYTE_GRAY);
		bufferedImage.getRaster().setDataElements(0, 0, width, height, rawData);

#		Create a graphics contents on the buffered image, draw something and then dispose it
#		g2d = bufferedImage.createGraphics();
#		g2d.setColor(Color.white);
#		g2d.fillRect(0, 0, width, height);
#		g2d.setColor(Color.black);
#		g2d.fillOval(0, 0, width, height);
#		g2d.dispose();
		
#		Save as PNG
		file=File(fileName);
		ImageIO.write(bufferedImage, "png", file);
		return;

	def loadImageFile(self, fileName):
		if fileName != None:#Get data from file directly
#			self.data.load(PNGLoader(fileName));
			self.dataHolder=dnp.io.load(fileName);
#			self.dataset = self.data.getAxis(0);
			self.dataset = self.dataHolder[0];
		if self.alive:
			self.display();

		return self.dataset;

	def postCapture(self):
		if not self.save:
			return;

		runs=NumTracker(self.name);
		nextNum = runs.getCurrentFileNumber() + 1;
		fn="%s%05d.png"%(self.filePrefix, nextNum);
		self.fileName = os.path.join(self.filePath, fn);

#		print "Dubug: Saving file started";
		t0=time();

		#My Own PNG file writer
#		self.saveImageFile(self.fileName);

		#PNG file writer from GDA Analysis package
		dnp.io.save(self.fileName, self.dataset,  autoscale=False);
#		print "Dubug: Saving file finished within %d seconds" %(time()-t0);
	
		runs.incrementNumber();

	def singleShot(self, newExpos):
		self.setCollectionTime(newExpos);
		self.detector.prepareForCollection();
		self.collectData();
		sleep(self.exposureTime);
		while self.getStatus() != Detector.IDLE:
			sleep(self.exposureTime/10.0);

		return self.readout();

	def display(self,dataset=None):
		if dataset is None:
			if self.dataset is None:
				print "No dataset to display";
				return;
			else:
				dataset = self.dataset;

		if self.panel:
			SDAPlotter.imagePlot(self.panel, dataset);
		else:
			print "No panel set to display"
			raise Exception("No panel_name set in %s. Set this or set %s.setAlive(False)" % (self.name,self.name));

# Detector Implementation
	def getCollectionTime(self):
		self.exposureTime=self.detector.getCollectionTime();
		return self.exposureTime;

	def setCollectionTime(self, newExpos):
		self.exposureTime = newExpos;
		self.detector.setCollectionTime(self.exposureTime);
#        adBase=self.detector.getAdBase();

	def prepareForCollection(self):
		if self.save:
			self.setNewImagePath()
		self.detector.prepareForCollection();
		
	def collectData(self):
		self.detector.collectData();
	
	def getStatus(self):
		return self.detector.getStatus();
	
	def createsOwnFiles(self):
		return self.save;
	
	def readout(self):
		self.getCameraData();#To get the dataset
		self.postCapture();#To save file if needed

		if self.alive:
			self.display();
			
		if self.save:
			result=[self.exposureTime, self.fileName];
		else:
			result=[self.exposureTime];
			
		return result;


class NdArrayWithStatPluginDeviceClass(DetectorBase):
	DETECTOR_STATUS_IDLE, DETECTOR_STATUS_BUSY, DETECTOR_STATUS_PAUSED, DETECTOR_STATUS_STANDBY, DETECTOR_STATUS_FAULT, DETECTOR_STATUS_MONITORING = range(6);
	def __init__(self, name, adDetector):

		self.setName(name);
		self.detector=adDetector
		self.level = self.detector.getLevel() + 1;
		self.exposureTime = 0.1;

		self.detector.setComputeCentroid(True);
		self.detector.setComputeStats(True);
		self.ndStats=self.detector.getNdStats();
		
		
		self.centroid=[None]*5;
		self.statistics=[None]*5;

		self.setInputNames([]);
		self.setExtraNames(['exposure', 'cen_x', 'cen_y', 'cen_sx', 'cen_sy', 'cen_sxy', 'mean', 'sigma', 'max', 'min', 'sum']);
		self.setOutputFormat(['%f', '%10.4f', '%10.4f', '%10.4f', '%10.4f', '%10.4f', '%10.4f', '%10.4f', '%10.4f', '%10.4f', '%10.4f']);

	def getCentroid(self):
		centroidX=self.ndStats.getCentroidX_RBV()
		centroidY=self.ndStats.getCentroidY_RBV()
		centroidSigmaX=self.ndStats.getSigmaX_RBV()
		centroidSigmaY=self.ndStats.getSigmaY_RBV()
		centroidSigmaXY=self.ndStats.getSigmaXY_RBV()

		self.centroid=[centroidX, centroidY, centroidSigmaX, centroidSigmaY, centroidSigmaXY];

		return self.centroid;

	def getStatistics(self):
		statMax=self.ndStats.getMaxValue_RBV()
		statMin=self.ndStats.getMinValue_RBV()
		statTotal=self.ndStats.getTotal_RBV()
		statMean=self.ndStats.getMeanValue_RBV()
		statSigma=self.ndStats.getSigma_RBV()
		self.statistics=[statMean, statSigma, statMax, statMin, statTotal];
		
		return self.statistics;
		
# Detector Implementation
	def getCollectionTime(self):
		self.exposureTime=self.detector.getCollectionTime();
		return self.exposureTime;

	def setCollectionTime(self, newExpos):
		self.exposureTime = newExpos;
		self.detector.setCollectionTime(self.exposureTime);
#        adBase=self.detector.getAdBase();

#	def prepareForCollection(self):
#		self.detector.prepareForCollection();
		
	def collectData(self):
		self.detector.collectData();
	
	def getStatus(self):
		return self.detector.getStatus();
#		return Detector.IDLE;
	
	def createsOwnFiles(self):
		return False;

	def readout(self):
		self.getStatistics();
		self.getCentroid();

		result=[self.exposureTime]
		result.extend( self.centroid);
		result.extend( self.statistics);
		
		return result;

	def getPosition(self):
		return self.readout();

	def toFormattedString(self):
		w=self.centroid + self.statistics;
		resultStr=self.getName() + ': ' + '%s, '*len(w) %tuple(w)
		return resultStr.strip(', ');


#Usage
#import Diamond.AreaDetector.NdArrayPluginDevice; reload(Diamond.AreaDetector.NdArrayPluginDevice)
#from Diamond.AreaDetector.NdArrayPluginDevice import NdArrayPluginDeviceClass

#viewerName="Area Detector"
#d7cam = NdArrayPluginDeviceClass('f1', d7cam_ad, viewerName);
#d7cam.setFile('flea', 'd7cam_');


#Usage
#import Diamond.AreaDetector.NdArrayWithStatPluginDeviceClass; reload(Diamond.AreaDetector.NdArrayWithStatPluginDeviceClass)
#from Diamond.AreaDetector.NdArrayWithStatPluginDeviceClass import NdArrayWithStatPluginDeviceClass

#viewerName="Area Detector"
#d7cam = NdArrayWithStatPluginDeviceClass('f1', d7cam_ad, viewerName);
#d7cam.setFile('flea', 'd7cam_');



