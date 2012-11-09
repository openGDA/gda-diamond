print "===================================================================";
print "To change user data directory, call chgDir('proposal', visit)";
print "For example: chgDir('sp0', 0) will set the data directory for beamline commissioning" ;
print "             chgDir('sp32', 1) will set the data directory for Visit 1 of Proposal sp32 users" ;
print

#Setup the environment variables
import os

def chgDir(proposal, visit):
    if proposal == "sp0": # the default commissioning proposal
        userDir = proposal;
    else:
        userDir = proposal + "-" + str(visit);
    
    print "New user data directory is: /dls/i18/data/2009/" + userDir;

    #remove the old symbolic link
    os.system("rm -f /dls/i18/data/operation");
    
    #create the new symbolic link to point to the user data directory
    cmd = "ln -s /dls/i18/data/2009/" + userDir + " /dls/i18/data/operation"
    os.system(cmd);
