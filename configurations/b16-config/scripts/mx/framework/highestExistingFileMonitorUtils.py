''' py file to setup highestExistingFileMonitor '''
from gda.factory import Finder
from gda.device.detectorfilemonitor import HighestExistingFileMonitorSettings

from gdascripts.messages import handle_messages
import os.path
import re

class MxHighestExistingFileMonitor:
	
	def __init__(self, highestExistingFileMonitor=None):
		
		if highestExistingFileMonitor is None:
			highestExistingFileMonitor = Finder.find("highestExistingFileMonitor")
		
		self.highestExistingFileMonitor = highestExistingFileMonitor
	
	def configureHighestExistingFileMonitor(self, fileTemplatePrefix, fileTemplate, startNumber):
		"""
		Method to setup the monitoring of the latest detector file
		Parameters:
		fileTemplatePrefix - folder in which the file is to be stored
		fileTemplate - template to get filename
		startNumber - the initial number to look for
		
		e.g.
		configureHighestExistingFileMonitor( "/dls/i24/data/2011/mx6387-36/ev71a/", "012121_b3_x1_1_%04d.cbf", 1)
		"""
		print "Configuring file monitor for files:", fileTemplatePrefix, fileTemplate, startNumber
		settings = HighestExistingFileMonitorSettings( fileTemplatePrefix, fileTemplate, startNumber)
		self.highestExistingFileMonitor.setHighestExistingFileMonitorSettings(settings)
		self.highestExistingFileMonitor.setRunning(True)
		
		"""
		Method to load in a .cbf file directly from a given path
		Parameters:
		filePath - the path name to the file
		startNumber - the initial number to look for, 1 as default
		
		Even though a file with a number is explicitly passed in, the file range offset is determined by the value of
		the StartNumber - filePath = {path}/012121_b3_x1_1_0020.cbf, StartNumber = 4 -> range is 012121_b3_x1_1_0004.cbf
		to 012121_b3_x1_1_{nth file}.cbf
		
		An example: from a command console, load in a file
		highestExistingFileMonitorUtils.showFile("/dls/i24/data/2011/mx6387-36/ev71a/012121_b3_x1_1_0001.cbf",2)
		"""
	
	def showFile(self, filePath="",startNumber=1):
		
		try:
			#De-construct the file path to produce the required parameters to pass into
			#the configureHighestExistingFileMonitor method
			if os.path.exists(filePath):
				fileTemplatePrefix, filename = os.path.split(filePath)
				fileTemplatePrefix = "%s/"%fileTemplatePrefix
				extension = os.path.splitext(filename)[1]
				filename = re.search(r".*_",filename)
				fileTemplate = "%s%s%s"%(filename.group(),'%04d',extension)
				self.configureHighestExistingFileMonitor(fileTemplatePrefix,fileTemplate, startNumber)
		except Exception, e:
				handle_messages.log(None, IOError("Unable to load the file - " + e.message))
