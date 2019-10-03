from time import sleep
import os;
import jarray;

from java import lang
#from java.awt import Color;
from java.awt import Graphics2D;
from java.awt.image import BufferedImage;
#from java.awt.image import RenderedImage;
from java.io import File;
#from java.io import IOException;

from javax.imageio import ImageIO;

import scisoftpy as dnp

#import java
import Jama
from Jama import Matrix
from math import *



from gda.epics import CAClient
from gda.data import NumTracker
from gda.jython import InterfaceProvider

from gda.device.detector import DetectorBase


from gda.analysis.datastructure import *
from gda.analysis import *
#from gda.analysis import DataSet
from gda.analysis import RCPPlotter;
from gda.analysis.io import PNGLoader, PNGSaver;


from gov.aps.jca.event import PutEvent;
from gov.aps.jca.event import PutListener;
from gov.aps.jca import CAStatus;
from gov.aps.jca.dbr import DBRType;

import scisoftpy as dnp;


class EpicsCameraClass(DetectorBase):
	DETECTOR_STATUS_IDLE, DETECTOR_STATUS_BUSY, DETECTOR_STATUS_PAUSED, DETECTOR_STATUS_STANDBY, DETECTOR_STATUS_FAULT, DETECTOR_STATUS_MONITORING = range(6);

	#CA Put Callback listener that handles the callback event
	class CaputCallbackListenerClass(PutListener):
		def __init__ (self, camera):
			self.camera = camera;
			
		def putCompleted(self, event):
			if event.getStatus() != CAStatus.NORMAL:
				print 'Camera trigger failed!'
				print 'Failed source: ' + event.getSource().getName();
				print 'Failed stuatus: ' + event.getStatus();
			else:
				#print 'The camera is called back';
				self.camera.cameraStatus = EpicsCameraClass.DETECTOR_STATUS_IDLE;
			return;

		def getStatus(self):
				return self.camera.cameraStatus;
			
	def __init__(self, name, pvRootCamera, panelName="Fleacam"):
		self.setName(name);
		self.setInputNames([]);
		self.setLevel(7);
		
		self.pvRoot = pvRootCamera;
		self.setupEpics(pvRootCamera);

		self.panel = panelName;
		
		self.fileName=None;
		self.filePath = None;
		self.filePrefix = None;
		
#		self.data = ScanFileHolder();
		self.dataHolder = None;
		self.rawData = None;
		self.dataset = None;
		self.width = 1024;
		self.height = 768;
#		self.rawDataArray = [[0. for x in range(self.width)] for y in range(self.height)];
#		self.rawDataArray = [[x+y*self.width for x in range(self.width)] for y in range(self.height)];
		
		self.exposureTime = 1;
		self.cameraStatus=EpicsCameraClass.DETECTOR_STATUS_IDLE;
		
		self.putListener = EpicsCameraClass.CaputCallbackListenerClass(self);
#		self.putListener = EpicsCameraClass.CaputCallbackListenerClass();

		self.alive = True;
		self.save = False;
		self.logScale = False;
		
		

	def __del__(self):
		self.cleanChannel(self.frameData);
		self.cleanChannel(self.frameWidth);
		self.cleanChannel(self.frameHeight);
		self.cleanChannel(self.capture);
		self.cleanChannel(self.enableStream);
		self.cleanChannel(self.enableCapture);
	
	def setupEpics(self, pvRootCamera):
		self.frameData  =CAClient(pvRootCamera + ':DATA'); self.configChannel(self.frameData);
		self.frameWidth =CAClient(pvRootCamera + ':WIDTH'); self.configChannel(self.frameWidth);
		self.frameHeight=CAClient(pvRootCamera + ':HEIGHT'); self.configChannel(self.frameHeight);

		self.capture = CAClient(pvRootCamera + ':SNAPSHOT'); self.configChannel(self.capture);

		self.enableStream  = CAClient(pvRootCamera + ':ENABLE'); self.configChannel(self.enableStream);
		self.enableCapture = CAClient(pvRootCamera + ':DISAIMG1'); self.configChannel(self.enableCapture);
		
	def configChannel(self, channel):
		if not channel.isConfigured():
			channel.configure();

	def cleanChannel(self, channel):
		if channel.isConfigured():
			channel.clearup();

		
#TODO: Don need this command once the EPICS bugs fixed
	def turnOn(self):
		cmd = "caput " + self.pvRoot + ":GETSNAP1.VAL 1";
		print cmd;
		os.system(cmd);
		cmd = "caput " + self.pvRoot + ":GETSNAP1.OUTB '"+ self.pvRoot + ":CHKACQ.PROC CA'"
		print cmd;
		os.system(cmd);

	def setAlive(self, alive=True):
		self.alive = alive

	def setSave(self, save=True):
		self.save = save;

	def setFile(self, subDir, newFilePrefix):
		"""Set file path and name"""
#		imagePath = InterfaceProvider.getPathConstructor().createFromProperty("gda.data.scan.datawriter.datadir");
		imagePath=InterfaceProvider.getPathConstructor().createFromDefaultProperty() + File.separator;
		newFilePath = os.path.join(imagePath, subDir);

		if not os.path.exists(newFilePath):
			print "Path does not exist. Create new one."
			os.makedirs(newFilePath);
			
		if not os.path.isdir(newFilePath):
			print "Invalid path";
			return;
				
		self.filePath = newFilePath;
		self.filePrefix = newFilePrefix
		print "Image file path set to " + self.filePath;
		
	def getFilePath(self):
		return self.filePath;

	def getFilePrefix(self):
		return self.filePrefix;


	def getWidth(self):
		self.width = int(float(self.frameWidth.caget()));
		return self.width;
	
	def getHeight(self):
		self.height = int(float(self.frameHeight.caget()));
		return self.height;

	def getCameraData(self):
#		self.rawData = self.frameData.getController().cagetByteArray(self.frameData.getChannel());
		self.width = int(float(self.frameWidth.caget()));
		self.height = int(float(self.frameHeight.caget()));
		self.rawData = self.frameData.cagetArrayByte();

		#cast the byte array to double array for dataset 
		tempDoubleList = [float(x) for x in self.rawData];

#		self.dataset=DataSet.array(self.frameData.cagetArrayDouble());
		self.dataset = dnp.array(tempDoubleList)
		self.dataset.shape = [self.height, self.width]
#		self.data = ScanFileHolder();
#		self.data.addDataSet(self.getName(), self.dataset);

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

		bufferedImage =  BufferedImage(width, height, BufferedImage.TYPE_BYTE_INDEXED);
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

	def trigger(self, newExpos):
#TODO: Maybe not needed once EPICS bugs fixed:
		#Disable the stream (Stream OFF)
		self.enableStream.caput(0);
		#To 'arm' the feature:
		self.enableCapture.caput(0);
		sleep(0.1);

#		Trigger the camera without caput callback
#		self.capture.caput(1);
#		self.cameraStatus = EpicsCameraClass.DETECTOR_STATUS_IDLE;


#		Trigger the camera with caput callback
		self.capture.getController().caput(self.capture.getChannel(), 1, self.putListener);
		self.cameraStatus = EpicsCameraClass.DETECTOR_STATUS_BUSY;
		
#TODO: remove the fake callback once its implemented by controls:
#		self.fakeCallback();

	def fakeCallback(self, occurs=1):
		fakeStatus = CAStatus.NORMAL;
		fakeEvent = PutEvent(self.capture.getChannel(), DBRType.ENUM, occurs, fakeStatus);
		self.putListener.putCompleted(fakeEvent);

	def postCapture(self):
		if not self.save:
			return;
		
		runs=NumTracker(self.name);
		nextNum = NumTracker(self.name).getCurrentFileNumber() + 1;

		self.fileName = os.path.join(self.filePath, self.filePrefix+str(nextNum)+".png");

#		print "New File name is: ----------->" + self.fileName;
		#My Own PNG file writer
#		self.saveImageFile(self.fileName);

		#PNG file writer from GDA Analysis package
#		self.data.setDataSet(self.getName(), self.dataset);
#		self.data.save(PNGSaver(self.fileName));
		dnp.io.save(self.fileName, self.dataset);
	
		runs.incrementNumber();


	#PseudoDetector Implementation
	def getPosition(self):
		return self.readout();
		
	def asynchronousMoveTo(self,newExpos):
		self.setCollectionTime(newExpos)
		self.collectData();

#	def moveTo(self, newPos):
#		self.asynchronousMoveTo(newPos);
#		while self.isBusy():
#			sleep(5);

#	def waitWhileBusy(self):
#		while self.isBusy():
#			sleep(5);
#		return;

	def getCollectionTime(self):
		return self.exposureTime;

	def setCollectionTime(self, newExpos):
		self.exposureTime = newExpos;

	def collectData(self):
		self.trigger(self.exposureTime);
		while self.getStatus() != EpicsCameraClass.DETECTOR_STATUS_IDLE:
			sleep(0.1);
			
		self.getCameraData();
		self.postCapture();
		return;
	
	def readout(self):
		if self.alive:
			self.display();
		if self.save:
			return self.fileName;
		else:
			return self.dataset;

	def getStatus(self):
		return self.cameraStatus;

	def createsOwnFiles(self):
		return self.save;
		
	
	def toString(self):
#		self.getPosition();
		if self.fileName == None:
			result = "No image file saved."
		else:
			result =  "Latest image file saved as: " + self.fileName;

		return result;
	

	def singleShot(self, newExpos):
		self.setCollectionTime(newExpos);
		self.collectData();
		self.readout();

	def display(self,dataset=None):
		if dataset is None:
			if self.dataset is None:
				print "No dataset to display";
				return;
			else:
				dataset = self.dataset;

		if self.panel:
			RCPPlotter.imagePlot(self.panel, dataset);
		else:
			print "No panel set to display"
			raise Exception("No panel_name set in %s. Set this or set %s.setAlive(False)" % (self.name,self.name));


#Example
#pvRootCamera04='BL07I-DI-PHDGN-04:CAM';
#viewerName="Area Detector"
#cam04 = EpicsCameraClass('cam04', pvRootCamera04, viewerName);

