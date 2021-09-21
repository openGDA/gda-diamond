from time import sleep

from gda.data import NumTracker
from gda.device.scannable import ScannableMotionBase
from gda.device.detector import DetectorBase
from gda.device.Detector import BUSY, IDLE;

from Diamond.Comm.SocketDevice import SocketDeviceClass
from Diamond.Comm.SocketDevice import SocketError;

#The Class for creating a socket-based Device
class ClassixSystemClass(SocketDeviceClass):
	def __init__(self, name, hostName, hostPort):
		self.name = name;
		
		#New style Python class with super() to invoke base class constructor
#		super(CameraSockteDeviceClass, self).__init__(hostName, hostPort);
		#Old style Python class to invoke base class constructor
		SocketDeviceClass.__init__(self, hostName, hostPort);

	def sendAndReply(self, strSend):
		return self.resilientSendAndReply(strSend, 5);

	
	def getStatus(self):
		if self.checkStatus() =='READY':
			status = IDLE;
		else:
			status = BUSY;

		return status;

	def isBusy(self):
		if self.getStatus() == IDLE:
			return False;
		else:
			return True;

	def checkStatus(self):
		reply = self.sendAndReply('STAT');
#		print "Current status is: " + reply;
		rlist=reply.strip(' \n\r').split(' ',1);
		return rlist[0];

	def quit(self):
		while self.checkStatus() != 'READY':
			sleep(1);
		
		reply = self.sendAndReply('QUIT');
		rlist=reply.strip(' \n\r').split(' ',1);
		if rlist[0] != 'OK':
			print "Error with QUIT: " + reply;
#		print "QUIT command successfully sent out";
		return;

	def getImageIntegration(self):
		while self.isBusy():
			sleep(1);
		
		reply = self.sendAndReply('IMAG');
		rlist=reply.strip(' \n\r').split(' ',1);
		if rlist[0] != 'IMAGD':
			print "Error: " + reply;
		else:
			rf=float(rlist[1]);
			return rf;

	def startImageCollection(self, newExpos):
		while self.isBusy():
			sleep(1);
			
		reply = self.sendAndReply('IMAG ' + str(newExpos) );
		rlist=reply.strip(' \n\r').split(' ',1);
		if rlist[0] != 'OK':
			print "Server replied wrong message: " + reply;
		return;

	def getFilterPosition(self):
		reply = self.sendAndReply('FILT');
		rlist=reply.strip(' \n\r').split(' ',1);
		if rlist[0] != 'FILTD':
			print "Error: " + reply;
			rf = 999;
		else:
			rf=int(float(rlist[1]));
			return rf;
		
	def setFilterPosition(self,newPos):
		reply = self.sendAndReply('FILT ' + str(newPos) );
		rlist=reply.strip(' \n\r').split(' ',1);
		if rlist[0] != 'OK':
			print "Server replied wrong message: " + reply;
		return;
	

#The Class for creating Psuedo Device
class ClassixCameraPseudoDeviceClass(DetectorBase):
	def __init__(self, name, classix):
		self.setName(name);
		self.setInputNames([]);
		self.setExtraNames([name]);
#		self.Units=[strUnit];
		self.setLevel(7);
		
		self.camera = classix;
		self.exposureTime = 1;

	def save(self, startPos, stopPos, stepSize):
		while self.isBusy():
			sleep(1);
			
		scanNumber=self.getScanNumber();
		reply = self.camera.sendAndReply('SAVE E ' + str(scanNumber) + ' ' + str(startPos) + ' ' + str(stopPos) + ' ' + str(stepSize));
		rlist=reply.strip(' \n\r').split(' ',1);
		if rlist[0] == 'SAVED':
			print 'Classix saves images successfully.'
			return True;
		else:
			print 'Porblem when Classix saving images: ' + reply;
			return True;
	
	#DetectorBase Implementation
	def getPosition(self):
		return self.readout();
		
	def asynchronousMoveTo(self,newExpos):
		self.setCollectionTime(newExpos)
		self.collectData();

#	def moveTo(self, newPos):
#		self.asynchronousMoveTo(newPos);
#		while self.isBusy():
#			sleep(5);

#	def waitWhileBusy(self):
#		while self.isBusy():
#			sleep(5);
#		return;

	def getCollectionTime(self):
		return self.exposureTime;

	def setCollectionTime(self, newExpos):
		self.exposureTime = newExpos;

	def collectData(self):
		self.camera.startImageCollection(self.exposureTime);
		return;
	
	def readout(self):
		return self.camera.getImageIntegration();

	def getStatus(self):
		return self.camera.getStatus();

	#Only used for oly ScannableBase, not the new DetectorBase
#	def isBusy(self):
#		if  self.checkStatus() == 'READY':
#			return False;
#		else:
#			return Ture;

	def singleShot(self, newExpos):
		self.setCollectionTime(newExpos);
		self.collectData();
		self.readout();
		
	def getScanNumber(self):
		nt = NumTracker("tmp")
		#get current scan number
		return int(nt.getCurrentFileNumber());
		

class ClassixFilterPseudoDeviceClass(ScannableMotionBase):
	def __init__(self, name, classix):
		self.setName(name);
		self.setInputNames([]);
		self.setExtraNames([name]);
#		self.Units=[strUnit];
		self.setLevel(7);
		
		self.filter = classix;
		
	#ScannableMotionBase Implementation
	def atScanStart(self):
		return;

	def atScanEnd(self):
		return;
	
	def toString(self):
		ss=self.getName() + ": Current filter position is: " + str(self.getPosition());
		return ss;

	def getPosition(self):
		while self.isBusy():
			sleep(5);
		return self.filter.getFilterPosition();
	
	def asynchronousMoveTo(self,newPos):
		self.filter.setFilterPosition(newPos);

#	def moveTo(self, newPos):
#		self.asynchronousMoveTo(newPos);
#		while self.isBusy():
#			sleep(5);

#	def waitWhileBusy(self):
#		while self.isBusy():
#			sleep(5);
#		return;

	def isBusy(self):
		if self.filter.isBusy():
			print 'filter moving...';
			sleep(5);
			
		return self.filter.isBusy();

#print "Note: Use Object name 'classix' for direct communication to the Classix System";
#classix = ClassixSystemClass('classxi','172.23.106.152', 6342 );

#print "Note: Use Pseudo Device name 'camera' for Classix camera";
#camera = ClassixCameraPseudoDeviceClass('camera',classix);

#print "Note: Use Pseudo Device name 'filter' for Classix filter";
#filter = ClassixFilterPseudoDeviceClass('filter',classix);


