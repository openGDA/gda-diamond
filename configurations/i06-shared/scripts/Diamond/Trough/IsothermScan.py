
from time import sleep, ctime;
import time, sys, math, random;

import jarray;

from java import lang

from gda.device.scannable import PseudoDevice;
from gda.device.scannable import ScannableBase
from gda.device.MotorStatus import READY, BUSY, FAULT;

from gda.device import Detector
from gda.device.detector import DetectorBase

from gda.scan import ConcurrentScan, PointsScan;

from Diamond.Utility.Threads import BackgroundRunningTask
#To start a long running activity
def doAsync (func, param):
	BackgroundRunningTask(func, param).start()


from Diamond.PseudoDevices.FileFilter import SrsFileFilterClass;

from Diamond.Utility.ScriptLogger import ScriptLoggerClass;
logger=ScriptLoggerClass();


from gda.jython import ScriptBase




class DummyTriggeringDevice(DetectorBase):
	def __init__(self, name):
		
		self.setName(name);
		self.setLevel(7);

		self.setInputNames(["collectionTime"]);
		self.setExtraNames(["NumberOfTriggering"]);
		self.setOutputFormat(["%5.3f", "%10.5f"]);

		self.numberOfChannels=2
		self.labelList=["Channel1", "Channel2"]
		self.numberOfTriggerings = 1;
		self.timeout = 60;
		self.timeoutStart=None;

		self.reset();


	def reset(self):
		self.length=0;
		self.dataBuffer=[[]]*self.numberOfChannels;

	def setNumberOfTriggers(self, numberOfTriggerings):
		self.reset();
		self.numberOfTriggerings = numberOfTriggerings;
		
#		for i in range( self.numberOfTriggerings ):
#			self.setTimeout();
#			while not self.isDataAvailable():
#				print "Waiting for trigger " + str(i)
#				sleep(5);
#				self.checkTimeout();
#			print "One trigger Done!"
#		print "All Done!"
		
	def slowRefill(self):
		for i in xrange(self.numberOfTriggerings):
			self.refill(1);
			sleep(self.collectionTime);
			
	def refill(self, numberOfDataPoints):
#		numberOfDataPoints = min(self.numberOfTriggerings-dl, numberOfDataPoints);
		for i in range(self.numberOfChannels):
			self.dataBuffer[i].extend(  [random.uniform(i,i+1) for r in xrange(numberOfDataPoints)] );
			
		return self.dataBuffer;
	
	def getBuffer(self):
		return self.dataBuffer

	def getBufferLength(self):
		self.length = len( self.dataBuffer[0] );
		return self.length;

	def setTimeout(self):
#		print "To set timeout"
		self.timeoutStart = time.time();
			
	def checkTimeout(self):
#		print "To check timeout"
		if self.timeoutStart is None:#no one set the timeout yet. 
			return;
		
		currenttime = time.time();
		
		if currenttime>self.timeoutStart + self.timeout:
			raise RuntimeError("Timeout Error");
		else:
			return;
		

# Scannable Implementation
	def createsOwnFiles(self):
		return False;
	
	def collectData(self):
		self.triggerTime = time.time();
		doAsync(self.slowRefill, None);

	def readout(self):
		return [self.collectionTime,self.numberOfTriggerings];
	
	def asynchronousMoveTo(self,collectionTimeList):
		self.collectionTime=collectionTimeList[0]*0.8
		self.numberOfTriggerings = collectionTimeList[1];
		self.collectData();


	def getStatus(self):
		currenttime = time.time();
		
		if currenttime<self.triggerTime + self.getCollectionTime():
			return Detector.BUSY
		else:
			return Detector.IDLE;
		



#######################################################
# To deal with self triggering detectors that can generate multiple detection results by triggering once
#This device will query the detector continuously and save the results in an internal buffer.
#pos this device will return one element from the buffer
#class BufferedSelfTriggeringDetectorClass(DetectorBase):
class DataBufferDeviceClass(ScannableBase):
	def __init__(self, name, triggeringDevice):
		
		self.setName(name);
		self.setInputNames([name+'_index']);
		self.setLevel(7);
		
		self.indexChannel=None;
		self.triggeringDevice = triggeringDevice;

		self.reset();

	def reset(self):
		self.numberOfChannels=self.triggeringDevice.numberOfChannels

		extraNames = [];
		outputFormat = ['%f'];
		for label in self.triggeringDevice.labelList:
			extraNames.append(self.name + '_' + label)
			outputFormat.append( '%f' );

#		self.extraNames = extraNames;
#		self.outputFormat = outputFormat;
		self.setExtraNames(extraNames);
		self.setOutputFormat(outputFormat);


		self.data=[[None]]*self.numberOfChannels;
		self.defaultSize = 100;
		self.readPointer = -1;
		
	def setIndexChannel(self, indexChannel):
		self.indexChannel = indexChannel;
		
	def getDataLength(self):
		if self.data[0][0] is None:
			return 0;
		return len(self.data[0]);

	
	def getNewData(self, offset, size):
#		self.triggeringDevice.refill(5);
		#To check the data buffer head position
		head=self.triggeringDevice.getBufferLength()-1;
		if offset > head:
#			print " No new data available. Offset exceeds Head(" + str(head) + ").";
			return False;

#		print "New data available, Offset does not exceed Head(" + str(head) + ").";
		for i in range(self.numberOfChannels):
			self.data[i]=self.triggeringDevice.getBuffer()[i];
		
		return True;


	def isDataAvailable(self):
#		print "---> Debug: Checking data availability"
		len = self.getDataLength();
		if len == 0 or self.readPointer > len-1:#either buffer is empty or no new data
			while self.getNewData(len, self.defaultSize):
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

	def readout(self):
#		self.setTimeout();
		if self.isDataAvailable():
			result = [ d[self.readPointer] for d in self.data ]
#			result = zip(*self.data)[self.readPointer]
		else:#No new data to read
#			sleep(5);
#			self.checkTimeout();
			print "Wrong readPointer: %d " %self.readPointer, " or wrong dataLength: %d" %(self.getDataLength());
			raise Exception('Array Out of Boundary Error!');
		
		return result;
	
	def readoutChannel(self, channelIndex):
		result = self.readout();
		return result[channelIndex-1];

	
# Scannable Implementation
	def atScanStart(self):
		self.reset();
#		self.triggeringDevice.collectData();
#		self.triggeringDevice.moveTo([1,10]);
		return;

	def atScanEnd(self):
		self.reset();
		return;
	
	def getPosition(self):
		resultList = [self.readPointer]; #The index
		resultList.extend(list(self.readout())); # the readout
		if self.indexChannel is not None:
			resultList[0]=resultList[self.indexChannel+1];
		
		resultJavaArray = jarray.array(resultList, 'd');
		return resultJavaArray;
	
	def asynchronousMoveTo(self,newPosition):
		self.triggeringDevice.setTimeout();
		self.readPointer = int(newPosition);

	def isBusy(self):
		if self.isDataAvailable():
			return False;
		else:
			sleep(1)
			self.triggeringDevice.checkTimeout()
			return True;

				
class IsothermDetector(DummyTriggeringDevice):
	def __init__(self, name, trough):
		
		DummyTriggeringDevice.__init__(self, name);

		self.numberOfChannels=6
		self.labelList=['area', 'piA', 'temperature', 'time', 'areaB', 'PiB']
		
		self.numberOfTriggerings = 1;
		self.timeout = 30;

		self.trough = trough;
		self.reset();
	

	def refill(self, numberOfDataPoints):
#		numberOfDataPoints = min(self.numberOfTriggerings-dl, numberOfDataPoints);
		p=self.trough.readValues()

		for i in range(self.numberOfChannels):
			if self.dataBuffer[i] == []:
				self.dataBuffer[i]=[p[i]];
			else:
				self.dataBuffer[i].append(p[i]);
		
		return self.dataBuffer;

	def prepareForCollection(self):
		self.trough.setMode('AREA');
		self.trough.setArea(300);
		if not self.trough.isRunning():
			self.trough.start();
		
	def setTargetPosition(self, targetPosition):
		self.trough.setMode('AREA');
		self.trough.setArea(targetPosition);
		if not self.trough.isRunning():
			self.trough.start();
		
		
	def endCollection(self):
		pass;

#Usage 1:
#dtd = DummyTriggeringDevice("dtd")
#dd=DataBufferDeviceClass("dd", dtd);
##scan dd 0 9 1
##To trigger the dummyDetector for ten counts
##pos dtd [1,10];


#iso=IsothermDetector("iso", trough);
#di=DataBufferDeviceClass("di", iso);
##scan di 0 9 1
##To trigger the dummyDetector for ten counts
##pos troughArea 200
##pos iso [2,10];

##iso.prepareForCollection();scan di 0 19 1
##pos iso [2,20]


class IsothermScanControlClass(object):
	
	def __init__(self, name, trough):
		self.name = name;
		self.scanStatus='Idle';
		self.scanTime = None;
		self.pointTime = None;
		self.numberOfPoints = None;
		self.velocity = None;
		self.accl = 1.0e+5;
		self.trough=trough;
		self.indexChannel=None;

	def setIndexChannel(self, indexChannel):
		self.indexChannel = indexChannel;
		
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
		pass

	def setAcceleration(self, accl):
		self.accl = accl;
		
	def setVelocity(self, velocity=None):
		if velocity is None:
			velocity = math.fabs( (self.stopPosition-self.startPosition)/self.scanTime);

		self.velocity = 1.0*velocity*self.trough.getSpeedCorrectionFactor();
		print "New Velocity is: " + str(self.velocity) + " cm2/s";
			
	def getRampingTime(self):
		result = math.fabs(1.0*self.velocity/self.accl);
		return result;
	
	def getRampingDistance(self):
		t=self.getRampingTime();
		result = math.fabs(0.5*self.accl*t*t);
		return result;
	
	def getStartPosition(self):
		lLimit, hLimit = self.trough.getAreaLimits();
		
		if self.stopPosition > self.startPosition:
			s0 = self.startPosition - self.getRampingDistance();
			return max(s0, lLimit);
		else:
			s0=self.startPosition + self.getRampingDistance();
			return min(s0, hLimit)
		
	def getEndPosition(self):
		lLimit, hLimit = self.trough.getAreaLimits();
		if self.stopPosition > self.startPosition:
			s0=self.stopPosition + self.getRampingDistance();
			return min(s0, hLimit)
		else:
			s0=self.stopPosition - self.getRampingDistance();
			return max(s0, lLimit);

	def getVelocity(self):
		return self.velocity;
	
	def getMotorSpeed(self):
		return self.trough.getSpeed();
	
	#Note: the unit of speed here is per second
	def setMotorSpeed(self, speed):
		self.trough.setSpeed(speed*60.0);

	def check(self):
#		self.velocity = self.velocity;
#		self.startPosition = self.startPosition;
#		self.stopPosition = self.stopPosition;
		return;

	def backupMotor(self):
		self.motorVelo = self.trough.getSpeed();

	def restoreMotor(self):
		self.trough.setSpeed(self.motorVelo);
		
	def build(self):
		self.check();
		
		#First, use the maxium speed to go to the start position
		maxSpeed = self.trough.getSpeedLimits()[1]/60.0;
		self.setMotorSpeed(maxSpeed);
		sleep(2);
		self.trough.synchronousAreaMoveTo( self.getStartPosition() );
		sleep(2);
		
		#Second: set the motor speed as requested
		self.setMotorSpeed(self.velocity);
		sleep(2);

	def kickoff(self):
#		self.motor.moveTo( self.getEndPosition(), self.putListener);
#		testMotor1.asynchronousMoveTo(self.getEndPosition());
		self.trough.asynchronousAreaMoveTo(self.getEndPosition());

	def abortScan(self):
		self.restoreMotor();

#A function to run the isotherm scan on Trough
	def isoscan(self, startPosition, stopPosition,scanTime, pointTime):
#		self = IsothermScanControlClass("fastController", trough);
		#    isoArea = IsothermAreaDeviceClass("isoArea", trough);
		isoDetector=IsothermDetector("isoDetector", self.trough);
		isoDetector.timeout=100;
		isoDetector.reset();
		
		
		isoData = DataBufferDeviceClass("isoData", isoDetector);
		isoData.reset();
		isoData.setIndexChannel(self.indexChannel);
		
		self.setAcceleration(10);
		self.setScanRange(startPosition, stopPosition);
		self.setTime(scanTime, pointTime);
		
		numPoint = self.getNumberOfPoint();
		positions1=self.getEstimatedPositions();
		
		step=self.getStep();
		
		
		print "Building the scan ..."
#		print "---> Debug: Current Time: " + ctime();
		self.build();
		
		print "Start ramping ..."
#		print "---> Debug: Current Time: " + ctime();
		self.kickoff();
		
		sleepTime = self.getRampingTime();
		if sleepTime >=10:
			sleep(sleepTime-10);
		
		print "...Start scan"
#		print "---> Debug: Current Time: " + ctime();
#		print "---> Debug: Current Position: " + str(self.trough.getArea());
		
#		print "****************** Trigger the detector";
	#	pos isoDetector [pointTime, numPoint]
		isoDetector.asynchronousMoveTo([pointTime, numPoint])
		
#		print "****************** Scan the data";
#		scan([isoData, 0, numPoint-1, 1]);
		try:
			theScan = ConcurrentScan([isoData, 0, numPoint-1, 1]);
			theScan.runScan();
		except:
			exceptionType, exception, traceback=sys.exc_info();
			logger.fullLog(None, "Error occurs at FastEnergyDeviceClass.cvscan", exceptionType, exception, traceback, True);


#Usage:
#isoController = IsothermScanControlClass("isoController", trough);
#isoController.isoscan(startPosition, stopPosition,scanTime, pointTime);

#isoscan 100 400 300 10
