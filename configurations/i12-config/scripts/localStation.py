#    file: localStation.py
#
#    For beamline specific initialisation code
import sys	
from gdascripts.messages import handle_messages
from gda.jython.commands import GeneralCommands

print "Performing I12 specific initialisation code"
print "=============================================="

from gda.jython.commands.GeneralCommands import alias

print "add EPICS scripts to system path"
print "------------------------------------------------"
### add epics plugin scripts library path
from gda.util import PropertyUtils
from java.lang import System
_epicsScriptLibraryDir = PropertyUtils.getExistingDirFromLocalProperties("gda.install.git.loc") + "/gda-epics.git/uk.ac.gda.epics/scripts" + System.getProperty("file.separator");
sys.path.append(_epicsScriptLibraryDir)

import i12utilities
from i12utilities import DocumentationScannable
import lookupTables


print "create commands for folder operations: wd, pwd, nwd, nfn, setSubdirectory('subdir-name')"
print "-------------------------------------------------"
# function to find the last file path
def wd(): 
    return i12utilities.wd()
alias("wd")

def pwd(): 
    return i12utilities.pwd()
alias("pwd")

def nwd():
    return i12utilities.nwd()
alias("nwd")

def nfn():
    return i12utilities.nfn()
alias("nfn")

def cfn(): 
    return i12utilities.cfn()
alias("cfn")

def setDataWriterToNexus():
    i12utilities.setDataWriterToNexus()
alias("setDataWriterToNexus")

def setDataWriterToSrs():
    i12utilities.setDataWriterToSrs()
alias("setDataWriterToSrs")

def getDataWriter():
    return i12utilities.getDataWriter()
alias("getDataWriter")

def ls_scannables():
    return i12utilities.ls_scannables()
alias("ls_scannables")

def helpi12(): 
    print "Help will be outputted"
alias("helpi12")

def reloadModuleLookup():
    lookupTables.reloadModuleLookup();
alias("reloadModuleLookup")
    
def reloadCameraMotionLookup():
    lookupTables.reloadCameraMotionLookup();
alias("reloadCameraMotionLookup")
    
def reloadTiltBallPositionLookup():
    lookupTables.reloadTiltBallPositionLookup();
alias("reloadTiltBallPositionLookup")
    
def reloadScanResolutionLookup():
    lookupTables.reloadScanResolutionLookup();
alias("reloadScanResolutionLookup")

def setSubdirectory(dirname):
    i12utilities.setSubdirectory(dirname)
    
msg = "i12 Help\n======="
msg += "\nPCO Help - type 'help i12pco'"
msg += "\nPixium Help - type 'help i12pixium'"
msg += "\nEDXD Help - type 'help i12edxd'"
msg += "\n====="
i12 = DocumentationScannable(msg, "http://confluence.diamond.ac.uk/display/I12Tech/I12+GDA+Help")
i12pco = DocumentationScannable("Documentation for i12pco", "http://confluence.diamond.ac.uk/display/I12Tech/PCO+detector")
i12pixium = DocumentationScannable("Documentation for i12pixium", "http://confluence.diamond.ac.uk/display/I12Tech/Pixium+in+GDA")
i12edxd = DocumentationScannable("Documentation for i12pixium", "http://confluence.diamond.ac.uk/display/I12Tech/EDXD%3A+Use+in+GDA")

# Do this last
#setSubdirectory("default")
print
print "-----------------------------------------------------------------------------------------------------------------"
print "Create an 'interruptable()' function which can be used to make for-loop interruptable in GDA."
print "    To use this, you must place 'interruptable()' call as the 1st or last line in your for-loop."
def interruptable():
    GeneralCommands.pause()
print
print "-----------------------------------------------------------------------------------------------------------------"
print "load EPICS Pseudo Device utilities for creating scannable object from a PV name."
from gdascripts.pd.epics_pds import * #@UnusedWildImport
print
print "-----------------------------------------------------------------------------------------------------------------"
print "load time utilities for creating timer objects."
from gdascripts.pd.time_pds import * #@UnusedWildImport
print
print "-----------------------------------------------------------------------------------------------------------------"
print "Load utilities: printJythonEnvironment(), caget(pv), caput(pv,value), attributes(object), "
print "    iterableprint(iterable), listprint(list), frange(start,end,step)"
from gdascripts.utils import * #@UnusedWildImport
print
print "-----------------------------------------------------------------------------------------------------------------"
print "load common physical constants"
from gdascripts.constants import * #@UnusedWildImport

from gda.configuration.properties import LocalProperties


# set up the reconmanager, however this should be moved into the Spring
#from uk.ac.gda.client.tomo import ReconManager
#rm = ReconManager()

# set up the extra scans
from init_scan_commands_and_processing import * #@UnusedWildImport
#scan_processor.rootNamespaceDict=globals()


from gda.scan.RepeatScan import create_repscan, repscan
vararg_alias("repscan")

from gdascripts.metadata.metadata_commands import setTitle
alias("setTitle")

if LocalProperties.check("gda.dummy.mode"):
    print "Running in dummy mode"

from gdascripts.pd.time_pds import waittimeClass2, showtimeClass, showincrementaltimeClass, actualTimeClass
waittime = waittimeClass2('waittime')
showtime = showtimeClass('showtime')
inctime = showincrementaltimeClass('inctime')
actualTime = actualTimeClass("actualTime")



try :
    print "setup edxd detector: edxd_counter, edxdout, edxd_binned"
    print "-------------------------------------------------"
    from edxd_count import edxd_count
    edxd_counter = edxd_count("edxd_counter", edxd) #@UndefinedVariable
    # set up the edxd to monitor to begin with
    edxd.monitorAllSpectra() #@UndefinedVariable
    print("After monitorAllSpectra")
    from EDXDDataExtractor import EDXDDataExtractor #@UnusedImport
    from EDXDDataExtractor import edxd2ascii
    from EDXDDataExtractor import postExtractor #@UnusedImport
    edxdout = edxd2ascii("edxdout")
    ## removing binned for the moment
    from edxd_binned_counter import EdxdBinned
    edxd_binned = EdxdBinned("edxd_binned", edxd) #@UndefinedVariable

    from edxd_q_calibration_reader import set_edxd_q_calibration
    print("After set_edxd_q_calibration")
    #epg 8 March 2011 Force changes to allow edxd to work on the trunk
    LocalProperties.set("gda.data.scan.datawriter.dataFormat", "NexusDataWriter")
    if LocalProperties.get("gda.data.scan.datawriter.dataFormat") != "NexusDataWriter":
        raise "Format not set to Nexus"
    edxd.setOutputFormat(["%5.5g", "%5.5g", "%5.5g", "%5.5g", "%5.5g"])
    
except :
	exceptionType, exception, traceback = sys.exc_info()
	handle_messages.log(None, "EDXD detector not available!", exceptionType, exception, traceback, False)

print "setup scan manager to control scan queue and their running"
print "-------------------------------------------------"
from manager_scan_functions import * #@UnusedWildImport

print "create 'topup' object"
print "-------------------------------------------------"
from topup_pause import TopupPause
topup = TopupPause("topup")

print "I12 specific commands: view <scannable>"
print "-------------------------------------------------"
def view(scannable): 
    for member in scannable.getGroupMembers() :
        print member.toFormattedString().replace('_', '.')

alias("view")

print "setup 'fastscan' object"
print "--------------------------------------------------"
from fast_scan import FastScan
fastscan = FastScan("fastscan");

print "setup 'sleeperWhileScan' object"
print "--------------------------------------------------"
from sleeperWhileScan import SleeperWhileScan
sleeper = SleeperWhileScan("sleeper");


print "Defines 'timer':"
print "--------------------------------------------------"
import timerelated 
timer = timerelated.TimeSinceScanStart("timer")

# tobias did this for the users at the end of run 3
from WaitLineDummy import WaitLineDummy
wld = WaitLineDummy("wld")

try :
    #create the PCO external object
    from pcoexternal import PCOext
    pcoext = PCOext(pco) #@UndefinedVariable
except :
    print "PCO external trigger not available"

from gdascripts.pd.time_pds import * #@UnusedWildImport
from gdascripts.pd.epics_pds import * #@UnusedWildImport
try:
    pixtimestamp = DisplayEpicsPVClass('pixtimestamp', 'BL12I-EA-DET-05:TIFF:TimeStamp_RBV', 's', '%.3f')
    pixtemperature = DisplayEpicsPVClass('pixtemperature', 'BL12I-EA-DET-05:TIFF:Temperature_RBV', 'degree', '%.3f') 
    pixtotalcount = DisplayEpicsPVClass('pixtotalcount', 'BL12I-EA-DET-05:STAT:Total_RBV', 'degree', '%d') 
    pixexposure = DisplayEpicsPVClass('pixexposure', 'BL12I-EA-DET-05:PIX:AcquireTime_RBV', 's', '%.3f') 
except:
    print "cannot create pixium timestamp and temperature scannables"
     
try:
    pcotimestamp = DisplayEpicsPVClass('pcotimestamp', 'TEST:TIFF0:TimeStamp_RBV', 's', '%.3f')    
except:
    print "cannot create PCO timestamp scannable"
try:
    loadcell = DisplayEpicsPVClass('loadcell', 'BL12I-EA-ADC-01:CH0', 's', '%.3f')
    HV_amp = EpicsReadWritePVClass('HV_amp', 'BL12I-EA-DAC-01:00', 's', '%.3f')
except:
    print "cannot create loadcell or HV_amp scannables"
    
print
print "create ETL detector objects"
try:
    eh1therm1 = DisplayEpicsPVClass('eh1therm1', 'BL12I-OP-THERM-01:TEMP:T1', 'degree', '%.3f')
    eh1therm2 = DisplayEpicsPVClass('eh1therm2', 'BL12I-OP-THERM-01:TEMP:T2', 'degree', '%.3f')
    eh1therm3 = DisplayEpicsPVClass('eh1therm3', 'BL12I-OP-THERM-01:TEMP:T3', 'degree', '%.3f')
    eh1therm4 = DisplayEpicsPVClass('eh1therm4', 'BL12I-OP-THERM-01:TEMP:T4', 'degree', '%.3f')
    eh1therm5 = DisplayEpicsPVClass('eh1therm5', 'BL12I-OP-THERM-01:TEMP:T5', 'degree', '%.3f')
    eh1therm6 = DisplayEpicsPVClass('eh1therm6', 'BL12I-OP-THERM-01:TEMP:T6', 'degree', '%.3f')
except:
    print "cannot create thermocouple scannables"
try:
    dac01_0 = EpicsReadWritePVClass('dac01_0', 'BL12I-EA-DAC-01:00', 'volt', '%.3f')
    dac01_1 = EpicsReadWritePVClass('dac01_1', 'BL12I-EA-DAC-01:01', 'volt', '%.3f')
    dac01_2 = EpicsReadWritePVClass('dac01_2', 'BL12I-EA-DAC-01:02', 'volt', '%.3f')
    dac01_3 = EpicsReadWritePVClass('dac01_3', 'BL12I-EA-DAC-01:03', 'volt', '%.3f')
    dac01_4 = EpicsReadWritePVClass('dac01_4', 'BL12I-EA-DAC-01:04', 'volt', '%.3f')
    dac01_5 = EpicsReadWritePVClass('dac01_5', 'BL12I-EA-DAC-01:05', 'volt', '%.3f')
    dac01_6 = EpicsReadWritePVClass('dac01_6', 'BL12I-EA-DAC-01:06', 'volt', '%.3f')
    dac01_7 = EpicsReadWritePVClass('dac01_7', 'BL12I-EA-DAC-01:07', 'volt', '%.3f')
except:
    print "cannot create DAC scannables"
print "--------------------------------------------------"
pdnames = []
from detector_control_pds import * #@UnusedWildImport

for pd in pds:
    pdnames.append(str(pd.getName()))
    
print "available Detector objects are:"
print pdnames
print [(str(pd.getName()), pd.getTargetPosition(), pd.getPosition()) for pd in pds]
print
print "create Long Count Time Scaler objects:"
print "---------------------------------------------------"
from long_count_time_scaler_pds import I0oh2l, I0eh1l, I0eh2l
print I0oh2l.getName(), I0eh1l.getName(), I0eh2l.getName()
print
print "create rocking motion objects:"
print "---------------------------------------------------"
from rockingMotion_class import RockingMotion #@UnresolvedImport
rocktheta = RockingMotion("rocktheta", ss1.theta, -1, 1) #@UndefinedVariable
print rocktheta.getName()

from positionCompareMotorClass import PositionCompareMotorClass
ss2x = PositionCompareMotorClass("ss2x", "BL12I-MO-TAB-06:X.VAL", "BL12I-MO-TAB-06:X.RBV", "BL12I-MO-TAB-06:X.STOP", 0.002, "mm", "%.3f")
ss2y = PositionCompareMotorClass("ss2y", "BL12I-MO-TAB-06:Y.VAL", "BL12I-MO-TAB-06:Y.RBV", "BL12I-MO-TAB-06:Y.STOP", 0.002, "mm", "%.3f")
ss2z = PositionCompareMotorClass("ss2z", "BL12I-MO-TAB-06:Z.VAL", "BL12I-MO-TAB-06:Z.RBV", "BL12I-MO-TAB-06:Z.STOP", 0.002, "mm", "%.3f")
ss2rx = PositionCompareMotorClass("ss2rx", "BL12I-MO-TAB-06:PITCH.VAL", "BL12I-MO-TAB-06:PITCH.RBV", "BL12I-MO-TAB-06:PITCH.STOP", 0.002, "deg", "%.3f")
ss2ry = PositionCompareMotorClass("ss2ry", "BL12I-MO-TAB-06:THETA.VAL", "BL12I-MO-TAB-06:THETA.RBV", "BL12I-MO-TAB-06:THETA.STOP", 0.002, "deg", "%.3f")

pco.setHdfFormat(False) #@UndefinedVariable

#EPG - 8 March 2011 - Hack to force Nexus for edxd
#pixium.setSRSFormat() #@UndefinedVariable
pco.setExternalTriggered(True) #@UndefinedVariable

print "create 'eurotherm1' and 'eurotherm2'" 
eurotherm1 = DisplayEpicsPVClass('eurotherm1', 'BL12I-EA-FURN-01:PV:RBV', 'c', '%.3f')
eurotherm2 = DisplayEpicsPVClass('eurotherm2', 'BL12I-EA-FURN-02:PV:RBV', 'c', '%.3f')

from tomographyScan import tomoScan, reportJythonNamespaceMapping #@UnusedImport
alias("reportJythonNamespaceMapping")
from tomo import tomoAlignment #@UnusedImport
#print
#print "setup tomographyScan:"
#from tomo import tomographyScan
#run("tomo/tomographyScan.py")

#from pv_scannable_utils import *
#print "added pv_scannable_utils" 

from PixiumAfterIOCStart_ModeChange import pixiumExp80ms, pixiumExp500ms, pixiumExp1000ms,pixiumExp2000ms, pixiumExp4000ms,pixiumAfterIOCStart
alias("pixiumExp80ms")
alias("pixiumExp500ms")
alias("pixiumExp1000ms")
alias("pixiumExp2000ms")
alias("pixiumExp4000ms")
alias("pixiumAfterIOCStart")

print 
print "==================================================="
print "local station initialisation completed."
