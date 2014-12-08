#dataDir.py
#For beamline staff to set/get user data directory based on the proposal and visit number

# Note:
# Run this command from beamline control machine cat get the current visit number from iKitten
# os.system("/dls_sw/dasc/bin/currentvisit")


print "===================================================================";
print "To change user data directory, call setDir('proposal', visit)";
print "To get current user data directory info, call getDir('proposal', visit)";
print "For example: setDir('si0', 0) will set the data directory for beamline commissioning" ;
print "             setDir('si32', 1) will set the data directory for users of Proposal si32, Visit 1" ;
print

#Setup the environment variables
import os
import time

from gda.configuration.properties import LocalProperties

#define the beamline commissioning proposal
bpDict={'i02':'mx0', 'i03':'mx0', 'i04':'mx0', 'i06':'si0', 'i11':'ee0', 'i15':'ee0', 'i16':'mt0', 'i18':'sp0', 'i22':'sm0'};

def setDir(proposal, visit, LocalProperties=LocalProperties):
    
    #get beamline name from GDA propertie
    #beamlineName = LocalProperties.get("gda.beamline.name");
    beamlineName = LocalProperties.get("gda.instrument.name");
    
    commissioningProposal = bpDict.get(beamlineName, 'unknownPorposal');
    
    if proposal == commissioningProposal: # the default commissioning proposal
        userDir = proposal;
    else:
        userDir = proposal + "-" + str(visit);
    #get current Year
    currentTime = time.localtime();
    currentYear = currentTime[0];


    userDir="/dls/" + beamlineName + "/data/" + str(currentYear) + "/" + userDir;
    symbolicLink = "/dls/" + beamlineName + "/data/operation";

    print "New user data directory is: " + userDir;

    #remove the old symbolic link
    os.system("rm -f " + symbolicLink);
    
    #create the new symbolic link to point to the user data directory
    os.system("ln -s " + userDir + " " + symbolicLink);


def getDir(proposal, visit, LocalProperties=LocalProperties):
    
    #get beamline name from GDA propertie
    #beamlineName = LocalProperties.get("gda.beamline.name");
    beamlineName = LocalProperties.get("gda.instrument.name");
    
    commissioningProposal = bpDict.get(beamlineName, 'unknownPorposal');
    
    if proposal == commissioningProposal: # the default commissioning proposal
        userDir = proposal;
    else:
        userDir = proposal + "-" + str(visit);

    #get current Year
    currentTime = time.localtime();
    currentYear = currentTime[0];

    userDir="/dls/" + beamlineName + "/data/" + str(currentYear) + "/" + userDir;
    symbolicLink = "/dls/" + beamlineName + "/data/operation";

    print userDir + " is the user data directory for this proposal and visit.";

