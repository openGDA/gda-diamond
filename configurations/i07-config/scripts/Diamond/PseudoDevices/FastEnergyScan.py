
from time import sleep, ctime;
#import time;
import sys;
import jarray;

#from gov.aps.jca.event import PutEvent;
from gov.aps.jca.event import PutListener;
from gov.aps.jca import CAStatus;

from gda.device.scannable import ScannableMotionBase;
#from gda.device.MotorStatus import READY, BUSY, FAULT;

#from gda.analysis import DataSet;
from gda.epics import CAClient;

from gda.scan import PointsScan;
from gda.factory import Finder;

from Diamond.PseudoDevices.FileFilter import SrsFileFilterClass;
from Diamond.Utility.ScriptLogger import ScriptLoggerClass;
logger=ScriptLoggerClass();

from gda.jython import ScriptBase

import scisoftpy as dnp

class FastEnergyScanControlClass(object):
	""" """
	#CA Put Callback listener that handles the callback event
	class CaputCallbackListenerClass(PutListener):
		def __init__ (self, device):
			self.device = device;
			
		def putCompleted(self, event):
			if event.getStatus() != CAStatus.NORMAL:
				logger.simpleLog('Motor move failed!');
				logger.simpleLog('Failed source: ' + event.getSource().getName());
			else:
				if self.device.isScanAborted():
					logger.simpleLog('Epics Scan aborted. The FastEnergyScanControlClass calls back successfully');
				else:
					logger.logger.debug('FastEnergyScanControlClass.CaputCallbackListenerClass.putCompleted:Epics Scan finished. The FastEnergyScanControlClass calls back successfully. Delaying...');
					sleep(1);
					self.device.fixDataHead();
					logger.logger.debug('FastEnergyScanControlClass.CaputCallbackListenerClass.putCompleted:... Data Head fixed.');
			self.device.isCalled = True;
			return;


	FASTSCAN_MODE = range(3);
	FASTSCAN_MODE_EPICS_STRING = ["Fixed", "Const velocity", "Slaved"];
	FASTSCAN_MODE_GDA_STRING  = ['fixid', 'cvid', 'slaveid'];

	
	FASTSCAN_STATUS = range(10);
	FASTSCAN_STATUS_STRING = ["Scan complete", "Scan aborted", "Moving PGM to midpoint", 
							"Calculating parameters", "Moving IDD and PGM to start position", 
							"Scan ready", "Starting scan move", "Scanning", "Scan complete", "Idle"];
	#Total 6 status from Epics, plus internal Idle status
	#	"Scan complete"
	#	"Scan aborted"
	#	"Moving PGM to midpoint"
	#	"Calculating parameters"
	#	"Moving IDD and PGM to start position"
	#	"Scan ready"
	#	"Starting scan move"
	#	"Scanning"
	#	"Scan complete"
	#	"Idle"

	def __init__(self, name, rootPV):
		self.name = name;
		self.setupEpics(rootPV);
		
		self.startEnergy=600;
		self.endEnergy=700;

		self.scanStatus='Idle';
		
		self.putListener = FastEnergyScanControlClass.CaputCallbackListenerClass(self);
		self.isCalled = True;

	def __del__(self):
		self.cleanChannel(self.chScanReady01);
		self.cleanChannel(self.chScanReady02);
		self.cleanChannel(self.chScanReady03);
		self.cleanChannel(self.chScanReady04);

		self.cleanChannel(self.chScanReady);

		self.cleanChannel(self.chStartEnergy);
		self.cleanChannel(self.chEndEnergy);
		self.cleanChannel(self.chScanTime);
		self.cleanChannel(self.chNumberOfPoints);

		self.cleanChannel(self.chIdMove);
		self.cleanChannel(self.chBuild);
		self.cleanChannel(self.chBuildStatus);
		self.cleanChannel(self.chExecute);
		self.cleanChannel(self.chStop);
		self.cleanChannel(self.chStatus);
		
		self.cleanChannel(self.chHead);

		self.cleanChannel(self.chVelocityStatus);

		self.cleanChannel(self.chPGMStatus);

	def setupEpics(self, rootPV):
#		Epics PVs for checking fast scan readiness:
		self.chScanReady01=CAClient(rootPV + ":PGM:HOME.RVAL");  self.configChannel(self.chScanReady01);
		self.chScanReady02=CAClient(rootPV + ":PGM:MODE.RVAL");  self.configChannel(self.chScanReady02);
		self.chScanReady03=CAClient(rootPV + ":ID:ENABLE.RVAL"); self.configChannel(self.chScanReady03);
		self.chScanReady04=CAClient(rootPV + ":DATA:OK.RVAL");   self.configChannel(self.chScanReady04);

#		New Epics PV for checking fast scan readiness, this should be used to replace the above four pvs:
		self.chScanReady=CAClient(rootPV + ":STATUS");  self.configChannel(self.chScanReady);
		
#		Epics PVs for fast scan setup:
		self.chStartEnergy=CAClient(rootPV + ":EV:START"); self.configChannel(self.chStartEnergy);
		self.chEndEnergy=CAClient(rootPV + ":EV:FINISH"); self.configChannel(self.chEndEnergy);
		self.chScanTime=CAClient(rootPV + ":TIME"); self.configChannel(self.chScanTime);
		self.chNumberOfPoints=CAClient(rootPV + ":NPULSES"); self.configChannel(self.chNumberOfPoints);
		
#		Epics PVs for fast scan control and status:
		self.chIdMode=CAClient(rootPV + ":IDMODE"); self.configChannel(self.chIdMode);
		self.chBuild=CAClient(rootPV + ":BUILD"); self.configChannel(self.chBuild);

		self.chBuildStatus=CAClient(rootPV + ":BUILDSTATUS"); self.configChannel(self.chBuildStatus);

		self.chExecute=CAClient(rootPV + ":START"); self.configChannel(self.chExecute);
		self.chStop=CAClient(rootPV + ":STOP");self.configChannel(self.chStop);
		self.chStatus=CAClient(rootPV + ":RUN:STATE"); self.configChannel(self.chStatus);

		#Epics PV for the Number of elements available
		self.chHead=CAClient(rootPV + ":ELEMENTCOUNTER");  self.configChannel(self.chHead);

		self.chVelocityStatus=CAClient("BL06I-OP-IDD-01:SET:VEL.STAT"); self.configChannel(self.chVelocityStatus);
		
		#To check the PGM is not stucked
		self.chPGMStatus=CAClient("BL06I-OP-PGM-01:ENERGY.DMOV"); self.configChannel(self.chPGMStatus);
		
	def configChannel(self, channel):
		if not channel.isConfigured():
			channel.configure();

	def cleanChannel(self, channel):
		if channel.isConfigured():
			channel.clearup();

	def fixPGM(self):
			pgminit();

	#To check the PGM is not used or stucked
	def checkPGM(self):
		dmov = int(float(self.chPGMStatus.caget()));
		
		if (dmov == 0): #stucked
			self.fixPGM();
			dmov = int(float(self.chPGMStatus.caget()));

		#return True if DMOV == 1
		return (dmov == 1);

	#To check the PGM and ID motors are ready for the fast scan
	def checkMotorReady(self):
#		c1= int(float(self.chScanReady01.caget()));
#		c2= int(float(self.chScanReady02.caget()));
#		c3= int(float(self.chScanReady03.caget()));
#		c4= int(float(self.chScanReady04.caget()));
#		return (c1 == 0 and c2 == 0 and c3 == 0 and c4 == 0);
		
		c= int(float(self.chScanReady.caget()));
		return (c == 0);


	def setEnergyRange(self, startEnergy, endEnergy):
		self.startEnergy=startEnergy;
		self.endEnergy=endEnergy;
		self.chStartEnergy.caput(startEnergy);
		self.chEndEnergy.caput(endEnergy);

	def getEnergyRange(self, startEnergy, endEnergy):
		return [self.startEnergy, self.endEnergy];

	def setTime(self, scanTime, pointTime):
		numberOfPoints = scanTime/pointTime;
		self.chScanTime.caput(scanTime)
		self.chNumberOfPoints.caput(numberOfPoints)

	def getNumberOfPoint(self):
		return int( float(self.chNumberOfPoints.caget()) );
	
	def getVelocityStatus(self):
		return self.chVelocityStatus.caget();
		
	
	def getDataHead(self):
		head = int(float(self.chHead.caget()));
		return head;
	
	def fixDataHead(self):
		head = self.getDataHead();
		numberOfPoint = self.getNumberOfPoint();
		
		if head >= numberOfPoint:
			logger.logger.debug("Enough points generated by the scan.");
		else:
			logger.simpleLog("Not enough points generated by the scan. Fix is needed to finished the scan.");
			self.chHead.caput(numberOfPoint);


	#trigger the scan
	def startScan(self):
#		self.chExecute.caput(1);
		#trigger the scan and setup the caput callback listener for checking
		self.isCalled = False;
		self.chExecute.getController().caput(self.chExecute.getChannel(), 1, self.putListener);

	#Abort the scan
	def abortScan(self):
		self.chStop.caput(1);
#		self.fixPGM();

	#set the ID mode
	def setIDMode(self, mode):
		self.chIdMode.caput(mode) #select the ID Mode 

	#get the ID mode
	def getIDMode(self):
		idmode=self.chIdMode.caget();
		return int(float(idmode));
	

	#trigger the scan
	def buildScan(self, timeout=None):
		if timeout is None:
			self.chBuild.caput('Busy') # click the build button and return
		else:
			self.chBuild.caput('Busy', timeout) # click the build button and wait for the call back
		

	def isBuilt(self):
		strStatus = self.getScanStatus();
#		strBuildStatus=self.chBuildStatus.caget();
#		if strBuildStatus == "Failure":
#			raise Exception("Fast energy scan CAN NOT be built. Please check the ID speed setting is not too slow!");
			
		if strStatus == 'Build failed - ID velocity too slow': #Built error
			raise Exception("Fast energy scan CAN NOT be built. Please check the ID speed setting is not too slow!");
		elif strStatus == 'Scan ready': #Finished building
			return True
		else:
			return False;

	def isScanReady(self):
		strStatus = self.getScanStatus();
		if strStatus == "Scan ready": #Finished building
			return True
		else:
			return False;
		
	def isScanning(self):
		strStatus = self.getScanStatus();
		if strStatus == "Scanning": #Finished building
			return True
		else:
			return False;

	def isScanComplete(self):
		strStatus = self.getScanStatus();
		if strStatus in ['Scan complete', 'Scan aborted'] and self.isCalled: #The last scan is finished and is called back
			return True
		else:
			return False;
		
	def isScanAborted(self):
		strStatus = self.getScanStatus();
		if strStatus == "Scan aborted": #The last scan is aborted.
			return True
		else:
			return False;

	def getScanStatus(self):
		newScanStatus = self.chStatus.caget();
		if newScanStatus != self.scanStatus: # scan status changed
			self.scanStatus = newScanStatus;
#			print self.scanStatus;
		return self.scanStatus;

###########################################################################
class FastEnergyScanIDModeClass(ScannableMotionBase):
	""" """

	def __init__(self, name, fastEnergyScanController):
		self.setName(name);
		self.setInputNames([name])
		self.setExtraNames([]);
		self.setOutputFormat(["%12.6f"]);
		self.setLevel(6);

		self.fesController = fastEnergyScanController;

	#set the ID mode
	def setIDMode(self, mode):
		self.fesController.setIDMode(mode);

	#get the ID mode
	def getIDMode(self):
		return self.fesController.getIDMode();

#ScannableMotionBase Implementation
	def getPosition(self):
		mode = self.getIDMode();
		modeString = FastEnergyScanControlClass.FASTSCAN_MODE_GDA_STRING[mode];
		return modeString;

	def asynchronousMoveTo(self,newPos):
		if newPos in FastEnergyScanControlClass.FASTSCAN_MODE:
			mode = newPos;
		elif newPos in FastEnergyScanControlClass.FASTSCAN_MODE_EPICS_STRING:
			mode = FastEnergyScanControlClass.FASTSCAN_MODE_EPICS_STRING.index(newPos);
		elif newPos in FastEnergyScanControlClass.FASTSCAN_MODE_GDA_STRING:
			mode = FastEnergyScanControlClass.FASTSCAN_MODE_GDA_STRING.index(newPos);
		else:
			print "Please use 'fixid', 'cvid' or 'slaveid' to set the fast energy scan mode";
			return;
		
		self.setIDMode(mode);
		
	def isBusy(self):
		return False;
	
	def toString(self):
		modeInfo="Fast Energy Scan ID mode: " + self.getPosition();
		return modeInfo;

###########################################################################
class FastEnergyDeviceClass(ScannableMotionBase):
	""" """

	def __init__(self, name, fastEnergyScanController, fastEnergyScanDetector):
		self.setName(name);
		self.setInputNames([name])
		self.setExtraNames([]);
#		self.Units=[strUnit]
		self.setOutputFormat(["%12.6f"]);
		self.setLevel(6);

		self.fesController = fastEnergyScanController;
		self.fesDetector = fastEnergyScanDetector;
		
		self.scanStatus='Idle';
		self.indexPosition = 0;
		self.indexChannel = 6;

		self.delay=None;
		self.filterByEnergy = True

	def setDelay(self, delay):
		self.delay = delay;

	#set the ID mode
	def setIDMode(self, mode):
		self.fesController.setIDMode(mode);

	#get the ID mode
	def getIDMode(self):
		return self.fesController.getIDMode();

	def buildScan(self):
		try:
			if not self.fesController.checkMotorReady():
				raise Exception("Fast energy scan CAN NOT be performed. Please check both PGM and ID are ready!");
			
			if self.fesController.getScanStatus() not in ["Scan complete", "Scan aborted", "Build failed - ID velocity too slow"]: #Not in Ready to Build status
				raise Exception("Fast energy scan CAN NOT be built because of wrong EPICS status!");
			
			#trigger the scan
			self.fesController.buildScan();
			print "Start building the fast energy scan..."
		
			while not self.fesController.isBuilt():
				logger.singlePrint('... ' + self.fesController.getScanStatus());
				sleep(2);
			print 'Fast Scan Built'
			
			#To check the ID velocity
#			print 'To check the ID motor velocity limit'
#			vID = int( float(self.fesController.getVelocityStatus()) );
#			if vID == 0:
#				print "... Required ID Speed OK";
#			else:
#				print "... Required ID Speed too LOW / too HIGH";
			
		except:
			exceptionType, exception, traceback=sys.exc_info();
			logger.fullLog(None, "Error occurs at FastEnergyDeviceClass.buildScan", exceptionType, exception, traceback, True);

	def execScan(self):
		try:
			if not self.fesController.isScanReady():
				raise Exception("Fast energy scan CAN NOT be performed. Please build the scan first!");
		
			print "Start the fast energy scan..."
			self.fesController.startScan();
			self.fesDetector.reset();
			self.indexPosition = 0;
			sleep(2);
		except:
			exceptionType, exception, traceback=sys.exc_info();
			logger.fullLog(None, "Error occurs at FastEnergyDeviceClass.execScan", exceptionType, exception, traceback, True);
		
#ScannableMotionBase Implementation
	def atScanStart(self):
#		print "At Scan Start"
		try:
			self.buildScan();
			self.execScan();
			
		except:
			exceptionType, exception, traceback=sys.exc_info();
			logger.fullLog(None, "Error occurs at FastEnergyDeviceClass.atScanStart", exceptionType, exception, traceback, True);

	def atScanEnd(self):
#		print "At Scan End"
		return;

	def atScanLineStart(self):
#		print "At Line Start"
		return;
		
	def atScanLineEnd(self):
#		print "At Line End, with index: ", self.indexPosition;
		return;

	def atPointStart(self):
#		print "At Point Start"
		return;
	
	def atPointEnd(self):
		self.indexPosition += 1;
#		print "At Point End with index: ", self.indexPosition;

	def getPosition(self):
		return self.fesDetector.readoutChannel(self.indexChannel);

	def asynchronousMoveTo(self,newPos):
		self.fesDetector.asynchronousMoveTo(self.indexPosition);
		if self.delay is not None:
			sleep(self.delay);
#		print "---> Debug: Energy device moves forward; " + str(newPos);
#		print "---> Debug: Energy Device asking new data at: " + ctime();
		
	def isBusy(self):
		if self.fesDetector.isDataAvailable():
#			logger.simpleLog("FastEnergyDeviceClass isBusy: False")
			return False;
		else:
#			logger.simpleLog("FastEnergyDeviceClass isBusy: True")
			if self.delay is not None:
				sleep(self.delay);
			return True;
	
	
	def toString(self):
		p=self.getPosition();
		return str(p);

	def stop(self):
		print self.getName() + ": Panic Stop Called"
		self.fesController.abortScan();

	def applyFileFilter(self, indexName, low, high):
		sff= SrsFileFilterClass(indexName, low, high);
		sff.setFilter(indexName, low, high);
		sff.loadFile();
		sff.applyFilter();
		sff.saveFile();
#		sff.saveNewFile();


	def cvscan(self, startEnergy, endEnergy, scanTime, pointTime):
		
		if not self.fesController.checkPGM():
			print "PGM is not in a movable status. Please check it manually!"
			return;

		if startEnergy >= endEnergy:
			print "Can only scan from low energy to high energy!"
			raise Exception('Wrong Energe Range!');

		self.fesDetector.reset();
		sleep(1);
		self.fesDetector.setFilter(startEnergy, endEnergy, self.indexChannel);
		self.fesController.setEnergyRange(startEnergy, endEnergy);
		self.fesController.setTime(scanTime, pointTime);
#		self.fesController.setIDMode(1);
	
		if pointTime > 2.0:
			self.setDelay(pointTime/2.0);
		elif pointTime>0.5:
			self.setDelay(pointTime/5.0);
		else:
			self.setDelay(pointTime/10.0);
			
		#to set delay half of point time
		self.setDelay(pointTime*0.5);
		
		numPoint = self.fesController.getNumberOfPoint();
		if numPoint < 1:
			print "Number of scan points is set to ZERO. Please check your command carefully!"
			return;
		
		step=1.0*(endEnergy - startEnergy)/numPoint;
		
		#pscan fastEnergy 0 1 numPoint fesData 0 1;
		fesData = self.fesDetector;
		
		try:
			theScan = PointsScan([self,0,1,numPoint,fesData,0,1]);
			theScan.runScan();
		except:
			exceptionType, exception, traceback=sys.exc_info();
			logger.fullLog(None, "Error occurs at FastEnergyDeviceClass.cvscan", exceptionType, exception, traceback, True);
			
		while(not self.fesController.isScanComplete() ):
			logger.singlePrint( "Wait for the fast energy scan to finish" );
			sleep(1);

		if self.fesController.isScanAborted():
			print "The Fast Energy Scan is aborted.";
		else:
			if self.filterByEnergy:
				# Apply the file filter to get rid of bad points
				print "Filtering " + self.getName() + " between %r and %r" % (startEnergy, endEnergy)
				self.applyFileFilter(str(self.getName()), startEnergy, endEnergy);
			print "The Fast Energy Scan for complete.";


#######################################################
class EpicsScandataDeviceClass(ScannableMotionBase):
	
	def __init__(self, name, rootPV):

		self.numberOfDetectors=None;
		self.setupEpics(rootPV);
		
		self.setName(name);
		self.setInputNames(["index"]);
		self.setLevel(7);
		en=[]; of=["%5.0f"];
		for i in range(self.numberOfDetectors):
			en.append("Channel_" + str(i+1));
			of.append("%20.12f");
		self.setExtraNames(en);
		self.setOutputFormat(of);

		self.timeout=30;
		self.defaultSize = 100;
		self.reset();


	def __del__(self):
		self.cleanChannel(self.chHead);
		self.cleanChannel(self.chDetectorNumbers);
		self.cleanChannel(self.chOffset);
		self.cleanChannel(self.chSize);
		self.cleanChannel(self.chUpdate);

		for chd in self.chData:
			self.cleanChannel(chd);

	def reset(self):
		self.setDataOffset(0);
		self.resetHead();
		self.setSize(self.defaultSize);
		self.data=[[None]]*self.numberOfDetectors;
		
		self.dataset = None;
		self.readPointer = -1;
		
	def getDataLength(self):
		if self.dataset is None:
			return 0;
		
		dim=self.dataset.shape
		return dim[1];
	
	def setupEpics(self, rootPV):
		#Epics PV for the Number of elements available
		self.chHead=CAClient(rootPV + ":ELEMENTCOUNTER");  self.configChannel(self.chHead);

		#Epics PV for the Number of channels (detectors)
		self.chDetectorNumbers=CAClient(rootPV + ":NODETECTORS");  self.configChannel(self.chDetectorNumbers);

		#Epics PV for setting the starting point for reading
		self.chOffset=CAClient(rootPV + ":STARTINDEX");  self.configChannel(self.chOffset);

		#Epics PV for setting the number of points for reading
		self.chSize=CAClient(rootPV + ":NOELEMENTS");  self.configChannel(self.chSize);

		#Epics PV for getting the data specified in offset and size
		self.chUpdate=CAClient(rootPV + ":UPDATE");  self.configChannel(self.chUpdate);

#		Epics PVs for the channels:
		self.numberOfDetectors = int(float(self.chDetectorNumbers.caget()));
		self.chData=[];

		for i in range(self.numberOfDetectors):
			self.chData.append( CAClient(rootPV + ":CH" + str(i+1) + "SUBARRAY"));
			self.configChannel(self.chData[i]);

		
	def configChannel(self, channel):
		if not channel.isConfigured():
			channel.configure();

	def cleanChannel(self, channel):
		if channel.isConfigured():
			channel.clearup();

#	Epics level operation:
	def getHead(self):
		head = int(float(self.chHead.caget()))-1;
		return head;

	def resetHead(self):
		self.chHead.caput(0);

	def setDataOffset(self, offset):
		self.chOffset.caput(self.timeout,offset);
	
	def getDataOffset(self):
		offset = int(float(self.chOffset.caget()));
		return offset;
	
	def setSize(self, size):
		self.chSize.caput(self.timeout,size);

	def getSize(self):
		size = int(float(self.chSize.caget()));
		return size;
		
	def updateData(self, offset, size):
		return self.getNewEpicsData(offset, size);
		
	def getNewEpicsData(self, offset, size):
		#To check the head
		head=self.getHead();
		if offset > head:
#			print " No new data available. Offset exceeds Head(" + str(head) + ").";
			return False;
		
#		print "New data available, Offset "+ str(offset) + " does not exceed Head(" + str(head) + ").";
		size = min(size, head-offset+1);
		
#		print "New offset %d" %offset + ", new size %d" %size;
		self.setDataOffset(offset);
		self.setSize(size);
		
		#Ask EPICS to update the subarrays
#		print "---> Debug: updating subarrays: start at: " + ctime();
		self.chUpdate.caput(self.timeout, 1);
#		self.chUpdate.caput(1);
#		sleep(1)
#		print "###> Debug: the current ElementCounter is : " + str(self.getHead());
#		print "###> Debug: the subarray size is: " + str(size);
#		print "---> Debug: updating subarrays: end at: " + ctime();

		la=[];
		#To get the subarray data from EPICS
#		print "---> Debug: get subarrays: start at: " + ctime();
		for i in range(self.numberOfDetectors):
#			self.data[i]=self.chData[i].cagetArrayDouble();
#TODO: make sure that the self.data[i] is a list
#			self.data[i]=self.chData[i].cagetArrayDouble();

#			self.data[i]=self.chData[i].getController().cagetDoubleArray(self.chData[i].getChannel(), self.getSize());
			ok = False
			while( not ok):
				try:
#				    logger.fullLog(None,"EpicsWaveformDeviceClass.getNewEpicsData: reading data for channel %d" %i)
				    self.data[i]=self.chData[i].getController().cagetDoubleArray(self.chData[i].getChannel(), size);
#				    logger.fullLog(None,"EpicsWaveformDeviceClass.getNewEpicsData: data read")
				    ok=True
				except:
					type, exception, traceback = sys.exc_info()
					logger.fullLog(None,"Error in EpicsWaveformDeviceClass.getNewEpicsData reading channel %d" %i, type, exception , traceback, False)
					ScriptBase.checkForPauses()

#			print "The type of subarray data from caget is: ", type(self.data[i]);
#			print "The subarray data from caget is: ", self.data[i];
			la.append(self.data[i]);
#		print "---> Debug: get subarrays: end at: " + ctime();
		
#		ds=DataSet(la);#ds is a new DataSet with dimension [numberOfDetectors, size];
#TODO: For the new dataset, the above line should be changed to the following
		ds=dnp.array(la) #ds is a new DataSet with dimension [numberOfDetectors, size];
		if self.dataset is None:
			self.dataset = ds;
		else:
			self.dataset=self.dataset.append(ds, 1) # extend the dataset along the "size" axis
#TODO: make sure that the self.dataset is a two dimensional dataset
#		print "###> Debug: the internal dataset is: ", self.dataset.getDimensions();
		return True;

# DetectorBase Implementation
	def getPosition(self):

#		resultList = list(self.readout());

		resultList = [self.readPointer];
		resultList.extend(list(self.readout()));

		resultJavaArray = jarray.array(resultList, 'd');
		return resultJavaArray;

	def asynchronousMoveTo(self,newPosition):
		self.readPointer = int(newPosition);

	def isDataAvailableNew(self):
		self.getNewEpicsData(self.getDataLength(), self.defaultSize);
		len = self.getDataLength();
		
		if len == 0 or self.readPointer > len-1:#either buffer is empty or no new data
			print "Checking Data Queue: no new data, buffer length: " + str(len);
			return False;#Epics data exhausted. 
		else: #self.readPointer <= len-1, which means there are new data in the buffer to offer
			print "Checking Data Queue: Data available."
			return True;

	def isDataAvailable(self):
#		print "---> Debug: Checking data availability"
		
		len = self.getDataLength();
		if len == 0 or self.readPointer > len-1:#either buffer is empty or no new data
#			if len == 0:
#				print "---> Debug: Empty buffer. No new data"
#			else:
#				print "---> Debug: No newly Buffered data. Try to fetch new data from EPICS"
			while self.getNewEpicsData(len, self.defaultSize):
				len = self.getDataLength();
				if self.readPointer <= len-1:#After updating buffer, new data available
					return True;
#			print "---> Debug: No more data from EPICS"
			return False;#Epics data exhausted. 
		else: #self.readPointer <= len-1, which means there are new data in the buffer to offer
#			print "---> Debug: New Buffered data available."
			return True;


	def isBusy(self):
		return False;

	def readout(self):
		if self.isDataAvailable():
#			temp = self.dataset.getSlice([0,self.readPointer], [self.numberOfDetectors, self.readPointer+1], [1,1]);
#TODO: For the new version of dataset, the above line should be changed to:
			temp = self.dataset[:, self.readPointer]

			result = temp.getBuffer();
		else:#No new data to read
			print "Wrong readPointer: %d " %self.readPointer, " or wrong dataLength: %d" %(self.getDataLength());
			raise Exception('Array Out of Boundary Error!');
		return result;
	
	def toString(self):
		return self.getName() + ": Count=" + str(self.getPosition());

	def readoutChannel(self, channelIndex):
		result = self.readout();
		return result[channelIndex-1];

						
class SingleChannelEpicsScanDataDeviceClass(EpicsScandataDeviceClass):
	
	def __init__(self, name, rootPV, channelIndex):
		EpicsScandataDeviceClass.__init__(self, name, rootPV);

		if channelIndex <= self.numberOfDetectors:
			self.channel = channelIndex;
		else:
			print "Wrong channel index. Use the default first channel"
			self.channel = 1;
			
		self.setName(name);
		self.setInputNames([name]);
		self.setExtraNames([]);
		self.setOutputFormat(["%20.12f"]);

# ScannableMotionBase Implementation
	def getPosition(self):
		result = self.readout();
		return result[self.channel-1];


#######################################################
class EpicsWaveformDeviceClass(ScannableMotionBase):
	def __init__(self, name, rootPV, channelList, extraChannelList=[]):

		self.numberOfChannels=len(channelList);
		self.setupEpics(rootPV);
		
		self.setName(name);
		self.setInputNames(["pIndex"]);
		self.setLevel(7);
		en=[]; of=["%5.0f"];
		for c in channelList + extraChannelList:
			en.append( str(c) );
			of.append("%20.12f");

		self.setExtraNames(en);
		self.setOutputFormat(of);

		self.timeout=30;
		self.defaultSize = 100;
		self.low = 0;
		self.high = 1000;
		self.keyChannel=None;

#		self.fastScanElementCounter = None;
		self.fastScanElementCounter = Finder.find("fastScanElementCounter");

		self.reset();

	def __del__(self):
		self.cleanChannel(self.chHead);
		for chd in self.chData:
			self.cleanChannel(chd);

	def reset(self):
		self.data=[[None]]*self.numberOfChannels;
		self.dataset = None;
		self.readPointer = -1;
		self.resetHead();
		
	def setFilter(self, low, high, keyChannel):
		self.low = low;
		self.high = high;
		self.keyChannel=keyChannel;
		
	def getDataLength(self):
		if self.dataset is None:
			return 0;
		dim=self.dataset.shape
		return dim[1];


	"""
	waveform PVs
	rootPV          = 'BL06I-MO-FSCAN-01'
	pvElementCounter= 'BL06I-MO-FSCAN-01:ELEMENTCOUNTER'

	pvDataChannel01 = 'BL06I-MO-FSCAN-01:CH1DATA'
	pvDataChannel02 = 'BL06I-MO-FSCAN-01:CH2DATA'
	pvDataChannel03 = 'BL06I-MO-FSCAN-01:CH3DATA'
	pvDataChannel04 = 'BL06I-MO-FSCAN-01:CH4DATA'
	...
	"""	
	def setupEpics(self, rootPV):
		#Epics PV for the Number of elements available
		self.chHead=CAClient(rootPV + ":ELEMENTCOUNTER");  self.configChannel(self.chHead);

#		Epics PVs for the channels:
		self.chData=[];
		for i in range(self.numberOfChannels):
			self.chData.append( CAClient(rootPV + ":CH" + str(i+1) + "DATA"));
			self.configChannel(self.chData[i]);
		
	def configChannel(self, channel):
		if not channel.isConfigured():
			channel.configure();

	def cleanChannel(self, channel):
		if channel.isConfigured():
			channel.clearup();

#	Epics level operation:
	def getHead(self):
		if self.fastScanElementCounter != None:
			return int(float(self.fastScanElementCounter()))-1;
		else:
			head = int(float(self.chHead.caget()))-1;
			return head;

	def resetHead(self):
		self.chHead.caput(0);
	
	def getNewEpicsData(self, offset, size):
		#To check the head
		head=self.getHead();
		if offset > head:
#			print " No new data available. Offset exceeds Head(" + str(head) + ").";
			return False;

#		print "New data available, Offset does not exceed Head(" + str(head) + ").";
		la=[];
		#To get the waveform data from EPICS
#		print "---> Debug: get waveform: start at: " + ctime();
		for i in range(self.numberOfChannels):
#			self.data[i]=self.chData[i].cagetArrayDouble();
#TODO: make sure that the self.data[i] is a list
#			self.data[i]=self.chData[i].cagetArrayDouble();
#			self.data[i]=self.chData[i].getController().cagetDoubleArray(self.chData[i].getChannel(), head+1);
#			print "The type of subarray data from caget is: ", type(self.data[i]);
#			print "The subarray data from caget is: ", self.data[i];
#		print "---> Debug: get waveform: end at: " + ctime();

			ok = False
			while( not ok):
				try:
#				    logger.fullLog(None,"EpicsWaveformDeviceClass.getNewEpicsData: reading data for channel %d" %i)
				    self.data[i]=self.chData[i].getController().cagetDoubleArray(self.chData[i].getChannel(), head+1);
#				    logger.fullLog(None,"EpicsWaveformDeviceClass.getNewEpicsData: data read")
				    ok=True
				except:
				    type, exception, traceback = sys.exc_info()
				    logger.fullLog(None,"Error in EpicsWaveformDeviceClass.getNewEpicsData reading channel %d" %i, type, exception , traceback, False)
				    ScriptBase.checkForPauses();

			la.append(self.data[i]);
		
#		ds=DataSet(la);#ds is a new DataSet with dimension [numberOfDetectors, size];
#TODO: For the new dataset, the above line should be changed to the following
		ds=dnp.array(la) #ds is a new DataSet with dimension [numberOfDetectors, size];
		
		self.dataset = ds;
		return True;

	def getUnFilteredPosition(self):
#		resultList = list(self.readout());
		resultList = [self.readPointer]; #The index
		resultList.extend(list(self.readout())); # the readout
		
		resultJavaArray = jarray.array(resultList, 'd');
		return resultJavaArray;

		
	def applyFilter(self, inputList, low, high, index):
		if index is None:
			return inputList;
		
		outputList=[];
		judge=inputList[index]
		for i in range(len(inputList)):
			if (judge>=low and judge<=high) or i==index:
				outputList.append(inputList[i]);
			else:
				outputList.append(0);
				
		return outputList;

	def getFilteredPosition(self):
		
		filteredReadout = self.applyFilter(list(self.readout()), self.low-1.0, self.high+1.0, self.keyChannel-1);
			
#		resultList = list(self.readout());
		resultList = [self.readPointer]; #The index
		resultList.extend(filteredReadout); # the readout
		
		resultJavaArray = jarray.array(resultList, 'd');
		return resultJavaArray;

# DetectorBase Implementation
	def getPosition(self):
#		return self.getUnFilteredPosition();
		return self.getFilteredPosition();


	def asynchronousMoveTo(self,newPosition):
		self.readPointer = int(newPosition);

	def isDataAvailableNew(self):
		self.getNewEpicsData(self.getDataLength(), self.defaultSize);
		len = self.getDataLength();
		
		if len == 0 or self.readPointer > len-1:#either buffer is empty or no new data
			print "Checking Data Queue: no new data, buffer length: " + str(len);
			return False;#Epics data exhausted. 
		else: #self.readPointer <= len-1, which means there are new data in the buffer to offer
			print "Checking Data Queue: Data available."
			return True;

	def isDataAvailable(self):
#		print "---> Debug: Checking data availability"
		len = self.getDataLength();
		if len == 0 or self.readPointer > len-1:#either buffer is empty or no new data
			while self.getNewEpicsData(len, self.defaultSize):
				len = self.getDataLength();
				if self.readPointer <= len-1:#After updating buffer, new data available
#					logger.simpleLog("EpicsWaveformDeviceClass.isDataAvailable: True, len=%d, readPointer= %d" % (len, self.readPointer));
					return True;
#			print "---> Debug: No more data from EPICS"
#			logger.simpleLog("EpicsWaveformDeviceClass.isDataAvailable: False");
			return False;#Epics data exhausted. 
		else: #self.readPointer <= len-1, which means there are new data in the buffer to offer
#			print "---> Debug: New Buffered data available."
#			logger.simpleLog("EpicsWaveformDeviceClass.isDataAvailable: True");
			return True;


	def isBusy(self):
		return False;

	def readout(self):
		if self.isDataAvailable():
			result = self.dataset[:, self.readPointer]
		else:#No new data to read
			print "Wrong readPointer: %d " %self.readPointer, " or wrong dataLength: %d" %(self.getDataLength());
			raise Exception('Array Out of Boundary Error!');
		
		ev=self.getExtraChannelValues(result);
		result.resize(result.size+len(ev))
		result[-len(ev):]=ev
		
		return result;
	
	def toString(self):
		return self.getName() + ": Count=" + str(self.getPosition());

	#To artificially add extra channels of which value is a calculation of existing channels
	def getExtraChannelValues(self, d):
		Id, I0, If = d[0], d[1], d[2]; #Channel 2, channel 1 and channel 3

		if I0 <= 0.001:
			I0 += 0.001;
			
		idi0 = float(Id)/I0;
		ifi0 = float(If)/I0;
		
		return [idi0, ifi0];
		
	def readoutChannel(self, channelIndex):
		result = self.readout();
		return result[channelIndex-1];
