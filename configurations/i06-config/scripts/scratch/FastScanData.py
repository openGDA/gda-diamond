
from time import sleep, ctime;

import jarray;

from gda.epics import CAClient;
from gda.device.scannable import PseudoDevice;
from org.eclipse.january.dataset import DatasetFactory

class FastEnergyDeviceClass(PseudoDevice):
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
		
	def setDelay(self, delay):
		self.delay = delay;

#PseudoDevice Implementation
	def atScanStart(self):
#		print "At Scan Start"
		if not self.fesController.checkMotorReady():
			raise Exception("Fast energy scan CAN NOT be performed. Please check both PGM and ID are ready!");
		
		if self.fesController.getScanStatus() not in ["Scan complete", "Scan aborted"]: #Not in Ready status
			raise Exception("Fast energy scan CAN NOT be performed because of wrong EPICS status!");
			
		#setup scan parameters
#		self.fesController.setEnergyRange(startEnergy, endEnergy);
#		self.fesController.setTime(scanTime, pointTime);
		
		#trigger the scan
		self.fesController.buildScan();
		print "Start building the fast scan..."
	
		while not self.fesController.isBuilt():
			print '... Scanning is building.'
			sleep(2);
		print 'Fast Scan Built'
	
		print "...Start scan"
		self.fesController.startScan();
		self.fesDetector.reset();
		self.indexPosition = 0;
		sleep(2);

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
#		print "---> Debug: Energy device moves forward; " + str(newPos);
#		print "---> Debug: Energy Device asking new data at: " + ctime();
		
	def isBusy(self):
#		return self.fesDetector.isBusy();
		if self.fesDetector.isDataAvailable():
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
		self.fesController.abortScan();


#from Diamond.PseudoDevices.EpicsScanDataDevice import EpicsScanDataDeviceClass, SingleChannelEpicsScanDataDeviceClass;
#######################################################
EpicsMCAWaveformDataDeviceClass("d1", "BL07I-EA-DET-01:MCA-01", 1);

class EpicsMCAWaveformDataDeviceClass(PseudoDevice):
	
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
	
	"""
	def setupEpics(self, rootPV):
		#Epics PV for the Number of elements available (Head of waveform)

#		Epics PVs for the channels:
		self.chData=[];

		for i in range(self.numberOfDetectors):
			self.chData.append( CAClient(rootPV + ":mca" + str(i+1)));
			self.configChannel(self.chData[i]);

		self.chHead=CAClient(rootPV + ":mca1.NORD");  self.configChannel(self.chHead);
		
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
	
	def getNewEpicsData(self, offset, size):
		#To check the head
		head=self.getHead();
		if offset > head:
			print " No new data available. Offset exceeds Head(" + str(head) + ").";
			return False;
		
		print "New data available, Offset does not exceed Head(" + str(head) + ").";

		la=[];
		#To get the waveform data from EPICS
		print "---> Debug: get waveform: start at: " + ctime();
		for i in range(self.numberOfDetectors):
#			self.data[i]=self.chData[i].cagetArrayDouble();
#TODO: make sure that the self.data[i] is a list
#			self.data[i]=self.chData[i].cagetArrayDouble();
			self.data[i]=self.chData[i].getController().cagetDoubleArray(self.chData[i].getChannel(), head+1);
#			print "The type of subarray data from caget is: ", type(self.data[i]);
#			print "The subarray data from caget is: ", self.data[i];
			la.append(self.data[i]);
		print "---> Debug: get waveform: end at: " + ctime();
		
		ds=DatasetFactory.createFromObject(la) #ds is a new DataSet with dimension [numberOfDetectors, size];
		
		self.dataset = ds;
		return True;

# PseudoDetector Implementation
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

