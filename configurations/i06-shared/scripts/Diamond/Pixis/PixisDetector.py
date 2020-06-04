import sys, os, stat;
from time import sleep

from gda.device.detector import DetectorBase
from gda.device import Detector
from gda.device.detector import NXDetectorDataWithFilepathForSrs

from gda.epics import CAClient;

#from gda.analysis import RCPPlotter 
from uk.ac.diamond.scisoft.analysis import SDAPlotter;

import scisoftpy as dnp;

import __main__ as gdamain  # @UnresolvedImport

from Diamond.Utility.ScriptLogger import ScriptLoggerClass;
from org.eclipse.january.dataset import DatasetUtils
logger=ScriptLoggerClass();

#The Class for creating a Pixis Detector as Psuedo Device
#the detectorName should be the adDetector that configured in GDA.
class PixisDetectorClass(DetectorBase):
	def __init__(self, name, panelName, detectorName, initPV="BL06I-EA-PIXIS-01:CAM:Initialize"):
		self.setName(name);
		self.setInputNames([name]);
		self.setExtraNames([]);
#		self.Units=[strUnit];
		self.setLevel(7);
		
		self.panel = panelName;
		self.detectorName=detectorName;
		self.initPV=initPV;
		
		self.detector=None;
		self.fileName=None;
		self.dataHolder = None;
		self.ch=None;

		self.exposureTime = 0

		self.logScale = False;
		self.alive=False;
		
		self.connect();
		
	def connect(self):
		try:
			self.ch=CAClient(self.initPV);
			self.ch.configure();
			self.detector =vars(gdamain)[self.detectorName];
			print "PIXIS Camera is connected successfully."
		except:
			exceptionType, exception, traceback=sys.exc_info();
			logger.dump("PIXIS Camera can not be connected ", exceptionType, exception, traceback)
		
		
	#DetectorBase Implementation
	def getCollectionTime(self):
		self.exposureTime=self.detector.getCollectionTime();
		return self.exposureTime;

	def setCollectionTime(self, newExpos):
		self.exposureTime = newExpos;
		self.detector.setCollectionTime(self.exposureTime);

	def prepareForCollection(self):
		self.detector.prepareForCollection();


	def endCollection(self):
		self.detector.endCollection();


	def collectData(self):
		self.initialiseDetector(1);#To press the Initialize Detector button
		
		self.detector.collectData();
		return;
		
	def readout(self):
#		self.getMetadata();
		
		nxDetectorReturn=self.detector.readout();
		
		if isinstance(nxDetectorReturn, NXDetectorDataWithFilepathForSrs):
			self.fileName=nxDetectorReturn.getFilepath();
		else:
			self.fileName=str(nxDetectorReturn);
		
		# Trying to re-enable this results in the  
		errorWhenEnabled=""" 		See /uk.ac.gda.devices.peem/src/gda/device/detector/areadetector/AreaDetectorController.java:339
                                                                                             /dls/i06-1/data/2014/si9122-1/104163_PixisImage/pixis_000001.tif
2014-03-06 12:43:28,340 INFO  [ScriptLogger]  - PilatusDetectorPseudoDevice.readout(): File '/dls/i06-1/data/2014/si9122-1/104159_PixisImagepixis_000000.tif' does not exist! 
2014-03-06 12:43:28,342 INFO  [gda.jython.logger.RedirectableFileLogger]  -  | PilatusDetectorPseudoDevice.readout(): File '/dls/i06-1/data/2014/si9122-1/104159_PixisImagepixis_000000.tif' does not exist!
2014-03-06 12:43:28,353 INFO  [gda.jython.logger.RedirectableFileLogger]  -  | ====================================================================================================
2014-03-06 12:43:28,355 ERROR [gda.scan.ScanBase] java.lang.Exception: during scan collection: DeviceException: Traceback (most recent call last):
  File "/dls_sw/i06-1/software/gda_versions/gda_8.34b/workspace_git/gda-mt.git/configurations/mt-config/scripts/Diamond/Pixis/PixisDetector.py", line 93, in readout
    raise Exception("No File Found Error");
"""
#		if not self.fileExists(self.fileName, 100):
#			logger.simpleLog( "PilatusDetectorPseudoDevice.readout(): File '" + self.fileName + "' does not exist!" );
#			raise Exception("No File Found Error");
#		
#		self.createMetadataFiles( str(self.fileName) );
			
		if self.alive:
			self.display();
		
		return self.fileName;

	def getStatus(self):
		return self.detector.getStatus();

	def createsOwnFiles(self):
		return True;

## Extra Implementation
	def initialiseDetector(self, value=1):
#		self.pv=GDAEpicsInterfaceReader.getPVFromSimplePVType(deviceName);
		if self.ch.isConfigured():
			self.ch.caput(value);
		else:
			self.ch.configure();
			self.ch.caput(value);
			self.ch.clearup();
		

	def fileExists(self, fileName, numberOfTry):
		result = False;
	
		for i in range(numberOfTry):
			if (not os.path.exists(fileName)) or (not os.path.isfile(fileName)):
				print "File '%s' does not exist on try " % fileName + str(i+1);
				logger.simpleLog( "PixisDetectorClass: File does not exist on try " + str(i+1) );
				#check again:
				sleep(1);
				os.system("ls -la " + fileName);
			else:
				#To touch the file will change the timestamps on the directory, which in turn causes the client to refetch the file's attributes. 
				os.system("touch -c " + fileName);
				
				#To check the file size non zero
				fsize = os.stat(fileName)[stat.ST_SIZE];
				print "File exists on try " + str(i+1) + " with size " + str(fsize);
				logger.simpleLog( "Pixis Camera: File '" + fileName + "' exists on try " + str(i+1) + " with size " + str(fsize) );
				sizePixis = 8388782L;
				if fsize!=sizePixis:
					print "Wrong file size: " + str(fsize);
					logger.simpleLog( "PixisDetector: File '" + fileName + "' has wrong file size: " + str(fsize) );
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
					logger.simpleLog( "PixisDetectorClass: There are something wrong on the file system !!!");
		return result;
		
	def setAlive(self, newAlive=True):
		self.alive = newAlive;
		
	def setLogScale(self, newLogScale=True):
		self.logScale = newLogScale;

	def setPanel(self, newPanelName):
		self.panel = newPanelName;
		
	def singleShot(self, newExpos):
		"""Shot single image with given exposure time""";
		if self.getStatus() != Detector.IDLE:
			print 'PIXIS detector not available, please try later';
			return;
		
		self.setCollectionTime(newExpos);
		self.collectData();
		while self.getStatus() != Detector.IDLE:
			sleep(self.exposureTime/2);
		return self.readout();

	def display(self, fileName=None):
		if fileName is None:
			fileName = self.fileName;
			
		self.dataHolder=dnp.io.load(fileName);
		dataset = self.dataHolder[0];

		if self.panel:
			if self.logScale:
				SDAPlotter.imagePlot(self.panel, DatasetUtils.lognorm(dataset)); #For RCP GUI
			else:
				SDAPlotter.imagePlot(self.panel, dataset); #For RCP GUI
		else:
			print "No panel set to display"
			raise Exception("No panel_name set in %s. Set this or set %s.setAlive(False)" % (self.name,self.name));


#Usage:
#import Diamond.Pixis.PixisDetector; reload(Diamond.Pixis.PixisDetector)
#from Diamond.Pixis.PixisDetector import PixisDetectorClass

#ViewerPanelName = "Area Detector"
#pixis = PixisDetectorClass("pixis", ViewerPanelName, adPixis);

