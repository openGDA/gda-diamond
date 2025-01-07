#Define a list of useful functions for beamline control

import __main__ as gdamain
import sys;
from time import gmtime, strftime
import os;
import cPickle as pickle;

from gda.factory import Finder
from gda.configuration.properties import LocalProperties
from gda.util import ElogEntry
from gda.data.metadata import GDAMetadataProvider
from gda.jython.commands import GeneralCommands
from gda.jython import InterfaceProvider
from gda.jython import JythonServerFacade;
from gda.data import NumTracker

from Diamond.Utility.ScriptLogger import ScriptLoggerClass;

logger=ScriptLoggerClass();

class BeamlineFunctionClass(object):
	ELOG_IDs={#beamlineName: log book ID
			'i02': 'BLI02',
			'i03': 'BLI03',
			'i04': 'BLI04',
			'i06': 'BLI06',
			'i07': 'BLI07',
			'i11': 'BLI11',
			'i16': 'BLB16',
			'b23': 'BLB23'
			}

	def __init__(self, beamlineName=None):
		if beamlineName in BeamlineFunctionClass.ELOG_IDs.keys():
			self.beamlineName=beamlineName;
			self.elogID=BeamlineFunctionClass.ELOG_IDs[beamlineName];

		self.nsh=vars(gdamain);
		self.cs = self.nsh['command_server'];
		self.pickleFileName='/dls_sw/i06/var/defaultList.txt';

	def setBeamlineName(self, beamlineName):
		if beamlineName in BeamlineFunctionClass.ELOG_IDs.keys():
			self.beamlineName=beamlineName;
			self.elogID=BeamlineFunctionClass.ELOG_IDs[beamlineName];

	def swap(self, a, b):
		return b,a

	#To get the current scan number
	def getScanNumber(self):
		from gda.data import NumTracker
		nt = NumTracker("tmp")
		scanNumber = nt.getCurrentFileNumber();
		del nt;
		return scanNumber

	#To get the current scan number
	def incScanNumber(self):
		from gda.data import NumTracker
		nt = NumTracker("tmp")
		nt.incrementNumber();
		del nt;
		return;

	#To setup an 'interruptable()' function which can be used to make for-loop interruptable in GDA."
	#To use this, place 'interruptable()' call as the 1st or last line inside a for-loop."
	def interruptable(self):
		GeneralCommands.pause()

	#To remvoe all devices inside a list by name
	def removeDevices(self, nameList):
		for dn in nameList:
			try:
				globals().pop(dn);
			except:
				pass;
			try:
				locals().pop(dn);
			except:
				pass;
			try:
				self.nsh.pop(dn)
			except:
				pass;
			try:
				exec("del "+ dn);
			except:
				pass;	
		exec("try:\n	del "+ ', '.join(nameList) + "\nexcept:\n	pass;\n")

	def getDevice(self, deviceName):
		device=None;
		
		if type(deviceName).__name__ in ['str', 'unicode']:#A name is giving
			if deviceName in self.nsh.keys():
				device=self.nsh[str(deviceName)]
			else:
				print "device %s does not exist" %deviceName;
		else:#a real device is given
			if deviceName in self.nsh.values():
				device = deviceName;
			else:
				print "device %s does not exist" %deviceName;
		return device;

	def isDefaultDeive(self, deviceName):
		device=self.getDevice(deviceName);
		if device is None:
			print "device %s does not exist" %deviceName;
			return False;

		defaultList = self.cs.getDefaultScannables();
		result = device in defaultList;
		return result;

	def removeDefaults(self, nameList):
		
		for deviceName in nameList:
			self.cs.removeDefault(self.nsh[deviceName])
		return

	def pickleIt(self, pickleFileName, content):
		try:
			outStream = file(pickleFileName, 'wb');
			#Pickle the file number and dump to a file stream
			pickle.dump(content, outStream);
			outStream.close();
		except IOError:
			print "Can not preserve the content.";

	def restoreIt(self, pickleFileName):
		content = None;
		try:
			inStream = file(pickleFileName, 'rb');
			content = pickle.load(inStream);
			inStream.close();
		except IOError:
			print "Can not restore the pickled content.";
		return content;

	def backupDefaults(self):
		defaultList=[];
		defaultList.extend( self.cs.getDefaultScannableNames() );
		self.pickleIt(self.pickleFileName, defaultList);

	def restoreDefaults(self):
		'''Restore the pickled device list'''
		fileconetent = self.restoreIt(self.pickleFileName);

		if fileconetent is None:
			print "Nothing to restore";
			return;

		for deviceName in fileconetent:
			self.cs.addDefault(self.nsh[deviceName])
		return

	def getLastTerminalCommand(self):
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

		return strCmd

	def getLastScanPoint(self):
		jsf=JythonServerFacade.getInstance();
		lsdp=jsf.getLastScanDataPoint();
		return lsdp;

	def getLastScanCommand(self):
		lsdp=self.getLastScanPoint();
		strCmd=lsdp.getCommand();
		return strCmd;

	def getLastScanFile(self):
		lsdp=self.getLastScanPoint();
		lastScanFile=lsdp.getCurrentFilename();
		return lastScanFile;

	def getLastSrsScanFile(self, extension="tmp"):
		if self.getLastScanFile().endswith(".dat"):
			return self.getLastScanFile()
		# Otherwise have a Nexus file so extract the location and recreate filename with NumTracker
		nt = NumTracker(extension);
		return os.path.join(os.path.dirname(self.getLastScanFile()), str(nt.getCurrentFileNumber()) + ".dat")

	def setSubDir(self, newSubDirName):
		sd=Finder.find("subdirectory");
		sd.setValue( str(newSubDirName) );
		print "New data path: %s" %( self.getDataPath() );

	def setTerminalLogger(self, newLoggerName="gda_terminal.log"):
		tlPath=InterfaceProvider.getPathConstructor().createFromDefaultProperty();
		tlFile = os.path.join(tlPath, newLoggerName);
		tlpp=Finder.find("terminallog_path_provider")
		tlpp.setPath( str(tlFile) );

	def getDataPath(self):
		dataPath=InterfaceProvider.getPathConstructor().createFromDefaultProperty();
		return dataPath;

	def registerForPathUpdate(self, observerObject):
		observableSubdirectory=Finder.find("observableSubdirectory");
		observableSubdirectory.addIObserver(observerObject);

	def setTitle(self, title):
		GDAMetadataProvider.getInstance().setMetadataValue("title", title)

	def getTitle(self):
		return GDAMetadataProvider.getInstance().getMetadataValue("title")

	def setVisit(self, visit):
		oldvisit = GDAMetadataProvider.getInstance().getMetadataValue("visit")
		GDAMetadataProvider.getInstance().setMetadataValue("visit", visit)

		user=GDAMetadataProvider.getInstance().getMetadataValue("federalid")
		if "user" in user:#to get rid of the beamline user account  "ixxuser"
			logTitle="visit manually changed from %s to %s by %s" % (oldvisit, visit, user);
			logContent="";
			if self.eLogPost(logTitle, logContent):
				logger.simpleLog("Changes logged in eLog"); 
			else:
				logger.simpleLog("eLog failed"); 

	def getVisit(self):
		return GDAMetadataProvider.getInstance().getMetadataValue("visit")

	def eLogPost(self, logTitle, logContent):
		logUserID= "gda" #The user ID e.g. epics or gda or abc12345 
		visit=self.getVisit(); #The visit number;
		logID=self.elogID; #The logbook ID, such as BLI07
		logGroupID= logID + "-USER";
		# Since GroupIDs are limited to 10 characters, I06-1 had to be a special case:
		if logID == "BLI06-1":
			logGroupID= logID + "-UE";
		try:
			ElogEntry(logTitle, logUserID, visit, logID, logGroupID).addHtml(logContent).post()
		except:
			exceptionType, exception, traceback=sys.exc_info();
			print "eLog post failed."
			logger.dump("---> ", exceptionType, exception, traceback)
			return False;
		return True;

	def getCurrentTime(self):
		ct=strftime("%Y-%m-%d %H:%M:%S", gmtime());
		return ct

	def logScan(self, timeOfScan, formatedExtraInfo):
		scanNumber=self.getScanNumber();	
		logTitle="scan " + str( scanNumber );
#		logContent  = "Time: " + self.getCurrentTime() + "<br>";
#		logContent += "scan command: " + self.getLastScanCommand() + "<br>";
#		logContent += "scan file: " + self.getLastScanFile();
#		logContent  = '<table><tbody>'
#		logContent += '<tr><th><span style="color: rgb(0,51,102);">Command</span></th><th class="nohighlight">scan test motor1 0 10 1</th></tr>'
#		logContent += '<tr><td class="highlight">Data File</td><td>/dls/i06/data</td></tr>'
#		logContent += '<tr><td class="highlight"><p>Beamline</p><p>Parameters</p></td><td><p>beamenergy=-4.68582090948e-05</p><p>ringcurrent=0.0311676636338</p></td></tr>'
#		logContent += '</tbody></table>'

		logContent  = '<table style="border:1px solid black;border-collapse:collapse;"><tbody>'
#		logContent += '<tr><th colspan="2" style="color: rgb(0,51,102);text-align: center;"><span>Automatic scan logging</span></th></tr>'
		logContent += '<tr><th colspan="2" style="color: rgb(0,51,102);">Automatic scan logging</th></tr>'
		logContent += '<tr style="border:1px solid black;"><td style="border:1px solid black;">Time</td><td>%s</td></tr>' %( timeOfScan )
		logContent += '<tr style="border:1px solid black;"><td style="border:1px solid black;">Command</td><td>%s</td></tr>' %( self.getLastScanCommand() )
		logContent += '<tr style="border:1px solid black;"><td style="border:1px solid black;">Data File</td><td>%s</td></tr>' %( self.getLastScanFile() )
		logContent += '<tr style="border:1px solid black;"><td style="border:1px solid black;" width=60><p>Beamline Parameters</p></td><td>%s</td></tr>' %(formatedExtraInfo)
		logContent += '</tbody></table>'

		if self.eLogPost(logTitle, logContent):
			logger.simpleLog("Scan %d logged" %(scanNumber))

		return;

	def stopArchiving(self):
		ddwf=Finder.find("DefaultDataWriterFactory");
		fr=Finder.find("FileRegistrar");
		ddwf.removeDataWriterExtender(fr);

	def restoreArchiving(self):
		ddwf=Finder.find("DefaultDataWriterFactory");
		fr=Finder.find("FileRegistrar");
		ddwf.addDataWriterExtender(fr);

	def registerFileForArchiving(self, fileName):
		fr=Finder.find("FileRegistrar");
		if os.path.exists(fileName) and os.path.isfile(fileName):
			fr.registerFile(fileName);

