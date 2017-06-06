#dataDir.py
#For beamline staff to set/get user data directory based on the proposal and visit number
# Note:
# Run this command from beamline control machine cat get the current visit number from iKitten
# os.system("/dls_sw/dasc/bin/currentvisit")

#Setup the environment variables
import os
import time
from java.io import File
import sys

from gda.configuration.properties import LocalProperties
from gdascripts.messages import handle_messages
from gdascripts.messages.handle_messages import simpleLog
global configured, mar, pilatus, ruby, atlas, beamlineName, commissioningProposal
configured = False
def configure(jythonNameMap, beamlineParameters):
	global configured, mar, pilatus, ruby, atlas, beamlineName, commissioningProposal
	"""
	sets module variables from jython namespace, finder and beamline parameters
	"""
	mar = jythonNameMap.mar
	pilatus = jythonNameMap.pilatus
	ruby = jythonNameMap.ruby
	atlas = jythonNameMap.atlas
	beamlineName = jythonNameMap.beamlineName
	commissioningProposal = jythonNameMap.commissioningProposal
	configured = True

def checkConfigured():
	if not configured:
		raise "dataDir not configured"
	
def setDir(proposal=None, visit=None, subdirectory=""):
	"""
	To change user data directory, call setDir('proposal', visit)
	for example, you might use:		to set the data directory for:
		setDir('cm2062', 3)			beamline commissioning
		setDir('ee4321', 1)			proposal ee4321, Visit 1
	"""
	
	if proposal == None:
		print _.__doc__
		return
	
	if visit == None:
		print "No visit supplied, assuming visit 1."
		visit = 1
	
	checkConfigured()
	if (proposal == commissioningProposal):    # the default commissioning proposal
		userDir = proposal 
	else:
		userDir = proposal + "-" + str(visit)
		
	if subdirectory != "" :
		userDir = userDir + "/" + subdirectory;
	#get current Year
	currentTime = time.localtime();
	currentYear = currentTime[0];
	fullUserDir = "/dls/" + str(beamlineName) + "/data/" + str(currentYear) + "/" + str(userDir) + "/";
	setFullUserDir(fullUserDir)

def setFullUserDir(fullUserDir):
	"""
	Sets the current data folder e.g. setFullUserDir("/dls/i15/data/2008/ee0/mysubfolder"
	"""
	checkConfigured()
	targetDir = File(fullUserDir)
	try:
		if not targetDir.exists():
			targetDir.mkdirs()
		if not targetDir.exists():
			raise Exception ,"Unable to create data directory " + `targetDir` + " check permissions"
	except:
		typ, exception, _ = sys.exc_info()
		raise Exception, "Error while trying to create data directory:"  + `targetDir` + " " + `typ` + ":" + `exception`
	
	# Set up directories for mar and ruby as well
	if (os.path.exists(fullUserDir)):
		mar.setDirectory(fullUserDir)
		simpleLog( "Mar directory set to: " + str(fullUserDir))
		pilatus.setFilePath(fullUserDir)
		simpleLog( "Pilatus directory set to: " + str(fullUserDir))
		ruby.setDir(fullUserDir)
		atlas.setDir(fullUserDir)
		simpleLog( "Ruby/Atlas directory set to: " + str(fullUserDir))
	else:
		simpleLog( "Directory does not exist: " + str(fullUserDir))

