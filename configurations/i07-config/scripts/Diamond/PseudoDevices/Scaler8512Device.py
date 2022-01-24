from time import sleep
from java import lang
from gda.device.scannable import ScannableMotionBase
from gda.device import Scannable
from gda.epics import CAClient

from gda.device import Detector
from gda.device.detector import DetectorBase

#A Class to set all the detector's integration time in one go
class DetectorIntegrationsDevice(ScannableMotionBase):
	def __init__(self, name, detectorList):
		self.setName(name);
		self.setInputNames([name]);
		self.setExtraNames([]);
		self.setLevel(7);
		self.setOutputFormat(["%20.8f"]);
		
		self.integrationTime=1;
		self.detectorList=[];
		self.detectorList.extend( detectorList );

	def addDetectors(self, detectorList):
		self.detectorList.extend( detectorList );
		
	def removeDetectors(self, detectorList):
		for d in detectorList:
			while d in self.detectorList:
				self.detectorList.remove( d );
		
	def setCollectionTime(self, t):
		self.integrationTime = t;
		for d in self.detectorList:
			print d.getName();
			d.setCollectionTime(self.integrationTime);
			
	#Scannable Implementations
	def getPosition(self):
		for d in self.detectorList:
			if d.getCollectionTime() != self.integrationTime:
				print "Inconsistant ingetration time: " +d.getName() + ", " + str( d.getCollectionTime() );
				return;
			
		return self.integrationTime;
	
	def asynchronousMoveTo(self,newPos):
		self.setCollectionTime(newPos);

	def isBusy(self):
		for d in self.detectorList:
			if d.getStatus() == Detector.BUSY:
				return True;
		return False;


#The Class for creating a Scaler channel monitor directly from EPICS PV
#For 8512 Scaler Card used in I06 only. This scaler card is not supported by EPICS scaler record
class Scaler8512ChannelEpicsDeviceClass(ScannableMotionBase):
	def __init__(self, name, strChTP, strChCNT, strChSn):
		self.setName(name);
		self.setInputNames([name]);
		self.setExtraNames([]);
#		self.Units=[strUnit];
		self.setLevel(7);
		self.setOutputFormat(["%20.8f"]);
		self.chTP=CAClient(strChTP);
		self.chCNT=CAClient(strChCNT);
		self.chSn=CAClient(strChSn);
		self.tp = -1;

#		self.setTimePreset(time)

	def atScanStart(self):
		if not self.chTP.isConfigured():
			self.chTP.configure()
		if not self.chCNT.isConfigured():
			self.chCNT.configure()
		if not self.chSn.isConfigured():
			self.chSn.configure()

	#Scannable Implementations
	def getPosition(self):
		return self.getCount();
	
	def asynchronousMoveTo(self,newPos):
		self.setCollectionTime(newPos);
		self.collectData();

	def isBusy(self):
		return self.getStatus()

	def atScanEnd(self):
		if self.chTP.isConfigured():
			self.chTP.clearup()
		if self.chCNT.isConfigured():
			self.chCNT.clearup()
		if self.chSn.isConfigured():
			self.chSn.clearup()


	#Scaler 8512 implementations		
	def getTimePreset(self):
		if self.chTP.isConfigured():
			newtp = self.chTP.caget()
		else:
			self.chTP.configure()
			newtp = float(self.chTP.caget())
			self.chTP.clearup()
		self.tp = newtp
		return self.tp

	#Set the Time Preset and start counting automatically
	def setTimePreset(self, newTime):
		self.tp = newTime
		newtp = newTime;
		if self.chTP.isConfigured():
			tp = self.chTP.caput(newtp)
		else:
			self.chTP.configure()
			tp = self.chTP.caput(newtp)
			self.chTP.clearup()
#		Thread.sleep(1000)	

	def getCount(self):
		if self.chSn.isConfigured():
			output = self.chSn.caget()
		else:
			self.chSn.configure()
			output = self.chSn.caget()
			self.chSn.clearup()
		return float(output)


	#Detector implementations
	
	#Tells the detector to begin to collect a set of data, then returns immediately.
	#public void collectData() throws DeviceException;
	#Set the Time Preset and start counting automatically
	def collectData(self):
		#self.setTimePreset(self.tp)
		if self.chCNT.isConfigured():
			tp = self.chCNT.caput(1)
		else:
			self.chCNT.configure()
			tp = self.chCNT.caput(1)
			self.chCNT.clearup()
#		Thread.sleep(1000)	

	#Tells the detector how long to collect for during a call of the collectData() method.
	#public void setCollectionTime(double time) throws DeviceException;
	def setCollectionTime(self, newTime):
		self.setTimePreset(newTime)
		
	#Returns the latest data collected.
	#public Object readout() throws DeviceException;
	def getCollectionTime(self):
		nc=self.getTimePreset()
		return nc

	#Returns the current collecting state of the device.
	# return ACTIVE (1) if the detector has not finished the requested operation(s), 
	#        IDLE(0) if in an completely idle state and 
	#        STANDBY(2) if temporarily suspended.
	#public int getStatus() throws DeviceException;
	def getStatus(self):
		if self.chCNT.isConfigured():
			self.stauts = self.chCNT.caget()
		else:
			self.chCNT.configure()
			self.stauts = self.chCNT.caget()
			self.chCNT.clearup()	
		if self.stauts == '0': #still counting, Busy
			return 0
		else:
			return 1


