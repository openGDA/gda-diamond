
from time import sleep
#import xmlrpclib;
from xmlrpclib import ServerProxy;

from gda.device.scannable import PseudoDevice
from gda.device.detector import PseudoDetector
from gda.device.Detector import BUSY, IDLE

import __main__ as gdamain

class VersaStatClientClass(object):
	
	def __init__(self, name, serverURI):
		self.name = name;
		self.uri = serverURI;
		
		self.server = None;
	
		self.delay = 2;

		self.mode = None;
		self.modeString = ['Potentiostat', 'Galvanostat'];
		
		self.range = None;
		self.rangeString = ['2A', '200mA', '20mA', '2mA', '200uA', '20uA', '2uA', '200nA', '20nA', '4nA'];

	def __del__(self):
		self.close();

	def setDelay(self, newDelay):
		self.delay = newDelay;
		
	def getDelay(self):
		return self.delay;
	
		
	def close(self):
		self.server.Close();
		self.server = None;
		
	def setup(self):
		''' To setup the device to default settings '''	
		#Set to use the external cell
		self.server.SetCellExternal();
		
		#Turn the cell on
		self.server.SetCellOn();
		
		#Set to potentiostatic mode
		self.server.SetModePotentiostat();
		
		#Enable the auto range
		self.autoRangeOn();

	def connect(self):
		self.server=ServerProxy(self.uri);

		#To find the serial number of the first instrument 
		sn=self.server.FindNext(0);
		
		#To connect to the instrument
		bs=self.server.Connect(sn);
		if bs is True:
			print "Connected to VersaSTAT sucessfully."
		else:
			print "Connection failed."
		
	def info(self):
		if self.server is None:
			print "Not connected.";
			return;
		print "Model:      " + self.server.GetModel();
		print "Serial No.: " + self.server.GetSerialNumber();
		print "Options:    " + self.server.GetOptions();
		print
		
		self.server.UpdateStatus();
		overload=self.server.GetOverload();
		overloadStatus=["No Overload", "Current Overload", "E, Power Amp or Thermal Overload"]
		print "Overload Info: " + overloadStatus[overload];

		booster=self.server.GetBoosterEnabled();
		if booster is True:
			print "Booster Enabled.";
		else:
			print "Booster Disabled.";

		cell=self.server.GetCellEnabled();
		if cell is True:
			print "Cell Enabled.";
		else:
			print "Cell Disabled.";

		currentRange=self.server.GetIRange();
		print "Current Range: " + currentRange;
		
	def cellOn(self):
		#Turn the cell off
		self.server.SetCellOn();
		
	def cellOff(self):
		#Turn the cell on
		self.server.SetCellOff();

		#Enable the auto range
	def autoRangeOn(self):
		self.server.SetAutoIRangeOn();

		#Disable the auto range
	def autoRangeOff(self):
		self.server.SetAutoRangeOff();
			
	def setPotentialDC(self, voltage):
		self.server.SetDCPotential(-1.0 * voltage);
		sleep(self.delay);
		
	def getEI(self):
		self.server.UpdateStatus();
		e = 1.0 * self.server.GetE();
		i = -1.0 * self.server.GetI();
		return [e,i];
		

class VersaStatDeviceClass(PseudoDevice):
	def __init__(self, name, deviceName):
		self.setName(name);
		self.setInputNames(['E']);
		self.setExtraNames(['I']);
		self.setOutputFormat(["%12.8f", "%12.8f"]);
		self.setLevel(7);
		self.device = vars(gdamain)[deviceName];

	def info(self):
		self.device.info();
		
	def setup(self):
		self.device.connect();
		self.device.setup();
		
	def cellOn(self):
		self.device.cellOn();

	def cellOff(self):
		self.device.cellOff();
		
	def close(self):
		self.device.close();
		
	def setDelay(self, newDelay):
		self.device.setDelay(newDelay);
		
	def getDelay(self):
		return self.device.getDelay();
		
	#PseudoDevice Implementation
	def toString(self):
		ss=self.getName() + ": [E, I]: " + str(self.getPosition());
		return ss;

	def getPosition(self):
		return self.device.getEI();

	def asynchronousMoveTo(self,newPos):
		#do not multiply by -1 since setPotentialDC will correct the sign
		self.device.setPotentialDC(1.0 * newPos)
		return;

	def isBusy(self):
		return False;


class VersaStatMonitorClass(PseudoDetector):
	def __init__(self, name, deviceName):
		self.setName(name);
		self.setInputNames([]);
		self.setExtraNames(['Ee', 'Ii']);
		self.setOutputFormat(["%12.8f", "%12.8f"]);
		self.setLevel(7);
		self.device = vars(gdamain)[deviceName];

	#PseudoDetector Implementation
	def toString(self):
		ss=self.getName() + ": [Ee, Ii]: " + str(self.getPosition());
		return ss;

	def getPosition(self):
		return self.readout();

	def asynchronousMoveTo(self,newPos):
		pass;

	def readout(self):
		return self.device.getEI();

	def getCollectionTime(self):
		return 0;

	def setCollectionTime(self, newExpos):
		pass;

	def collectData(self):
		return;

	def getStatus(self):
		return IDLE;
	
	def createsOwnFiles(self):
		return False;


#########################################################

serverURI="http://172.23.107.5:5678/VersaStatServer.rem";

versaStatClient = VersaStatClientClass("versaStatClient", serverURI);
#versaStatClient.connect();
#versaStatClient.setup();

versa = VersaStatDeviceClass("versa", "versaStatClient");
versa.setup();
#versa.close();
#versa.info();
#versa.cellOn();
#versa.cellOff();

versa2 = VersaStatMonitorClass("versa2", "versaStatClient");

versa.setOutputFormat([u'%12.8f', u'%15.11f'])
versa2.setOutputFormat([u'%12.8f', u'%15.11f'])

#delete all:
#exec("[versaStatClient, versa, versa2] = [None, None, None]");
