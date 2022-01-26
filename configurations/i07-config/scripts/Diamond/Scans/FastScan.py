
from time import sleep, ctime;
import jarray;
import sys, math;

from gda.epics import CAClient;
from gda.device.scannable import ScannableBase
from gda.scan import PointsScan;
from org.eclipse.january.dataset import DatasetFactory

from gov.aps.jca.event import PutEvent;
from gov.aps.jca.event import PutListener;
from gov.aps.jca import CAStatus;

#Introduce the script logger
from Diamond.Utility.ScriptLogger import ScriptLoggerClass;
logger=ScriptLoggerClass();

class FastScanControlClass(object):
	""" """

	MOTOR_STATUS_UPPERLIMIT, MOTOR_STATUS_LOWERLIMIT, MOTOR_STATUS_FAULT, MOTOR_STATUS_READY, MOTOR_STATUS_BUSY, MOTOR_STATUS_UNKNOWN, MOTOR_STATUS_SOFTLIMITVIOLATION = range(7);

	class CaputCallbackListenerClass(PutListener):
		def __init__ (self, owner):
			self.owner = owner;
			
		def putCompleted(self, event):
			if event.getStatus() != CAStatus.NORMAL:
				print 'Motor move failed!'
				print 'Failed source: ' + event.getSource().getName();
				print 'Failed stuatus: ' + event.getStatus();
			else:
				print 'Fast scan finished. The motor calls back';
#				self.owner.status = FastScanControlClass.MOTOR_STATUS_READY;
			return;

		def getStatus(self):
				return self.motor.status;


	def __init__(self, name):
		self.name = name;
		self.scanStatus='Idle';
		self.scanTime = None;
		self.pointTime = None;
		self.numberOfPoints = None;
		self.velocity = None;
		self.accl = None;
		self.putListener = FastScanControlClass.CaputCallbackListenerClass(self);

	def setScannable(self, scannableDevice):
		try:
			self.motor= scannableDevice.getMotor();
		except:
			raise ValueError("No device found Error");
		
		self.scannableDevice = scannableDevice;
		self.backupMotor();

	def setScanRange(self, startPosition, stopPosition):
		self.startPosition=1.0*startPosition;
		self.stopPosition=1.0*stopPosition;

	def getScanRange(self):
		return [self.startPosition, self.stopPosition];

	def setTime(self, scanTime, pointTime):
		self.scanTime = 1.0*scanTime;
		self.pointTime=1.0*pointTime;
		self.setVelocity(None);
		
	def getNumberOfPoint(self):
		return int(1.0 * self.scanTime / self.pointTime) + 1;

	def getStep(self):
		return 1.0*(self.stopPosition-self.startPosition)/( self.getNumberOfPoint()-1);
	
	def getEstimatedPositions(self):
		numberOfPoint = self.getNumberOfPoint();
		step = self.getStep();
	
		result = [float("%.4f" %(self.startPosition + x*step)) for x in range(numberOfPoint)];

		return result;

	def getRealPositions(self):
		return self.getEstimatedPositions();
	
	def getRealPosition(self):
		return self.scannableDevice.getPosition();

	def setAcceleration(self, accl):
		self.accl=accl;
		
	def setVelocity(self, velocity=None):
		if velocity is None:
			velocity = math.fabs( (self.stopPosition-self.startPosition)/self.scanTime);

		self.velocity = 1.0*velocity;
		print "New Velocity is: " + str(self.velocity);
			
	def getRampingTime(self):
		result = math.fabs(1.0*self.velocity/self.accl);
#		currentPosition = self.motor.getPosition();
#		result = math.sqrt(2.0*math.fabs(self.startPosition-currentPosition)/self.accl);
		return result;
	def getRampingDistance(self):
		t=self.getRampingTime();
		
		result = math.fabs(0.5*self.accl*t*t);
		return result;
	
	def getStartPosition(self):
		lLimit=self.motor.getMinPosition();
		hLimit=self.motor.getMaxPosition();
		if self.stopPosition > self.startPosition:
			s0 = self.startPosition - self.getRampingDistance();
			return max(s0, lLimit);
		else:
			s0=self.startPosition + self.getRampingDistance();
			return min(s0, hLimit)
		
	def getEndPosition(self):
		lLimit=self.motor.getMinPosition();
		hLimit=self.motor.getMaxPosition();
		if self.stopPosition > self.startPosition:
			s0=self.stopPosition + self.getRampingDistance();
			return min(s0, hLimit)
		else:
			s0=self.stopPosition - self.getRampingDistance();
			return max(s0, lLimit);

	def getVelocity(self):
		return self.velocity;
	
	def getMotorSpeed(self):
		return self.motor.getSpeed();
	
	def setMotorSpeed(self, speed):
		return self.motor.setSpeed(speed);

	def check(self):
#		self.velocity = self.velocity;
#		self.startPosition = self.startPosition;
#		self.stopPosition = self.stopPosition;
		return;

	def backupMotor(self):
		self.motorVelo = self.motor.getSpeed();

	def restoreMotor(self):
		self.motor.setSpeed(self.motorVelo);
		
	def build(self):
		self.check()
		self.scannableDevice.moveTo( self.getStartPosition() );
		self.setMotorSpeed(self.velocity);
		sleep(1);

	def kickoff(self):
#		self.motor.moveTo( self.getEndPosition(), self.putListener);
#		testMotor1.asynchronousMoveTo(self.getEndPosition());
		self.scannableDevice.asynchronousMoveTo(self.getEndPosition());

	def abortScan(self):
		self.restoreMotor();

class FastMotionDeviceClass(ScannableBase):
	""" """

	def __init__(self, name, fastScanController, fastScanDetector):
		self.setName(name);
		name1=fastScanController.scannableDevice.getName();
		name2=fastScanController.scannableDevice.getName()+"RBV";
		self.setInputNames([name1]);
		self.setExtraNames([name2]);
#		self.Units=[strUnit]
		self.setOutputFormat(["%12.6f", "%12.6f"]);
		self.setLevel(6);

		self.fastController = fastScanController;
		self.fastDetector = fastScanDetector;
		
		self.scanStatus='Idle';
		self.indexPosition = 0;
		self.indexChannel = 6;

		self.delay=None;
		
	def setDelay(self, delay):
		self.delay = delay;

#A function to run the fast scan
	def cvscan(self, startPosition, stopPosition,scanTime, pointTime):
		
#		self.fastController.setAcceleration(0.2);
#		self.fastController.setMotorSpeed(6);
		self.fastController.setScanRange(startPosition, stopPosition);
		self.fastController.setTime(scanTime, pointTime);
	
		self.fastDetector.setTime(scanTime+2.0*pointTime, pointTime);
		numPoint = self.fastController.getNumberOfPoint();
		
		self.fastController.setVelocity(velocity=None);
		positions1=self.fastController.getEstimatedPositions();

		step=self.fastController.getStep();
		
		try:
			theScan = PointsScan([self, 0, 1, numPoint, self.fastDetector, 0, 1]);
			theScan.runScan();
		except:
			exceptionType, exception, traceback=sys.exc_info();
			logger.fullLog(None, "Error occurs at FastMotionDeviceClass.cvscan", exceptionType, exception, traceback, True);

		
		positions2=self.fastController.getRealPositions();
	
#ScannableMotionBase Implementation
	def atScanStart(self):
#		print "At Scan Start"
		#trigger the scan
		
		print "Building the scan ..."
		print "---> Debug: Current Time: " + ctime();
		self.fastController.build();
		
		print "Start ramping ..."
		print "---> Debug: Current Time: " + ctime();
		self.fastController.kickoff();
		
		sleepTime = self.fastController.getRampingTime();
		if sleepTime >=10:
			sleepTime -= 10;
		else:
			sleepTime = 0;
			
		sleep(sleepTime);
	
		print "...Start scan"
		print "---> Debug: Current Time: " + ctime();
		print "---> Debug: Current Position: " + str(self.fastController.scannableDevice.getPosition());
		
		self.fastDetector.reset();
		self.fastDetector.start();
		self.indexPosition = 0;

	def atScanEnd(self):
#		print "At Scan End"
		self.fastController.restoreMotor();
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
#		return
		ep = self.fastController.getEstimatedPositions()[self.indexPosition];
		rp = self.fastController.getRealPosition();
#		return self.indexPosition;
#		return self.fastDetector.readoutChannel(self.indexChannel);
		return [ep,rp];

	def asynchronousMoveTo(self,newPos):
		self.fastDetector.asynchronousMoveTo(self.indexPosition);
#		print "---> Debug: Energy device moves forward; " + str(newPos);
#		print "---> Debug: Energy Device asking new data at: " + ctime();
		return;
		
	def isBusy(self):
#		return self.fesDetector.isBusy();
		if self.fastDetector.isDataAvailable():
			if self.delay is not None:
				sleep(self.delay);
			return False;
		else:
			return True;
	
	
	def toString(self):
		p=self.getPosition();
		return str(p);

	def stop(self):
		print self.getName() + ": Panic Stop Called"
		self.fastController.abortScan();



class EpicsMCADataDeviceClass(ScannableBase):
	
	def __init__(self, name, rootPV, numberOfMCA):
		self.numberOfDetectors = numberOfMCA;
		self.setupEpics(rootPV);
		
		self.setName(name);
		self.setInputNames([]);
		self.setLevel(7);
		en=[]; of=[];
		for i in range(self.numberOfDetectors):
			en.append("Channel_" + str(i+1));
			of.append("%20.12f");
		self.setExtraNames(en);
		self.setOutputFormat(of);

		self.timeout=30;
		self.defaultSize = 100;
		self.reset();

	def __del__(self):
		self.cleanChannel(self.chDwell);
		self.cleanChannel(self.chPreset);
		self.cleanChannel(self.chEraseStart);

		self.cleanChannel(self.chHead);
		for chd in self.chData:
			self.cleanChannel(chd);

	def reset(self):
		self.data=[[None]]*self.numberOfDetectors;
		self.dataset = None;
		self.readPointer = -1;
		
	def getDataLength(self):
		if self.dataset is None:
			return 0;
		
		dim=self.dataset.getDimensions();
		return dim[1];
	
	
	"""
	rootPV:   BL07I-EA-DET-01:MCA-01
	Waveform: BL07I-EA-DET-01:MCA-01:mca1
	Head:     BL07I-EA-DET-01:MCA-01:mca1.NORD
	
	PointTime: BL07I-EA-DET-01:MCA-01:Dwell
	TotalTime: BL07I-EA-DET-01:MCA-01:PresetReal
	EraseStart: BL07I-EA-DET-01:MCA-01:EraseStart
	
	"""
	def setupEpics(self, rootPV):
		self.chDwell =CAClient(rootPV + ":Dwell"); self.configChannel(self.chDwell);
		self.chPreset=CAClient(rootPV + ":PresetReal"); self.configChannel(self.chPreset);
		self.chEraseStart=CAClient(rootPV + ":EraseStart"); self.configChannel(self.chEraseStart);

		#Epics PV for the Number of elements available (Head of waveform)
		self.chHead=CAClient(rootPV + ":mca1.NORD");  self.configChannel(self.chHead);

#		Epics PVs for the channels:
		self.chData=[];
		for i in range(self.numberOfDetectors):
			self.chData.append( CAClient(rootPV + ":mca" + str(i+2)));
			self.configChannel(self.chData[i]);
		
		
	def configChannel(self, channel):
		if not channel.isConfigured():
			channel.configure();

	def cleanChannel(self, channel):
		if channel.isConfigured():
			channel.clearup();

#	Epics level operation:
	def setTime(self, totalTime, pointTime):
		self.chPreset.caput(totalTime);
		self.chDwell.caput(pointTime);
		
	def start(self):
		self.chEraseStart.caput(1);

	def getHead(self):
		head = int(float(self.chHead.caget()))-1;
		return head;
	
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
		for i in range(self.numberOfDetectors):
#			self.data[i]=self.chData[i].cagetArrayDouble();
#TODO: make sure that the self.data[i] is a list
#			self.data[i]=self.chData[i].cagetArrayDouble();
			self.data[i]=self.chData[i].getController().cagetDoubleArray(self.chData[i].getChannel(), head+1);
#			print "The type of subarray data from caget is: ", type(self.data[i]);
#			print "The subarray data from caget is: ", self.data[i];
			la.append(self.data[i]);
#		print "---> Debug: get waveform: end at: " + ctime();
		
		ds=DatasetFactory.createFromObject(la) #ds is a new DataSet with dimension [numberOfDetectors, size];
		
		self.dataset = ds;
		return True;

# DetectorBase Implementation
	def getPosition(self):
		resultList = list(self.readout());
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
			temp = self.dataset.getSlice([0,self.readPointer], [self.numberOfDetectors, self.readPointer+1], [1,1]);
#TODO: For the new version of dataset, the above line should be changed to:
#			temp = self.dataset[:, self.readPointer]

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
