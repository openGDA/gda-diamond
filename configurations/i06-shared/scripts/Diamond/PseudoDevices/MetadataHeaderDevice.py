#@PydevCodeAnalysisIgnore

from time import ctime
import sys, os

from gda.device.scannable import PseudoDevice
from gda.data.metadata import Metadata
from gda.data.metadata import GDAMetadataProvider

from gda.jython import InterfaceProvider
from gda.jython import JythonServerFacade;
from gda.scan import ScanDataPoint

from gda.configuration.properties import LocalProperties

import __main__ as gdamain;

#Introduce the script logger
from Diamond.Utility.ScriptLogger import ScriptLoggerClass;
logger=ScriptLoggerClass();


class MetadataHeaderDeviceClass(PseudoDevice):
	'''Metadta writer.
	Usage:
	>>>run "MetaDataHeaderDeviceClass"
	>>>
	>>>mds = MetaDataHeaderDeviceClass("mds", [phi,chi,eta])  # make a small one
	>>>mdb = MetaDataHeaderDeviceClass("mdb", [enf,hkl,euler])  # make a big one
	>>>scan x 1 10 1 mds mdb
	'''
	def __init__(self, name):
		self.setName(name);
		self.setInputNames([])
		self.setExtraNames([])
		self.setOutputFormat([])

		self.extraHeaderItem=set();
		self.deviceList = [];
		self.metadata = GDAMetadataProvider.getInstance(0);
		self.scanLogger=None;
		self.startingTime=None;
		self.positionString = None;

	def setScanLogger(self, scanLogger=None):
		self.scanLogger=scanLogger;
		
	def getDeviceList(self):
		return self.deviceList;
		
	def add(self, newDeviceList):
		if type(newDeviceList).__name__ != 'list':
			print "Please use a list of device or device name as input";
			print "Usage: metadata.add([motor1, motor2])";
			return;
		
		for nd in newDeviceList:
			if ( nd in vars(gdamain).keys() ):
				newd = vars(gdamain)[nd];
			elif (nd in vars(gdamain).values()):
				newd = nd;
			elif (nd in locals()):
				continue
			else:
				print "Can not find the device with name: " + str(nd.name)+" in __main__ scope";
				continue;
			if 'getPosition' not in dir(newd):
				print "Device " + str(newd) + " does not have getPosition() method."
				continue;
			if newd not in self.deviceList:
				self.deviceList.append(newd);
			
	def remove(self, removeDeviceList):
		if type(removeDeviceList).__name__ != 'list':
			print "Please use a list of device as input";
			return;
		
		for nd in removeDeviceList:
			if ( nd in vars(gdamain).keys() ):
				newd = vars(gdamain)[nd];
			elif (nd in vars(gdamain).values()):
				newd = nd;
			elif (nd in locals()):
				continue
			else:
				print "Can not find the device with name: " + str(nd);
				continue;
			if newd in self.deviceList:
				self.deviceList.remove(nd);
	
	def getLastScanCommand(self):
        #jsf=InterfaceProvider.getJythonNamespace()
		jsf=JythonServerFacade.getInstance();
		sdp=jsf.getLastScanDataPoint();

		strCmd="GDA command";
		
		if isinstance(sdp, ScanDataPoint):
			strCmd=sdp.getCommand();
		return strCmd;

	def getLastCommandFromHistory(self):
		#jsf=InterfaceProvider.getJythonNamespace()
		jsf=JythonServerFacade.getInstance();
		
		historyFilePath = LocalProperties.get("gda.jythonTerminal.commandHistory.path", jsf.getDefaultScriptProjectFolder());
		historyFileName = os.path.join(historyFilePath, ".cmdHistory.txt")
		
		if not os.path.exists(historyFileName):
			print "No history found"
			strCmd=''
		else:
			historyFile=open(historyFileName, 'r');
			strCmd=( historyFile.readlines() )[-1];
			historyFile.close();
		
		#	with open(historyFileName as historyFile:
		#		strCmd=(historyFile)[-1]);
			
		return strCmd
	
	def addExtraHeaderItem(self, newHeaderItem):
		self.extraHeaderItem.add(newHeaderItem);
		
	def removeExtraHeaderItem(self, headerItem):
		self.extraHeaderItem.remove(headerItem);
		
	def clearExtraHeaderItems(self):
		self.extraHeaderItem.clear();

	def getPositionString(self):
		return self.positionString;

	def createHeader(self):
		#To add the time
		self.startingTime= ctime()
		metadataString = ("\ndate='" + self.startingTime +"'\n");
		
		#To add the scan command
#		metadataString += "command="+self.metadata.getMetadataValue(GDAMetadataProvider.SCAN_IDENTIFIER)+"\n" 
#		metadataString += "command="+self.getLastScanCommand()+"\n"

		#To add a list of motor positions
		self.createPositionString();
		metadataString += self.positionString;

		for s in self.extraHeaderItem:
			metadataString += "\n" + str(s)
			
		return metadataString;

	def createPositionString(self):
		#To add the time
		ps = "";
		#To add a list of motor positions
		for i in range(len(self.deviceList)):
			p = self.deviceList[i].getPosition()
			#print "p: ", p, " ", type(p)
			if type(p).__name__ in ["float", "int", "str", "unicode"]:
				ps += self.deviceList[i].getName().split(".")[-1] + "=" + str(p) + "\n";
			else:
				namelist = self.deviceList[i].getInputNames()+ self.deviceList[i].getExtraNames()
				for nm in range(len(namelist)):
					ps += (namelist[nm] + "=" + str(p[nm]) + "\n")

		self.positionString = ps;
		return self.positionString;

	def atScanStart(self):
		# The gda does not create the datafile until it recors the first datapoint
		# At this time it looks for a variable named SRSWriteAtFileCreation in the
		# jython namespace, assumes its a string and writes into the header.
		
		if vars(gdamain).has_key("SRSWriteAtFileCreation"):
			#logger.simpleLog("Found it: SRSWriteAtFileCreation = " + vars(gdamain)["SRSWriteAtFileCreation"]);
			vars(gdamain)["SRSWriteAtFileCreation"]=self.createHeader();
		else:
			#logger.simpleLog("SRSWriteAtFileCreation does not exist. Create new one instead.");
			vars(gdamain)["SRSWriteAtFileCreation"]=self.createHeader();
		return;
	
	def atScanEnd(self):
		try:
			if self.scanLogger is not None:
				formatedPositionString =  '<div>' + self.positionString.replace("\n" , "</div><div>") + '</div>'
	#			formatedPositionString  = '<div>beamenergy=-4.68582090948e-05</div>'
	#			formatedPositionString += '<div>ringcurrent=0.0311676636338</div>'
				self.scanLogger.logScan( self.startingTime, formatedPositionString );
		except:
			exceptionType, exception, traceback=sys.exc_info();
			print "Automatic scan logging failed."

		#do not clear as SrsDataFile does this
		#see gda-core.git commit d0fcf64c6ee

	def isBusy(self):
		return False;

	def asynchronousMoveTo(self,new_position):
		pass

	def getPosition(self):
		pass
	

#Usage:
#from Diamond.PseudoDevices.MetadataHeaderDevice import MetadataHeaderDeviceClass
#metadata = MetadataHeaderDeviceClass("metadata");
#metadata.add([testMotor1, testMotor2]);
#metadata.remove([testMotor2]);
#add_default(metadata);


class MetadataConsumerClass(object):
	def __init__(self, metadataDevice=None):
		self.metadataDevice = metadataDevice;
		self.metadataText=None;
		self.positionString=None;

	def setMetadataDevice(self, metadataDevice=None):
		self.metadataDevice = metadataDevice;

	def getMetadata(self):
		if self.metadataDevice is None:
			return;
		self.metadataText=self.metadataDevice.createHeader();
		return self.metadataText;
       
	def addExtraInfo(self, extraText):
		if self.metadataDevice is None:
			return;
		self.metadataDevice.addExtraHeaderItem(extraText);
    
	def removeExtraInfo(self, extraText):
		if self.metadataDevice is None:
			return;
		self.metadataDevice.removeExtraHeaderItem(extraText);
		
	def clearExtraInfo(self):
		if self.metadataDevice is None:
			return;
		self.metadataDevice.clearExtraHeaderItems();

	def createMetadataFiles(self, origionalFile):
		if self.metadataDevice is None:
			return;

		additionalFileName=os.path.splitext(origionalFile)[0] + ".txt";
		additionalFile=open(additionalFileName, 'w');
		additionalFile.write("Metadata for: " + origionalFile + self.metadataText);
		additionalFile.close();
#		print "Metadata file: " + additionalFileName;
		return;

