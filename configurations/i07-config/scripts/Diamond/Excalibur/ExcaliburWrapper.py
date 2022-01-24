from time import sleep;
import sys, os, stat;

from gda.device import Detector
from gda.device.detector import DetectorBase
from gda.device.detector import NXDetectorDataWithFilepathForSrs

from gda.device.detector.areadetector.v17.ADDriverPilatus import Gain;

from gda.analysis import ScanFileHolder
#from gda.analysis import RCPPlotter;
from uk.ac.diamond.scisoft.analysis import SDAPlotter

from gda.data import ObservablePathConstructor

from gda.observable import IObserver
from gda.data.metadata import MetadataBlaster

from gda.jython import InterfaceProvider
from gda.factory import Finder

import scisoftpy as dnp;

from Diamond.Objects.Shutter import ShutterDeviceClass
from Diamond.PseudoDevices.MetadataHeaderDevice import MetadataHeaderDeviceClass
from Diamond.PseudoDevices.MetadataHeaderDevice import MetadataConsumerClass


#Introduce the script logger
from Diamond.Utility.ScriptLogger import ScriptLoggerClass;
logger=ScriptLoggerClass();

import __main__ as gdamain

class ExcaliburOdinI07(DetectorBase, ShutterDeviceClass, MetadataConsumerClass, IObserver):
	DETECTOR_STATUS_IDLE, DETECTOR_STATUS_BUSY, DETECTOR_STATUS_PAUSED, DETECTOR_STATUS_STANDBY, DETECTOR_STATUS_FAULT, DETECTOR_STATUS_MONITORING = range(6);

	def __init__(self, name, panelName, detectorName, shutterName=None):
		DetectorBase.__init__(self)
		self.setName(name);
		self.setInputNames(['exposure']);
		self.setExtraNames([]);
#		self.setOutputFormat(['%.2f']);

		self.panel = panelName;
		self.detector = vars(gdamain)[detectorName];

		self.detectorInfo = None;
#		self.dataHolder = ScanFileHolder()
		self.dataHolder = None;
		self.sum = 0
		self.maxpix = 0
		self.num_images = 1

#		self.filePath = None;
#		self.filePrefix = None;
#		self.fileFormat = "%s%s%4.4d.tif";
#		self.fileNumber = self.detector.getFileNumber();

		self.fileName = None;
		self.filePrefix = None;
		self.subDir = None;

		self.logScale = False;
		self.alive=True;

		ShutterDeviceClass.__init__(self, shutterName);
		MetadataConsumerClass.__init__(self);

#Observer Implementation
	def update(self, source, arg):
		if isinstance(source, MetadataBlaster):
			print "To update the image file path for %s:" %( self.getName() );
			self.setFile();
		return;


# Detector Implementation
	def getCollectionTime(self):
		return self.detector.getCollectionTime()

	def setCollectionTime(self, newExpos):
		self.detector.setCollectionTime(newExpos);

	def prepareForCollection(self):
		#scaninfo = InterfaceProvider.getCurrentScanInformationHolder().getCurrentScanInformation()
		self.detector.prepareForCollection()
		self.checkPath()

	def collectData(self):
#		print "Debug: "+  sys._getframe().f_code.co_name +" is called";
		self.getMetadata();
		self.openShutter();
		self.detector.collectData();
		return;

	def readout(self):
#		print "Debug: "+  sys._getframe().f_code.co_name +" is called";
		self.closeShutter()

		self.fileName=str(self.detector.controller.getLastFile())

		if not self.fileExists(self.fileName, 100):
			logger.simpleLog( "PilatusDetectorPseudoDevice.readout(): File '" + self.fileName + "' does not exist!" );
			raise Exception("No File Found Error");

		self.createMetadataFiles(str(self.fileName));

		if self.alive:
			self.display();

		return self.fileName;

	def getStatus(self):
		return self.detector.getStatus();

	def createsOwnFiles(self):
		return True

	def endCollection(self):
#		print "Debug: "+  sys._getframe().f_code.co_name +" is called";
		self.closeShutter();


#Scannable Implementation
	def getPosition(self):
		return self.readout();

#	def asynchronousMoveTo(self,newExpos):
#		self.setCollectionTime(newExpos)
#		self.collectData();

#    def atPointEnd(self):
#        self.closeShutter();
#        print "Debug: "+  sys._getframe().f_code.co_name +" is called";

	def atScanEnd(self):
		self.detector.atScanEnd()

	def atScanStart(self):
		self.detector.atScanStart()

	def stop(self):

#		print "Debug: "+  sys._getframe().f_code.co_name +" is called";
		self.closeShutter();
		self.detector.stop()

	def atCommandFailure(self):
#		print "Debug: "+  sys._getframe().f_code.co_name +" is called";
		self.closeShutter();

	def toString(self):
		return "ExcaliburWrapperI07"


## Extra Implementation
	def setAlive(self, newAlive=True):
		self.alive = newAlive;

	def setLogScale(self, newLogScale=True):
		self.logScale = newLogScale;

	def setPanel(self, newPanelName):
		self.panel = newPanelName;

	def getDetectorInfo(self):
		return self.detectorInfo;


	def display(self, file=None):
		if file is None:
			file = self.fileName;

#		self.dataHolder.loadPilatusData(file)
#		self.dataHolder.load(PilatusTiffLoader(file));
#		dataset = self.dataHolder.getAxis(0);
		self.dataHolder=dnp.io.load(file);
		dataset = self.dataHolder['data'][0, :, :]._jdataset()

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
	def getDataDir_Old(self):
		dataDir = InterfaceProvider.getPathConstructor().createFromDefaultProperty();
#		dataDir = InterfaceProvider.getPathConstructor().createFromProperty("gda.pilatus.datadir");
		return dataDir;

	def getDataDir(self):
		opc=ObservablePathConstructor();
		opc.setName("opc");
		opc.setTemplate("${gda.data}/$year$/$visit$/$subdirectory$")
		opc.setGdaMetadata( Finder.find("GDAMetadata") );
		opc.configure();

		dataDir = opc.getPath();
		return dataDir;

	def checkPath(self):
#			self.subDir=str(subDir);
#			self.filePrefix = str(newFilePrefix);

		pilatusDataDir = InterfaceProvider.getPathConstructor().createFromDefaultProperty();

		fullPath = os.path.join(pilatusDataDir, self.subDir);
		if fullPath != self.getFilePath():
			self.setFile();
		return;

	def setFile(self, subDir=None):
		"""Set file path and name"""
		if subDir is not None:
			self.subDir=str(subDir);

		dataDir = InterfaceProvider.getPathConstructor().createFromDefaultProperty();

		fullPath = os.path.join(dataDir, self.subDir);

		if not os.path.exists(fullPath):
			print "Warning: Excalibur image path does not exist. Create new"
			print "OS Command: " + "umask 0002; mkdir -p " + fullPath;
			os.system("umask 0002; mkdir -p " + fullPath);

#		Check the new path created.
		if not os.path.exists(fullPath):
			print "Error: Excalibur image path does not exist and can not be created"
			return;

		print "Note: Current Excalibur image path: " + fullPath;
		self.detector.setFileDirectory(fullPath)

	def getFilePath(self):
		return self.detector.getFileDirectory()


	def getFullFileName(self):
		"""Returns file path of the latest image file"""
		return self.detector.readout()


#Additional DLS Luster fix to deal with delay
	def fileExists(self, fileName, numberOfTry):
		result = False;

		for i in range(numberOfTry):
			if (not os.path.exists(fileName)) or (not os.path.isfile(fileName)):
				if i>1:#To make a note if tried more than twice
					print "File ({}) does not exist on try ".format(fileName) + str(i+1);
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
# 				if fsize!=sizeP100K and fsize!=sizeP2M:
# 					print "Wrong file size: " + str(fsize);
# 					logger.simpleLog( "DetectorAnalyser: File '" + fileName + "' has wrong file size: " + str(fsize) );
# 					sleep(1);
# 					continue;
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

