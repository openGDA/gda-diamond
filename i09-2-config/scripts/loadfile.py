#loadfile.py
#For users to load sample information excel file to ${gda.config}/var directory

# Note:
# Run this command from beamline control machine cat get the current visit number from iKitten
# os.system("/dls_sw/dasc/bin/currentvisit")


#Setup the environment variables
import os
import time

from gda.configuration.properties import LocalProperties

def loadsampleinformationfile(filename, LocalProperties=LocalProperties):
    """Load sample information from users provided Excel spreadsheet into GDA system.
    
    usage:
            loadsampleinformationfile('/absolute/File/Path/To/Excel/Spreadsheet')
    """

    vardir = LocalProperties.get("gda.config") + "/var";
    defaulfFilename = vardir + "/SampleInfo.xls";
    #copy user supplied file over to GDA system
    val=os.system("cp -f " + filename + " " + defaulfFilename);
    
    if val == 0:
        print "load completed."
    else:
        raise Exception("File load failed.")
    # health check on file read/write permissions
    si.setSampleInfoFile(defaulfFilename) #@UndefinedVariable
    
print "To load your spreadsheet use: >>>loadsampleinformationfile('/absolute/File/Path/To/Excel/Spreadsheet')."
