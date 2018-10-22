from time import sleep
import cPickle as pickle
import os;

from gda.epics import CAClient;
from gda.data import NumTracker;

from PilatusInfo import PilatusInfo;

from Diamond.Comm.SocketDevice import SingleSessionSocketDeviceClass
from Diamond.Comm.SocketDevice import SocketError

class Pilatus(object):
	def __init__(self, name):
		self.name=name;
		self.detectorModel = None;
		self.detectorInfo = None;
		
		self.exposureTime = 0
		self.exposurePeriod = 1;
		
		self.status = PilatusInfo.DETECTOR_STATUS_STANDBY;

		self.filePath = None;
		self.filePrefix = 'pilatusImage';
		self.fileFormat = "%s%s%d.tif";
		self.numImages = 1;
		self.gain = 0;
		self.thresholdEnergy = 5000;
		

		self.runs=NumTracker(self.filePrefix);
		self.fileNumber = self.runs.getCurrentFileNumber();

		
	def turnOn(self):
		self.status = PilatusInfo.DETECTOR_STATUS_IDLE;
		
	def turnOff(self):
		self.status = PilatusInfo.DETECTOR_STATUS_STANDBY;

	def setThreshold(self, newGain, newThresholdEnergy):
		raise NotImplementedError("This is an abstract method that must be implemented by subclass.");
		return;
	
	def getThreshold(self):
		raise NotImplementedError("This is an abstract method that must be implemented by subclass.");
		return;
	
	def setExposurePeriod(self, newExpp):
		raise NotImplementedError("This is an abstract method that must be implemented by subclass.");
		return;

	def getExposurePeriod(self):
		raise NotImplementedError("This is an abstract method that must be implemented by subclass.");
		
	def start(self):
		return;

	def getDetectorInfo(self):
		return self.detectorInfo;

	def setNumOfImages(self, number):
		raise NotImplementedError("This is an abstract method that must be implemented by subclass.");
		return;
	
	def getNumOfImages(self):
		return self.numImages;

	def setFilePath(self, newFilePath):
		raise NotImplementedError("This is an abstract method that must be implemented by subclass.");
		return;
	
	def getFilePath(self):
		return self.filePath

	def setFilePrefix(self, filePrefix):
		self.filePrefix = filePrefix;
#		self.runs=NumTracker(self.filePrefix);
#		self.fileNumber = self.runs.getCurrentFileNumber();
		
	def getFilePrefix(self):
		return self.filePrefix;

	def getFileNumber(self):
		self.fileNumber = self.runs.getCurrentFileNumber();
		return self.fileNumber;

	def getFileFromat(self):
		return self.fileFormat;

	def getFullFileName(self):
		"""Returns file path of the LAST CREATED image"""
		self.fileNumber=self.getFileNumber();
		
		fileName=self.filePrefix + "%04.0f" %(self.fileNumber) + self.fileFormat[-4:];
		return os.path.join(self.filePath, fileName); 
	
	def getCurrentFullFileName(self):
		"""Returns file path of the next image to be created"""
		self.fileNumber=self.getFileNumber();
		return self.filePath + self.filePrefix + "%04.0f" %(self.fileNumber+1) + self.fileFormat[-4:]

	def getNextFullFileName(self):
		return self.getCurrentFullFileName();

	def getMultipleFullFileNames(self):
		"""Returns a list of image names from multiple shot"""
		self.fileNumber=self.getFileNumber();
		names = [];
		for i in range(self.numImages):
			names.append(self.filePath + self.filePrefix + "%04.0f" %(self.fileNumber) + "_%05.0f" %(i) + self.fileFormat[-4:]);
		return names;

# Palitus Detector Interface Implementation
	def getCollectionTime(self):
		raise NotImplementedError("This is an abstract method that must be implemented by subclass.");
		return;

	def setCollectionTime(self, newExpos):
		raise NotImplementedError("This is an abstract method that must be implemented by subclass.");
		return;

	def collectData(self):
		raise NotImplementedError("This is an abstract method that must be implemented by subclass.");
		return;

	def readout(self):
		return self.getFullFileName();

	def getStatus(self):
		return self.status;
	

class PilatusOverSocket(Pilatus, SingleSessionSocketDeviceClass):
	terminators = '\n\x15\x18';
	def __init__(self, name):
		Pilatus.__init__(self, name);
		self.detectorInfo = 'Pilatus Over Socket';
		
		self.setFilePrefix('pilatusImage');

		serverHost = 'localhost';
		serverPort = 41234;
#		super(SockteDeviceClass, self).__init__(self, serverHost, serverPort);
		SingleSessionSocketDeviceClass.__init__(self, serverHost, serverPort);

	def turnOn(self):
		self.status = PilatusInfo.DETECTOR_STATUS_IDLE;
		self.connect();
	
	def turnOff(self):
		self.send("exit ");
		self.disconnect();

	def getNumOfImages(self):
		reply = self.sendAndReply('nimages');
#		The reply should be something like: '15 OK N images (frames) set to: 1'
		print reply;
		rlist = reply.split(' ',9);
		if rlist[1] == 'OK':
			self.numImages = int(rlist[7].rstrip(PilatusOverSocket.terminators));
		else:
			print "Get detector information failed.";
		return self.numImages;

	def setNumOfImages(self, number):
		self.numImages = number;
		self.sendAndReply('nimages ' + str(number));
		return self.numImages;

	def setFilePath(self, newFilePath):
		"""Set file path"""
		self.filePath = newFilePath;
		self.sendAndReply('imgpath ' + newFilePath);
	
	def getFilePath(self):
		if self.filePath != None:
			return self.filePath;
		
		reply = self.sendAndReply('imgpath ');
		print reply;
#		The reply should be something like: '10 OK' /home/det/p2_det/images/'
		rlist = reply.split(' ',3);
		if rlist[1] == 'OK':
			self.filePath = rlist[2].rstrip(PilatusOverSocket.terminators);
		else:
			print "Get detector information failed.";
		return self.filePath;

	def setFilePrefix(self, filePrefix):
		self.filePrefix = filePrefix;
		self.runs=NumTracker(self.filePrefix);
		self.fileNumber = self.runs.getCurrentFileNumber();
		
	def getFileNumberOld(self):
		"""Restore the pickled file number for persistence"""
		try:
			inStream = file(self.filePath+'simPilatusFileNumber.txt', 'rb');
			self.fileNumber = pickle.load(inStream);
			inStream.close();
		except IOError:
			print "No previous pickled file numbers. Create new one";
			self.fileNumber = 0;
		return self.fileNumber;
	
	def saveFileNumberOld(self):
		"""Save the file number for persistence"""
		outStream = file(self.filePath+'simPilatusFileNumber.txt', 'wb');
		try:
			#Pickle the file number and dump to a file stream
			pickle.dump(self.fileNumber, outStream);
			outStream.close();
		except IOError:
			print "Can not preserve file numbers.";

# Palitus Detector Interface Implementation
	def getCollectionTime(self):
		reply = self.sendAndReply("exptime");
#		The reply should be something like: '15 OK   Exposure time set to: 2.000000 sec.'
		print reply;
		rlist = reply.split(' ',9);
		if rlist[1] == 'OK':
			self.exposureTime = float(rlist[8]);
		else:
			print "Get detector information failed.";
			
		return self.exposureTime;

	def setCollectionTime(self, newExpos):
		reply = self.sendAndReply("exptime " + str(newExpos));
		print reply;
		rlist = reply.split(' ',9);
		if rlist[1] == 'OK':
			self.exposureTime = float(rlist[8]);
		else:
			print "Set detector information failed.";
		return self.exposureTime;

	def collectData(self):
#		newFileName = self.filePrefix + "%04.0f" % self.fileNumber + self.fileFormat[-4:]
		newFileName = self.getNextFullFileName();
		self.status = PilatusInfo.DETECTOR_STATUS_BUSY;
		try:
			reply01 = self.sendAndReply('exposure ' + newFileName);
			reply02 = self.receive();
			print reply01;
			print reply02;
			self.runs.incrementNumber();
		except SocketError, msg:
			print 'Socket Connection Error: ' + str(msg);

		self.status = PilatusInfo.DETECTOR_STATUS_IDLE;
		return;
	

class PilatusOverEpics(Pilatus):
	def __init__(self, name):
		Pilatus.__init__(self, name);
		self.detectorInfo = 'Pilatus Over Epics';

		self.chAcquire=None;
		self.chAabort=None;

		self.chFilePath=None;
		self.chFileName=None;
		self.chFileFormat=None;
		self.chFileNumber=None;

		self.chExposureTime=None;
		self.chExposurePeriod=None;
		self.chNumImages=None;

		self.chGain=None;
		self.chThresholdEnergy=None;
		
	def setup(self, rootPV):
		self.ClientRoot = rootPV;
		
		self.chAcquire=CAClient(self.ClientRoot+':Acquire'); self.chAcquire.configure();
		self.chAabort=CAClient(self.ClientRoot+':Abort'); self.chAabort.configure();

		self.chFilePath=CAClient(self.ClientRoot+':FilePath'); self.chFilePath.configure();
		self.chFileName=CAClient(self.ClientRoot+':Filename'); self.chFileName.configure();
		self.chFileNumber=CAClient(self.ClientRoot+':FileNumber'); self.chFileNumber.configure();
		self.chFileFormat=CAClient(self.ClientRoot+':FileFormat'); self.chFileFormat.configure();

		self.chNumImages=CAClient(self.ClientRoot+':NImages');	self.chNumImages.configure();
		self.chExposureTime=CAClient(self.ClientRoot+':ExposureTime'); self.chExposureTime.configure();
		self.chExposurePeriod=CAClient(self.ClientRoot+':ExposurePeriod'); self.chExposurePeriod.configure();

		self.chThresholdEnergy=CAClient(self.ClientRoot+':ThresholdEnergy'); self.chThresholdEnergy.configure();
		self.chGain=CAClient(self.ClientRoot+':Gain'); self.chGain.configure();

		self.chNumImages.caput(1);

		self.numImages = 1;
		self.fileFormat=self.chFileFormat.caget();

	def rebootIOC(self, iocRootPV):
		#Use the EDM screen reboot button: for example: "caput BL07I-EA-IOC-03:SYSRESET 1"
		cmd = "caput " + iocRootPV + ":SYSRESET 1";
		print cmd;
		os.system(cmd);
		sleep(10);
		
	def setNumOfImages(self, number):
		self.numImages = number;
		self.chNumImages.caput(number);

	def setFilePath(self, newFilePath):
		"""Set file path"""
		self.filePath = newFilePath;
		self.chFilePath.caput(self.filePath);
	
	def getFilePath(self):
		self.filePath = self.chFilePath.caget();
		return self.filePath
		
	def setFilePrefix(self, filePrefix):
		self.filePrefix = filePrefix
		self.chFileName.caput(self.filePrefix);
		self.fileNumber = self.getFileNumber();
		
	def getFilePrefix(self):
		self.filePrefix = self.chFileName.caget();
		return self.filePrefix;

	def getFileNumber(self):
		self.fileNumber = int(float(self.chFileNumber.caget())) -1;
		return self.fileNumber;
	
#	Only to deal with the epics bug, no need if the bug fixed
#	def getFullFileName(self):
#		"""Returns file path of the LAST CREATED image"""
#		self.fileNumber=self.getFileNumber();
#		return self.filePath + self.filePrefix + "%04.0f" % (self.fileNumber) + self.fileFormat[-4:]


# Palitus Detector Interface Implementation
	def getCollectionTime(self):
		self.exposureTime = float(self.chExposureTime.caget());
		return self.exposureTime;

	def setCollectionTime(self, newExpos):
		if self.exposureTime != newExpos:	#send command to change exposure time if required
			self.exposureTime = newExpos;
			self.chExposureTime.caput(self.exposureTime);
		return self.exposureTime;

	def collectData(self):
		self.chAcquire.caput(1);
		return;

	def setThreshold(self, newGain, newThresholdEnergy):
		self.chGain.caput(PilatusInfo.GAIN_THRESHOLD.index(newGain));
		self.chThresholdEnergy.caput(newThresholdEnergy);
		return;
	
	def getThreshold(self):
		self.gain = int( float( self.chGain.caget()) );
		self.thresholdEnergy = float( self.chThresholdEnergy.caget());
		print 'Gain: ' + PilatusInfo.EPICS_GAIN_THRESHOLD[self.gain] + ',  Threshold Energy: ' + str(self.thresholdEnergy);
		return [self.gain, self.thresholdEnergy];
	
	def setExposurePeriod(self, newExpp):
		self.exposurePeriod = newExpp;
		self.chExposurePeriod.caput(newExpp);
		return;

	def getExposurePeriod(self):
		self.exposurePeriod = float( self.chExposurePeriod.caget());
		return self.exposurePeriod;


	def getStatus(self):
		isbusy=int(float(self.chAcquire.caget()));
		isbusy=int(float(self.chAcquire.caget()));
		isbusy=int(float(self.chAcquire.caget()));
		if isbusy == 0:
			self.status = PilatusInfo.DETECTOR_STATUS_IDLE;
		else:
			self.status = PilatusInfo.DETECTOR_STATUS_BUSY;
			
		return self.status;
	
# Pilatus Detector Factory
class PilatusFactory(object):
	products = [];
	classByType = { PilatusInfo.PILATUS_TYPE_100K_EPICS : PilatusOverEpics,
					PilatusInfo.PILATUS_TYPE_100K_SOCKET: PilatusOverSocket,
					PilatusInfo.PILATUS_TYPE_2M_EPICS   : PilatusOverEpics,
					PilatusInfo.PILATUS_TYPE_2M_SOCKET  : PilatusOverSocket,
		     };

	def create(self, name, pilatusType):
		p = PilatusFactory.classByType[pilatusType](name);
		PilatusFactory.products.append(p);
		return p;

	def listAll(self):
		for p in PilatusFactory.products:
			print p.getName(), ": ", p.getDetectorInfo();


#Usage:
#hostName = socket.gethostname();
#portNumber = 2729;

#pf = PilatusFactory();
#p1 = pf.create('ps100k', PilatusInfo.PILATUS_TYPE_100K_SOCKET);
#p1 = pf.create('ps100k', PilatusInfo.PILATUS_TYPE_100K_SOCKET);
#p1 = pf.create('ps100k', PilatusInfo.PILATUS_TYPE_2M_SOCKET);

#p1.setupServer(hostName, portNumber);
#p1.turnOn();

#p1.setFilePath('/home/xr56/Dev/users/data/');
#p1.setFilePrefix('demo_');
#p1.setCollectionTime(1);
#p1.start();
