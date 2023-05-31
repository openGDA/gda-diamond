from gda.device.scannable import ScannableMotionBase
from gda.epics import CAClient

from gda.device import Detector
from i06shared import installation
from uk.ac.diamond.daq.concurrent import Async
from random import Random
from java.util.concurrent import TimeUnit

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
		self.setLevel(7);
		self.setOutputFormat(["%20.8f"]);
		self.chTP=CAClient(strChTP);
		self.chCNT=CAClient(strChCNT);
		self.chSn=CAClient(strChSn);
		self._busy = False
		self.future = None
		self.maxDataValue = 1000000
		self.minDataValue = 0
		
#		self.setTimePreset(time)

	def atScanStart(self):
		if installation.isLive():
			if not self.chTP.isConfigured():
				self.chTP.configure()
			if not self.chCNT.isConfigured():
				self.chCNT.configure()
			if not self.chSn.isConfigured():
				self.chSn.configure()

	#Scannable Implementations
	def getPosition(self):
		if installation.isLive():
			if self.chSn.isConfigured():
				output = float(self.chSn.caget())
			else:
				self.chSn.configure()
				output = float(self.chSn.caget())
				self.chSn.clearup()
			return output
		else:
			if self.future:
				return self.future.get()
			else:
				return "NOT AVAILABLE"
		
	def asynchronousMoveTo(self,new_pos):
		if installation.isLive():
			self.setTimePreset(new_pos);
			if self.chCNT.isConfigured():
				self.chCNT.caput(1)
			else:
				self.chCNT.configure()
				self.chCNT.caput(1)
				self.chCNT.clearup()
		else:
			self._busy = True
			collection_time_millisecond = float(new_pos) * 1000.0
			self.future =  Async.schedule(self.acquireData, collection_time_millisecond, TimeUnit.MILLISECONDS)
			
	def acquireData(self):
		return Random().randint(self.minDataValue, self.maxDataValue)

	def isBusy(self):
		if installation.isLive():
			if self.chCNT.isConfigured():
				status = int(self.chCNT.caget())
			else:
				self.chCNT.configure()
				status = int(self.chCNT.caget())
				self.chCNT.clearup()	
			return status
		else:
			return self._busy;
		
	def waitWhileBusy(self):
		self.future.get()
		self._busy = False
		
	def atScanEnd(self):
		if installation.isLive():
			if self.chTP.isConfigured():
				self.chTP.clearup()
			if self.chCNT.isConfigured():
				self.chCNT.clearup()
			if self.chSn.isConfigured():
				self.chSn.clearup()


	#Scaler 8512 implementations		
	def getTimePreset(self):
		if installation.isLive():
			if self.chTP.isConfigured():
				newtp = float(self.chTP.caget())
			else:
				self.chTP.configure()
				newtp = float(self.chTP.caget())
				self.chTP.clearup()
			return newtp
		else:
			return self.preset_time

	#Set the Time Preset and start counting automatically
	def setTimePreset(self, new_time):
		if installation.isLive():
			if self.chTP.isConfigured():
				self.chTP.caput(new_time)
			else:
				self.chTP.configure()
				self.chTP.caput(new_time)
				self.chTP.clearup()
		else:
			self.preset_time = new_time





