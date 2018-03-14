#@PydevCodeAnalysisIgnore
from utils.ScriptLogger import logging

from time import ctime
import os

#from gda.data.metadata import Metadata
from gda.data.metadata import GDAMetadataProvider

from gda.jython import InterfaceProvider
from gda.jython import JythonServerFacade;

from gda.configuration.properties import LocalProperties

import __main__ as gdamain;


class MetadataScannable(ScannabelMotionBase):
	'''creates a metadata object which hold a list of scannables 
	to be collected in the header of a scan SRS file as key=value pairs if its property recordAsHeader=True;
	or to be collected at every scan data point in a scan SRS file if its property recordAsHeader=False.
	Usage:
	create a metadata object:
	>>>mds = MetadataHeaderDevice("mds", [phi,chi,eta])
	To use in scan, either 
	>>>add_default([mds])
	for every scan thereafter, or 
	>>>scan x 1 10 1 mds
	To add to the list of metadata to capture use
	>>>mds.add([motor1, motor2])
	To remove from the list of metadata to capture use
	>>>mds.remove([motor1, motor2])
	To add metadata in file header use
	>>>mds.setRecordAsHeader(True)
	To collect metadata at every scan data point use
	>>>mds.setRecordAsHeader(False)
	'''
	logger=logging.getLogger("i09.scripts.metadata.MetadataHeader")
	def __init__(self, name, pdlist=None):
		self.pdlist=pdlist
		self.setName(name);
		self.setInputNames([])
		self.updateExtraNamesOutputFormat()
		self.setLevel(7)
		#allow any additional information
		self.extraHeaderItem=set();
		self.recordAsHeader=True
		#self.metadata = GDAMetadataProvider.getInstance(0);
	
	def setRecordAsHeader(self, v):
		self.recordAsHeader=v
	
	def getRecordAsHeader(self):
		return self.recordAsHeader

	def updateExtraNamesOutputFormat(self):
		names=[]; formats=[];
		for pd in self.pdlist:
			names+=pd.getInputNames()+pd.getExtraNames()
			formats+=pd.getOutputFormat()
		self.setExtraNames(names);
		self.setOutputFormat(formats)
		
	def getDeviceList(self):
		return self.pdlist;
		
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
			else:
				print "Can not find the device with name: " + str(nd);
				continue;
			if 'getPosition' not in dir(newd):
				print "Device " + str(newd) + " does not have getPosition() method."
				continue;
			if newd not in self.pdlist:
				self.pdlist.append(newd);
			self.updateExtraNamesOutputFormat()
			
	def remove(self, removeDeviceList):
		if type(removeDeviceList).__name__ != 'list':
			print "Please use a list of device as input";
			print "Usage: metadata.remove([motor1, motor2])";
			return;
		
		for nd in removeDeviceList:
			if ( nd in vars(gdamain).keys() ):
				newd = vars(gdamain)[nd];
			elif (nd in vars(gdamain).values()):
				newd = nd;
			else:
				print "Can not find the device with name: " + str(nd);
				continue;
			if newd in self.pdlist:
				self.pdlist.remove(nd);
			self.updateExtraNamesOutputFormat()
	
	def getLastCommand(self):
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
		'''add any extra header item'''
		self.extraHeaderItem.add(newHeaderItem);
		
	def removeExtraHeaderItem(self, headerItem):
		'''remove added extra header item'''
		self.extraHeaderItem.remove(headerItem);
		
	def clearExtraHeaderItems(self):
		'''clear all extra header item'''
		self.extraHeaderItem.clear();

	def createHeader(self):
		#To add the time
		metadataString = ("\ndate='" + ctime() +"'\n");
		
		#To add the scan command
		metadataString += "command="+self.getLastCommand()+"\n" 

		if self.recordAsHeader:
			#To add a list of scannable positions as key vaule pair in the header
			for i in range(len(self.pdlist)):
				p = self.pdlist[i].getPosition()
				#print "p: ", p, " ", type(p)
				if type(p).__name__ in ["float", "int", "str", "unicode"]:
					metadataString += self.pdlist[i].getName().split(".")[-1] + "=" + str(p) + "\n";
				else:
					namelist = self.pdlist[i].getInputNames()+ self.pdlist[i].getExtraNames()
					for nm in range(len(namelist)):
						metadataString += (namelist[nm] + "=" + str(p[nm]) + "\n")

		for s in self.extraHeaderItem:
			metadataString += "\n" + str(s)
			
		return metadataString;
	
	def atScanStart(self):
		# The gda does not create the data file until it records the first data point
		# At this time it looks for a variable named SRSWriteAtFileCreation in the
		# jython namespace, assumes its a string and writes into the header.
		
		if vars(gdamain).has_key("SRSWriteAtFileCreation"):
			self.keyFound=True
			logger.debug("Found it: SRSWriteAtFileCreation = " + vars(gdamain)["SRSWriteAtFileCreation"]);
			self.defaultSRSWriteAtFileCreation=vars(gdamain)["SRSWriteAtFileCreation"]
			vars(gdamain)["SRSWriteAtFileCreation"]+="\n"+self.createHeader();
		else:
			self.keyFound=False
			logger.debug("SRSWriteAtFileCreation does not exist. Create new one instead.");
			vars(gdamain)["SRSWriteAtFileCreation"]=self.createHeader();
		return;
	
	def atScanEnd(self):
		# reset the Header values
		if self.keyFound:
			vars(gdamain)["SRSWriteAtFileCreation"]=self.defaultSRSWriteAtFileCreation
		else:
			vars(gdamain)["SRSWriteAtFileCreation"]="";
	
	def isBusy(self):
		return False;

	def asynchronousMoveTo(self,new_position):
		pass

	def getPosition(self):
		if self.recordAsHeader:
			pass
		else:
			outlist=[]
	
			for pd in self.pdlist:
				# Get a position
				try:
					position = pd()
				except (Exception, java.lang.Exception), e:
					#print self.name + ": The position of " + pd.name + " is 'Unavailable' as it's getPosition is throwing:", e
					position = ['Unavailable'] * len(pd.outputFormat)
				
				# Create a list from the position
				try:
					position_list = list(position)
				except TypeError:
					position_list = [position]
				
				outlist += position_list
								
			return outlist

