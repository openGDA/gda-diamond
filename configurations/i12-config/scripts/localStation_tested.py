#    localStation.py
#
#    For beamline specific initialisation code
from gda.factory import Finder

print "Performing I12 specific initialisation code"
print "------------------------------------------------"

from gda.jython.commands.GeneralCommands import alias
from gda.jython import InterfaceProvider
from gda.data import NumTracker

from uk.ac.gda.client.tomo import ReconManager
import os
import sys

print "-----------------------------------"
print "add EPICS scripts to system path"
print "-----------------------------------"
### add epics plugin scripts library path
from gda.util import PropertyUtils
from java.lang import System
_epicsScriptLibraryDir = PropertyUtils.getExistingDirFromLocalProperties("gda.root") + "uk.ac.gda.epics/scripts" + System.getProperty("file.separator");
sys.path.append(_epicsScriptLibraryDir)

# set up a nice method for getting the latest file path
i12NumTracker = NumTracker("i12");

print "----------------------------------------------------------------------------------------"
print "create comands for folder operations: wd, pwd, nwd, nfn, setSubdirectory('subdir-name')"
print "----------------------------------------------------------------------------------------"
# function to find the last file path
def wd():
    dir = InterfaceProvider.getPathConstructor().createFromDefaultProperty()
    return dir
    
alias("wd")

# function to find the last file path
def pwd():
    dir = InterfaceProvider.getPathConstructor().createFromDefaultProperty()
    filenumber = i12NumTracker.getCurrentFileNumber();
    return os.path.join(dir,str(filenumber))
    
alias("pwd")

# function to find the next file path
def nwd():
    dir = InterfaceProvider.getPathConstructor().createFromDefaultProperty()
    filenumber = i12NumTracker.getCurrentFileNumber();
    return os.path.join(dir,str(filenumber+1))
    
alias("nwd")

# function to find the next scan number
def nfn():
    filenumber = i12NumTracker.getCurrentFileNumber();
    return filenumber+1
    
alias("nfn")
# the subdirectory parts
def setSubdirectory(dirname):
    Finder.find("GDAMetadata").setMetadataValue("subdirectory",dirname)
    try:
        os.mkdir(wd())
    except :
        pass
    
# Do this last
setSubdirectory("default")

# set up the reconmanager, however this should be moved into the Spring
#rm = ReconManager()

# set up the extra scans
#from init_scan_commands_and_processing import * #@UnusedWildImport
#scan_processor.rootNamespaceDict=globals()

#print "----------------------------------------------------------"
#print "setup edxd detector: edxd_count, edxdout, edxd_binned"
#print "----------------------------------------------------------"
# import the EDXD counter
#from edxd_count import edxd_count
#run("edxd_count")
#edxd_counter = edxd_count("edxd_counter", edxd) #@UndefinedVariable
# set up the edxd to monitor to begin with
#edxd.monitorAllSpectra() #@UndefinedVariable
#from EDXDDataExtractor import EDXDDataExtractor #@UnusedImport
#from EDXDDataExtractor import edxd2ascii
#from EDXDDataExtractor import postExtractor #@UnusedImport
#edxdout = edxd2ascii("edxdout")
## removing binned for the moment
#from edxd_binned_counter import EdxdBinned
#edxd_binned = EdxdBinned("edxd_binned",edxd) #@UndefinedVariable

print "----------------------------------------------------------"
print "setup scan manager to control scan queue and their running"
print "----------------------------------------------------------"
# import the Scan Manager
#from manager_scan import * #@UnusedWildImport
#sm = ScanManager()

#run("manager_scan_functions") #@UndefinedVariable

print "----------------------------------------------------------"
print "create 'topup' object"
print "----------------------------------------------------------"
# set up the topup and beam off pause
from topup_pause import * #@UnusedWildImport
topup = TopupPause("topup")

print "----------------------------------------------------------"
print "I12 specific commands: view <scannable>"
print "----------------------------------------------------------"
def view(scannable): 
    for member in scannable.getGroupMembers() :
        print member.toString().replace('_','.')

alias("view")

print "----------------------------------------------------------"
print "setup 'fastscan' object"
print "----------------------------------------------------------"
#from fast_scan import FastScan
#fastscan = FastScan("fastscan");

# import the required scans
#run("tomo_scan") #@UndefinedVariable

print "---------------------------------------------------------"
print "Defines 'timer':"
print "---------------------------------------------------------"

import timerelated 
timer = timerelated.TimeSinceScanStart("timer")


# tobias did this for the users at the end of run 3
run("WaitLineDummy.py") #@UndefinedVariable

#create the PCO external object
#from pcoext import PCOext
#pcoext = PCOext(pco) #@UndefinedVariable

from gdascripts.pd.time_pds import * #@UnusedWildImport
from gdascripts.pd.epics_pds import * #@UnusedWildImport
pixtimestamp=DisplayEpicsPVClass('pixtimestamp', 'BL12I-EA-DET-05:TIFF:TimeStamp_RBV', 's', '%.3f')    
pixtemperature=DisplayEpicsPVClass('pixtemperature', 'BL12I-EA-DET-05:TIFF:Temperature_RBV', 'degree', '%.3f') 
 
#pcotimestamp=DisplayEpicsPVClass('pcotimestamp', 'TEST:TIFF0:TimeStamp_RBV', 's', '%.3f')    

print "---------------------------------------------------------------------------------------------"
print "create ETL detector objects"
pdnames=[]
from detector_control_pds import * #@UnusedWildImport

for pd in pds:
    pdnames.append(pd.getName())
    
print "available Detector objects are:"
print pdnames
print [(pd.getName(), pd.getTargetPosition(), pd.getPosition()) for pd in pds]
print
print "---------------------------------------------------------------------------------------------"
print "create Long Count Time Scaler objects:"
from long_count_time_scaler_pds import I0oh2l, I0eh1l, I0eh2l
print I0oh2l.getName(), I0eh1l.getName(), I0eh2l.getName()


