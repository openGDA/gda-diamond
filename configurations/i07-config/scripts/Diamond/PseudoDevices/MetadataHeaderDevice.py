#@PydevCodeAnalysisIgnore

from time import ctime
import sys, os

from gda.device.scannable import ScannableMotionBase
from gda.data.metadata import Metadata
from gda.data.metadata import GDAMetadataProvider

from gda.jython import InterfaceProvider
from gda.jython import JythonServerFacade;
from gda.scan import ScanDataPoint

from gda.configuration.properties import LocalProperties

import __main__ as gdamain;

from gdascripts.scannable.installStandardScannableMetadataCollection import meta

#Introduce the script logger
from Diamond.Utility.ScriptLogger import ScriptLoggerClass;
logger=ScriptLoggerClass();


class MetadataHeaderDeviceClass(ScannableMotionBase):
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
		self.metadata = GDAMetadataProvider.getInstance(0);
		self.scanLogger=None;
		self.startingTime=None;
		self.positionString = None;

	def setScanLogger(self, scanLogger=None):
		self.scanLogger=scanLogger;
	
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
		position_string = "";
		#To add a list of motor positions
		for meta_scannable in meta.getMeta():
			position = meta_scannable.getPosition()
			#print "p: ", p, " ", type(p)
			if type(position).__name__ in ["float", "int", "str", "unicode"]:
				position_string += meta_scannable.getName().split(".")[-1] + "=" + str(position) + "\n";
			else:
				namelist = meta_scannable.getInputNames() + meta_scannable.getExtraNames()
				for name_index in range(len(namelist)):
					position_string += (namelist[name_index] + "=" + str(position[name_index]) + "\n")

		self.positionString = position_string;
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

