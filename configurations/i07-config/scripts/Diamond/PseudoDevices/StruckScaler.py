#The GDA Classes for the an ADC-controlled Scaler Card

from time import sleep
#import math

from gda.device.detector import DetectorBase
from gda.device.Detector import BUSY, IDLE
from gda.epics import CAClient;


#from gov.aps.jca.event import PutEvent;
from gov.aps.jca.event import PutListener;
from gov.aps.jca import CAStatus;

from Diamond.Objects.Shutter import ShutterDeviceClass


class StructScalerGdaClass(DetectorBase):
	"""The class holds a scaler wrapping a scalar card. It will return 
	the counts from a number of channels given in channelList.
	"""
	def __init__(self, name, scaler):
		self.setName(name);
#		self.setInputNames(['IngetrationTime']);

		self.scaler=scaler;
		
		self.channels = self.scaler.getTotalChans();
	
		en=[]; of=["%8.3f"];
		for i in range(self.channels):
			en.append("Channel" + str(i+1));
			of.append("%20.12f");
		self.setExtraNames(en);
		self.setOutputFormat(of);
#		self.Units=[strUnit];
		self.setLevel(7);


# Detector Implementation
	def getCollectionTime(self):
		return self.scaler.getCollectionTime();

	def setCollectionTime(self, newExpos):
		self.scaler.setCollectionTime(newExpos);

	def collectData(self):
		self.scaler.collectData();

	def readout(self):
		return self.scaler.readout();

	def getStatus(self):
		return self.scaler.getStatus();
	
	def createsOwnFiles(self):
		return False;
	
	def toString(self):
		return self.getName() + ": Integration= " + str(self.getCollectionTime()) + ", Count=" + str(self.getPosition());

	def toFormattedString(self):
		return self.getName() + ": Integration= " + str(self.getCollectionTime()) + ", Count=" + str(self.getPosition());
		

class StructScalerGdaChannelClass(StructScalerGdaClass, ShutterDeviceClass):
	def __init__(self, name, scaler, channel, shutterName=None):
		StructScalerGdaClass.__init__(self, name, scaler);
		ShutterDeviceClass.__init__(self, shutterName);

		self.setExtraNames([]);
		self.setOutputFormat(["%20.12f"]);

		self.channel = channel;
	
#Detector Implementation
	def collectData(self):
		self.openShutter()
		self.scaler.collectData();
		
	def readout(self):
#		return self.getCounts();
		self.closeShutter()
		return self.scaler.readout(self.channel);

#	def prepareForCollection(self):
#		self.openShutter();

	def endCollection(self):
		self.closeShutter();

#Scannable Implementation
	def stop(self):
		self.closeShutter();

	def atCommandFailure(self):
		self.closeShutter();

		
#	def atScanEnd(self):
#		self.closeShutter();


#The Class for creating a Scaler channel monitor directly from EPICS PV
#For 8512 Scaler Card used in I06 only. This scaler card is not supported by EPICS scaler record
class StructScalerEpicsClass(DetectorBase):
	SCALER_EPICS_STATUS_DONE, SCALER_EPICS_STATUS_BUSY = range(2);
	SCALER_EPICS_STATUS_STRINGS = ['Done', 'Busy'];
	
	SCALER_MODE_SINGLE, SCALER_MODE_CONTINUOUS = range(2);
	SCALER_MODE_STRINGS = ['SINGLE', 'CONTINUOUS'];

	SCALER_CHANNEL = 8;
	#CA Put Callback listener that handles the callback event
	class CaputCallbackListenerClass(PutListener):
		def __init__ (self, scaler):
			self.scaler = scaler;
			
		def putCompleted(self, event):
			if event.getStatus() != CAStatus.NORMAL:
				print 'Scaler count failed!'
				print 'Failed source: ' + event.getSource().getName();
				print 'Failed stuatus: ' + event.getStatus();
			else:
#				print 'The scaler calls back, Counting Done.';
				self.scaler.scalerStatus = IDLE;
			return;

		def getStatus(self):
				return self.scaler.magnetStatus;
			
	
	def __init__(self, name, rootPV):
		self.scalerRootPV = rootPV;
		self.setName(name);
#		self.setInputNames(['IngetrationTime']);
		
		en=[]; of=["%6.4f"];
		for i in range(StructScalerEpicsClass.SCALER_CHANNEL):
			en.append("Channel" + str(i+1));
			of.append("%20.12f");
		self.setExtraNames(en);
		self.setOutputFormat(of);
#		self.Units=[strUnit];
		self.setLevel(7);
		
		self.exposureTime = None;
		self.scalerStatus = IDLE; #GDA side status

		self.epicsStatus = StructScalerEpicsClass.SCALER_EPICS_STATUS_DONE; # Epics side status
		self.mode = StructScalerEpicsClass.SCALER_MODE_SINGLE; # Epics side running mode

		self.counts = [0] * StructScalerEpicsClass.SCALER_CHANNEL;
		
		self.chIT = None;
		self.chStart = None;
		self.chMode = None;
		self.chCounts = [None] * StructScalerEpicsClass.SCALER_CHANNEL;
		
		self.setup();
		self.putListener = StructScalerEpicsClass.CaputCallbackListenerClass(self);


	def __del__(self):
		self.cleanChannel(self.chIT);
		self.cleanChannel(self.chStart);
		self.cleanChannel(self.chMode);

		for i in range(StructScalerEpicsClass.SCALER_CHANNEL):
			self.cleanChannel(self.chCounts[i]);
		

	#pvRootScaler   = "BL07I-EA-ADC-01";
	#pvScalerIT     = "BL07I-EA-ADC-01:INTTIME";
	#pvScalerStart  = "BL07I-EA-ADC-01:STARTCOUNT";
	#pvScalerCount1 = "BL07I-EA-ADC-01:CH1:SUM";
	#pvScalerCount2 = "BL07I-EA-ADC-01:CH2:SUM";
	#pvScalerMode   = "BL07I-EA-ADC-01:MODE";
	
	def setup(self):
#		Epics PVs for changing the magnet X, Y, Z field value:
		self.chIT=CAClient(self.scalerRootPV+":INTTIME"); self.configChannel(self.chIT);
		self.chStart=CAClient(self.scalerRootPV+":STARTCOUNT"); self.configChannel(self.chStart);
		self.chMode=CAClient(self.scalerRootPV+":MODE"); self.configChannel(self.chMode);
		
		for i in range(StructScalerEpicsClass.SCALER_CHANNEL):
			self.chCounts[i]=CAClient(self.scalerRootPV+":CH" + str(i+1)+ ":SUM"); self.configChannel(self.chCounts[i]);

		
	def configChannel(self, channel):
		if not channel.isConfigured():
			channel.configure();

	def cleanChannel(self, channel):
		if channel.isConfigured():
			channel.clearup();

#	Epics level operation:
	def getIntegrationTime(self):
		return float( self.chIT.caget());

	def setIntegrationTime(self, newTime):
		self.chIT.caput(newTime);

	def startCounting(self):
		"""Start the counting """
		if self.getScalerStatus() != StructScalerEpicsClass.SCALER_EPICS_STATUS_STRINGS[StructScalerEpicsClass.SCALER_EPICS_STATUS_DONE]:
			print "Scaler is busy";
			return False;
		
		if self.getScalerMode() != StructScalerEpicsClass.SCALER_MODE_STRINGS[StructScalerEpicsClass.SCALER_MODE_SINGLE]:
			print "Scaler is currently in CONTINUOUSLY counting mode. GDA will change it to SINGLE counting mode";
			self.setScalerMode(StructScalerEpicsClass.SCALER_MODE_SINGLE);
			sleep(1);
		
#		Setup the the caput call back listener so that will be notified when move done 
		self.scalerStatus = BUSY;
		self.chStart.getController().caput(self.chStart.getChannel(), 1, self.putListener);
		return True;

	def getScalerMode(self):
		self.mode = int( float(self.chMode.caget()) );
		return StructScalerEpicsClass.SCALER_MODE_STRINGS[self.mode];

	def setScalerMode(self, newMode):
		if type(newMode).__name__ == 'int':
			self.mode = newMode;
		elif type(newMode).__name__ == 'str' and newMode in StructScalerEpicsClass.SCALER_MODE_STRINGS:
				self.mode = StructScalerEpicsClass.SCALER_MODE_STRINGS.index(newMode);
		else:
			print "Unknown mode";
			return;
		self.chMode.caput(self.mode);

	def getScalerStatus(self):
		self.epicsStatus =int( float(self.chStart.caget()) );
		return StructScalerEpicsClass.SCALER_EPICS_STATUS_STRINGS[self.epicsStatus];
		
	def getCounts(self):
		for i in range(StructScalerEpicsClass.SCALER_CHANNEL):
			self.counts[i] = float( self.chCounts[i].caget());
		return self.counts;

	def getCount(self, channelNumber):
		self.counts[channelNumber] = float( self.chCounts[channelNumber].caget());
		return self.counts[channelNumber];

#Detector Implementation
	def getCollectionTime(self):
		self.exposureTime=self.getIntegrationTime();
		return self.exposureTime;

	def setCollectionTime(self, newExpos):
		self.exposureTime = newExpos;
		self.setIntegrationTime(newExpos);

	def collectData(self):
		self.startCounting();

	def readout(self):
		return self.getCounts();
#		return self.getCount(0);

	def createsOwnFiles(self):
		return False;
	

#Scannable Implementation
	def getPosition(self):
		return self.readout();

	def asynchronousMoveTo(self,newExpos):
		self.setCollectionTime(newExpos)
		self.collectData();

	def getStatus(self):
		return self.scalerStatus;
	
	def toString(self):
		return self.getName() + ": Integration= " + str(self.getCollectionTime()) + ", Count=" + str(self.getPosition());


class StructScalerEpicsChannelClass(StructScalerEpicsClass):
	
	def __init__(self, name, rootPV, channel):
		StructScalerEpicsClass.__init__(self, name, rootPV);

		self.setExtraNames([]);
		self.setOutputFormat(["%20.12f"]);

		self.channel = channel;

# Detector Implementation
	def readout(self):
#		return self.getCounts();
		return self.getCount(self.channel);


#pvRootScaler   = "BL07I-EA-ADC-01";

#ionsc = AdcScalerClass('ionsc', pvRootScaler);
#ionsc1 = AdcScalerChannelClass('ionsc1', pvRootScaler, channel=0);
#ionsc1.setUsedByDefault(False);


# BL07I-EA-DET-01:SCALER.CNT     Done 
#BL07I-EA-DET-01:SCALER.S1      9.61967e+06 
#BL07I-EA-DET-01:SCALER.TP      4 
#BL07I-EA-DET-01:SCALER.CONT    AutoCount 

#eh1sc = StructScalerGdaClass("eh1scaler", struck1);
#eh1sc1 = StructScalerGdaChannelClass("eh1scaler", struck1, 0);
#eh1sc2 = StructScalerGdaChannelClass("eh1scaler", struck1, 1);
#eh1sc3 = StructScalerGdaChannelClass("eh1scaler", struck1, 2);

