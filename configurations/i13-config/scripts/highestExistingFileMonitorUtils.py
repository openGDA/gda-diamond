''' py file to setup highestExistingFileMonitor '''
from gda.factory import Finder
from gda.device.detectorfilemonitor import HighestExistingFileMonitorSettings

def configureHighestExistingFileMonitor( fileTemplatePrefix, fileTemplate, startNumber):
	"""
	Method to setup the monitoring of the latest detector file
	Parameters:
	fileTemplatePrefix - folder in which the file is to be stored
	fileTemplate - template to get filename
	startNumber - the initial number to look for
	
	e.g.
	configureHighestExistingFileMonitor( "/dls/i24/data/2011/mx6387-36/ev71a/", "012121_b3_x1_1_%04d.cbf", 1)
	"""
	settings = HighestExistingFileMonitorSettings( fileTemplatePrefix, fileTemplate, startNumber)
	highestExistingFileMonitor = Finder.find("highestExistingFileMonitor")
	highestExistingFileMonitor.setHighestExistingFileMonitorSettings(settings)
	highestExistingFileMonitor.setRunning(True)
