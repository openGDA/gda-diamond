#dataDir.py
#For beamline staff to set/get user data directory based on the proposal and visit number

# Note:
# Run this command from beamline control machine cat get the current visit number from iKitten
# system("/dls_sw/dasc/bin/currentvisit")


print "===================================================================";
print "To change user data directory, call setDir('proposal', visit)";
print "To get current user data directory info, call getDir('proposal', visit)";
print "For example: setDir('si0', 0) will set the data directory for beamline commissioning" ;
print "             setDir('si32', 1) will set the data directory for users of Proposal si32, Visit 1" ;
print

#Setup the environment variables
from os import system;
from time import localtime;

from java.io import File;

from gda.configuration.properties import LocalProperties;
from gda.data import NumTracker
from gda.jython import InterfaceProvider

#define the beamline commissioning proposal
bpDict={'i02':'mx0', 'i03':'mx0', 'i04':'mx0', 'i06':'cm1895', 'i06-1':'cm1907', 'i07':'cm1896', 'i11':'ee0', 'i15':'ee0', 'i16':'mt0', 'i18':'sp0', 'i22':'sm0'};

def chgDir(proposal=None, visit=1):
	setDir(proposal, visit);

def setDir(proposal=None, visit=1):
	#get beamline name from GDA propertie
	#beamlineName = LocalProperties.get("gda.instrument");
	beamlineName = LocalProperties.get("gda.beamline.name");
	
	commissioningProposal = bpDict.get(beamlineName, 'unknownPorposal');

	if proposal is None: # the default commissioning proposal
		proposal = commissioningProposal;

	userDir = proposal + "-" + str(visit);
	#get current Year
	currentTime = localtime();
	currentYear = currentTime[0];


	userDir="/dls/" + beamlineName + "/data/" + str(currentYear) + "/" + userDir;
	symbolicLink = "/dls/" + beamlineName + "/data/operation";

	print "New user data directory is: " + userDir;

	#remove the old symbolic link
	system("rm -f " + symbolicLink);
	
	#create the new symbolic link to point to the user data directory
	system("ln -s " + userDir + " " + symbolicLink);


def getDir(proposal=None, visit=1):
	
	if proposal is None: # the default commissioning proposal
		userDir=InterfaceProvider.getPathConstructor().createFromDefaultProperty() + File.separator;
		print "Current User Data Directory: " + userDir;
	else:
		#	get current Year
		currentTime = localtime();
		currentYear = currentTime[0];
		userDir =  + proposal + "-" + str(visit);
		userDir="/dls/" + beamlineName + "/data/" + str(currentYear) + "/" + proposal + "-" + str(visit);
		print userDir + " should the user data directory for this proposal and visit.";

def lastscan(extension="tmp"):
	nt=NumTracker(extension);
	lastSRSFileName= InterfaceProvider.getPathConstructor().createFromDefaultProperty() + File.separator + str(nt.getCurrentFileNumber()) + ".dat";
	del nt;
	return lastSRSFileName;

alias("lastscan");

#To get the current scan number
def getScanNumber():
	nt = NumTracker("tmp")
	scanNumber = nt.getCurrentFileNumber();
	del nt;
	return scanNumber

def	getSrsFileName(scanNumber = None):
	if scanNumber is None:
		sn = getScanNumber()
	else:
		sn = scanNumber;
	srsPath = InterfaceProvider.getPathConstructor().createFromProperty("gda.data.scan.datawriter.datadir");
	srsFileName = srsPath + File.separator + str(sn) + ".dat";
	
	print "srs file name is: " + srsFileName;
	return srsFileName;
	
	
	
from gda.util import ElogEntry
from gda.data.metadata import GDAMetadataProvider

def setTitle(title):
	GDAMetadataProvider.getInstance().setMetadataValue("title", title)

def getTitle():
	return GDAMetadataProvider.getInstance().getMetadataValue("title")

def setVisit(visit):
	user=GDAMetadataProvider.getInstance().getMetadataValue("federalid")
	if user != "i22user":
		oldvisit = GDAMetadataProvider.getInstance().getMetadataValue("visit")
		try:
			ElogEntry.post("visit manually changed from %s to %s by %s" % (oldvisit, visit, user), "", "gda", None, "BLI22", "BLI22-USR", None)
		except:
			pass
	GDAMetadataProvider.getInstance().setMetadataValue("visit", visit)

def getVisit():
	return GDAMetadataProvider.getInstance().getMetadataValue("visit")

