#    file: localStation.py
#
#    For beamline specific initialisation code
import sys
import csv
from gdascripts.messages import handle_messages
from gda.jython import Jython
from gda.jython.commands import GeneralCommands
from gdascripts.utils import caput, caget, caput_wait
from gda.device.scannable import ScannableMotionBase
from gda.jython.commands import ScannableCommands


print "Performing I12 specific initialisation code"
print "=============================================="

from gda.jython.commands.GeneralCommands import alias, vararg_alias


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


from pv_scannable_utils import createPVScannable

print "-------------------------------------------------"
print "getting detectorModeSwitching"
try:
    import detectorModeSwitching
#from detectorModeSwitching import moveToImagingMode, moveToDiffractionMode, moveToEndOfHutchDiagnostic
except :
    exceptionType, exception, traceback = sys.exc_info()
    handle_messages.log(None, "Error on import detectorModeSwitching", exceptionType, exception, traceback, False)

print "-------------------------------------------------"
print "getting beamAttenuation"
import beamAttenuation
from beamAttenuation import moveToAttenuation


print "-------------------------------------------------"
print "getting pixium10_changeExposure"
from pixium10_utilities import pixium10_changeExposure, pixium10_changeExposureAndAcquirePeriod, pixium10_preview, earlyFramesIncluded, difract_redux, setup_pixium_postprocessing, pixium10_acquire_time_handler
earlyFramesOFF=earlyFramesIncluded
print "-------------------------------------------------"
print "create commands for folder operations: wd, pwd, nwd, nfn, cfn, setSubdirectory('subdir-name')"
print "-------------------------------------------------"
# function to find the last file path

from i12utilities import wd, pwd, nwd, nfn, cfn, setSubdirectory, getSubdirectory, setDataWriterToNexus, setDataWriterToSrs, getDataWriter, ls_scannables, isLive
alias("wd")
alias("pwd")
alias("nwd")
alias("nfn")
alias("cfn")
alias("setSubdirectory")
alias("getSubdirectory")
from i12utilities import getVisit, getVisitRootPath
alias("getVisit")
alias("getVisitRootPath")
from i12utilities import createScannableFromPV
from i12utilities import meta_add_EH2, meta_rm_EH2
alias("meta_add_EH2")
alias("meta_rm_EH2")

#print "create commands for Data Writer operations: setDataWriterToNexus, setDataWriterToSrs, getDataWriter"
#print "-------------------------------------------------"

#alias("setDataWriterToNexus")
#alias("setDataWriterToSrs")
#alias("getDataWriter")

print "Command to find list all the scannables: ls_scannables"
print "-------------------------------------------------"
alias("ls_scannables")

print "Commands to reload lookup tables: reloadModuleLookup, reloadCameraMotionLookup, reloadTiltBallPositionLookup, reloadScanResolutionLookup"
from lookupTables import reloadModuleLookup, reloadCameraMotionLookup, reloadTiltBallPositionLookup, reloadScanResolutionLookup
alias("reloadModuleLookup")
alias("reloadCameraMotionLookup")
alias("reloadTiltBallPositionLookup")
alias("reloadScanResolutionLookup")


msg = "i12 Help\n======="
msg += "\nPCO Help - type 'help i12pco'"
msg += "\nPixium Help - type 'help i12pixium'"
msg += "\nEDXD Help - type 'help i12edxd'"
msg += "\n====="
i12 = DocumentationScannable("i12Help", msg, "http://confluence.diamond.ac.uk/display/I12Tech/I12+GDA+Help")
i12pco = DocumentationScannable("i12HelpPco", "Documentation for i12pco", "http://confluence.diamond.ac.uk/display/I12Tech/PCO+detector")
i12pixium = DocumentationScannable("i12HelpPixium", "Documentation for i12pixium", "http://confluence.diamond.ac.uk/display/I12Tech/Pixium+in+GDA")
i12edxd = DocumentationScannable("i12HelpEdxd", "Documentation for i12edxd", "http://confluence.diamond.ac.uk/display/I12Tech/EDXD%3A+Use+in+GDA")

import i12info
import i13tomographyScan

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
print "Load utilities: caget(pv), caput(pv,value), attributes(object), "
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

from gdascripts.metadata.metadata_commands import setTitle, getTitle
alias("setTitle")
alias("getTitle")

print "setup meta-data provider"
from gdascripts.metadata.metadata_commands import meta_add, meta_ll, meta_ls, meta_rm
alias("meta_add")
alias("meta_ll")
alias("meta_ls")
alias("meta_rm")
from gda.data.scan.datawriter import NexusDataWriter
LocalProperties.set(NexusDataWriter.GDA_NEXUS_METADATAPROVIDER_NAME,"metashop")
from i12utilities import meta_add_EH2, meta_rm_EH2
alias("meta_add_EH2")
alias("meta_rm_EH2")

if LocalProperties.check("gda.dummy.mode"):
    print "Running in dummy mode"

from gdascripts.pd.time_pds import waittimeClass2, showtimeClass, showincrementaltimeClass, actualTimeClass
waittime = waittimeClass2('waittime')
showtime = showtimeClass('showtime')
inctime = showincrementaltimeClass('inctime')
actualTime = actualTimeClass("actualTime")

print "--------------------------------------------------"

try :
    print "setup edxd detector: edxd_counter, edxdout, edxd_binned"
    from edxd_count import edxd_count
    edxd_counter = edxd_count("edxd_counter", edxd) #@UndefinedVariable
#     # set up the edxd to monitor to begin with
#     edxd.monitorAllSpectra() #@UndefinedVariable
#     print("After monitorAllSpectra")
    from EDXDDataExtractor import EDXDDataExtractor #@UnusedImport
    from EDXDDataExtractor import edxd2ascii
    from EDXDDataExtractor import postExtractor #@UnusedImport
    edxdout = edxd2ascii("edxdout")
    ## removing binned for the moment
    from edxd_binned_counter import EdxdBinned
    edxd_binned = EdxdBinned("edxd_binned", edxd1) #@UndefinedVariable

    from edxd_q_calibration_reader import set_edxd_q_calibration
    print("After set_edxd_q_calibration")
    #epg 8 March 2011 Force changes to allow edxd to work on the trunk
    LocalProperties.set("gda.data.scan.datawriter.dataFormat", "NexusDataWriter")
    if LocalProperties.get("gda.data.scan.datawriter.dataFormat") != "NexusDataWriter":
        raise RuntimeError("Format not set to Nexus")
    edxd.setOutputFormat(["%5.5g", "%5.5g", "%5.5g", "%5.5g", "%5.5g"])
except :
    exceptionType, exception, traceback = sys.exc_info()
    handle_messages.log(None, "EDXD detector not available!", exceptionType, exception, traceback, False)

# manager_scan_functions commented out: probably not used and references client code
#print "--------------------------------------------------"

#print "setup scan manager to control scan queue and their running"
#from manager_scan_functions import * #@UnusedWildImport

print "--------------------------------------------------"
print "create 'topup' object"
from topup_pause import TopupPause
topup = TopupPause("topup")

print "--------------------------------------------------"

print "I12 specific commands: view <scannable>"
def view(scannable): 
    for member in scannable.getGroupMembers() :
        print member.toFormattedString().replace('_', '.')

alias("view")

# For the moment, stop dummy mode here
if isLive():
    print "--------------------------------------------------"
    print "setup 'fastscan' object"
    from fast_scan import FastScan
    fastscan = FastScan("fastscan");
    
    print "--------------------------------------------------"
    print "setup 'sleeperWhileScan' object"
    from sleeperWhileScan import SleeperWhileScan
    sleeper = SleeperWhileScan("sleeper");
    
    print "--------------------------------------------------"
    
    print "Defines 'timer':"
    import timerelated 
    timer = timerelated.TimeSinceScanStart("timer")
    
    # tobias did this for the users at the end of run 3
    from WaitLineDummy import WaitLineDummy
    wld = WaitLineDummy("wld")
    
    print "--------------------------------------------------"
    
    print "Creating PCO external object"
    
    try :
        #create the PCO external object
        from pcoexternal import PCOext
        pcoext = PCOext(pco) #@UndefinedVariable
    except :
        print "PCO external trigger not available"
    
    from gdascripts.pd.time_pds import * #@UnusedWildImport
    from gdascripts.pd.epics_pds import * #@UnusedWildImport
    
         
    try:
        pcotimestamp = DisplayEpicsPVClass('pcotimestamp', 'TEST:TIFF0:TimeStamp_RBV', 's', '%.3f')    
    except:
        print "cannot create PCO timestamp scannable"
    
    print "--------------------------------------------------"
    
    print "Creating DIO scannables"
    try:    
        dio01_out_02 = EpicsReadWritePVClass('dio01_out_02','BL12I-EA-DIO-01:OUT:02','bool','%i')
        dio01_out_04 = EpicsReadWritePVClass('dio01_out_04','BL12I-EA-DIO-01:OUT:04','bool','%i')
        dio01_out_05 = EpicsReadWritePVClass('dio01_out_05','BL12I-EA-DIO-01:OUT:05','bool','%i')
        dio01_out_06 = EpicsReadWritePVClass('dio01_out_06','BL12I-EA-DIO-01:OUT:06','bool','%i')
        dio01_out_07 = EpicsReadWritePVClass('dio01_out_07','BL12I-EA-DIO-01:OUT:07','bool','%i')
        dio01_out_08 = EpicsReadWritePVClass('dio01_out_08','BL12I-EA-DIO-01:OUT:08','bool','%i')
        
        
        dio02_in_05 = DisplayEpicsPVClass('dio02_in_05','BL12I-EA-DIO-01:IN:05','bool','%i')  
        dio02_in_06 = DisplayEpicsPVClass('dio02_in_06','BL12I-EA-DIO-01:IN:06','bool','%i')
        dio02_in_07 = DisplayEpicsPVClass('dio02_in_07','BL12I-EA-DIO-01:IN:07','bool','%i')
        dio02_in_08 = DisplayEpicsPVClass('dio02_in_08','BL12I-EA-DIO-01:IN:08','bool','%i')
       
        adc01_01 = DisplayEpicsPVClass('adc01_01', 'BL12I-EA-ADC-01:01', 'volt', '%.4g') #labelled according to RACK names, not EPICS
        adc01_02 = DisplayEpicsPVClass('adc01_02', 'BL12I-EA-ADC-01:02', 'volt', '%.4g')
        adc01_03 = DisplayEpicsPVClass('adc01_03', 'BL12I-EA-ADC-01:03', 'volt', '%.4g')
        adc01_04 = DisplayEpicsPVClass('adc01_04', 'BL12I-EA-ADC-01:04', 'volt', '%.4g')
        adc01_05 = DisplayEpicsPVClass('adc01_05', 'BL12I-EA-ADC-01:05', 'volt', '%.4g')
        adc01_06 = DisplayEpicsPVClass('adc01_06', 'BL12I-EA-ADC-01:06', 'volt', '%.4g')
        adc01_07 = DisplayEpicsPVClass('adc01_07', 'BL12I-EA-ADC-01:07', 'volt', '%.4g')
        adc01_08 = DisplayEpicsPVClass('adc01_08', 'BL12I-EA-ADC-01:08', 'volt', '%.4g')
        
        adc02_01 = DisplayEpicsPVClass('adc02_01', 'BL12I-EA-ADC-02:01', 'volt', '%.4f') #labelled according to RACK names, not EPICS
        adc02_02 = DisplayEpicsPVClass('adc02_02', 'BL12I-EA-ADC-02:02', 'volt', '%.4f')
        adc02_03 = DisplayEpicsPVClass('adc02_03', 'BL12I-EA-ADC-02:03', 'volt', '%.4f')
        adc02_04 = DisplayEpicsPVClass('adc02_04', 'BL12I-EA-ADC-02:04', 'volt', '%.4f')
        adc02_05 = DisplayEpicsPVClass('adc02_05', 'BL12I-EA-ADC-02:05', 'volt', '%.4f')
        adc02_06 = DisplayEpicsPVClass('adc02_06', 'BL12I-EA-ADC-02:06', 'volt', '%.4f')
        adc02_07 = DisplayEpicsPVClass('adc02_07', 'BL12I-EA-ADC-02:07', 'volt', '%.4f')
        adc02_08 = DisplayEpicsPVClass('adc02_08', 'BL12I-EA-ADC-02:08', 'volt', '%.4f')
       
        dac01_01 = EpicsReadWritePVClass('dac01_01', 'BL12I-EA-DAC-01:01', 'volt', '%.4g') #labelled according to RACK names, not EPICS
        dac01_02 = EpicsReadWritePVClass('dac01_02', 'BL12I-EA-DAC-01:02', 'volt', '%.4g')
        dac01_03 = EpicsReadWritePVClass('dac01_03', 'BL12I-EA-DAC-01:03', 'volt', '%.4g')
        dac01_04 = EpicsReadWritePVClass('dac01_04', 'BL12I-EA-DAC-01:04', 'volt', '%.4g')
        dac01_05 = EpicsReadWritePVClass('dac01_05', 'BL12I-EA-DAC-01:05', 'volt', '%.4g')
        dac01_06 = EpicsReadWritePVClass('dac01_06', 'BL12I-EA-DAC-01:06', 'volt', '%.4g')
        dac01_07 = EpicsReadWritePVClass('dac01_07', 'BL12I-EA-DAC-01:07', 'volt', '%.4g')
        dac01_08 = EpicsReadWritePVClass('dac01_08', 'BL12I-EA-DAC-01:08', 'volt', '%.4g')  
    
        radvolts = DisplayEpicsPVClass('radvolts', 'BL12I-EA-ADC-01:02', 'volt', '%.4g')
        radcounts = DisplayEpicsPVClass('radcounts', 'BL12I-DI-RDMON-01:T0', 'counts', '%.4g')
    
    except:
        print "cannot create EH1 ACD/DAC scannables."      
    
          
    try:
        dio04_out_01 = EpicsReadWritePVClass('dio04_out_01','BL12I-EA-DIO-04:OUT:01','bool','%i')
        dio04_out_02 = EpicsReadWritePVClass('dio04_out_02','BL12I-EA-DIO-04:OUT:02','bool','%i')
        dio04_out_03 = EpicsReadWritePVClass('dio04_out_03','BL12I-EA-DIO-04:OUT:03','bool','%i')
        dio04_out_04 = EpicsReadWritePVClass('dio04_out_04','BL12I-EA-DIO-04:OUT:04','bool','%i')
        dio04_out_05 = EpicsReadWritePVClass('dio04_out_05','BL12I-EA-DIO-04:OUT:05','bool','%i')
        dio04_out_06 = EpicsReadWritePVClass('dio04_out_06','BL12I-EA-DIO-04:OUT:06','bool','%i')
        dio04_out_07 = EpicsReadWritePVClass('dio04_out_07','BL12I-EA-DIO-04:OUT:07','bool','%i')
        dio04_out_08 = EpicsReadWritePVClass('dio04_out_08','BL12I-EA-DIO-04:OUT:08','bool','%i')
        
        dio03_in_01 = DisplayEpicsPVClass('dio03_in_01','BL12I-EA-DIO-03:IN:01','bool','%i')
        dio03_in_02 = DisplayEpicsPVClass('dio03_in_02','BL12I-EA-DIO-03:IN:02','bool','%i')  
        dio03_in_03 = DisplayEpicsPVClass('dio03_in_03','BL12I-EA-DIO-03:IN:03','bool','%i')  
        dio03_in_04 = DisplayEpicsPVClass('dio03_in_04','BL12I-EA-DIO-03:IN:04','bool','%i')
        dio03_in_05 = DisplayEpicsPVClass('dio03_in_05','BL12I-EA-DIO-03:IN:05','bool','%i')  
        dio03_in_06 = DisplayEpicsPVClass('dio03_in_06','BL12I-EA-DIO-03:IN:06','bool','%i')
        dio03_in_07 = DisplayEpicsPVClass('dio03_in_07','BL12I-EA-DIO-03:IN:07','bool','%i')
        dio03_in_08 = DisplayEpicsPVClass('dio03_in_08','BL12I-EA-DIO-03:IN:08','bool','%i')
        
        dac03_01 = EpicsReadWritePVClass('dac03_01', 'BL12I-EA-DAC-03:01', 'volt', '%.4f') #labelled according to RACK names, not EPICS
        dac03_02 = EpicsReadWritePVClass('dac03_02', 'BL12I-EA-DAC-03:02', 'volt', '%.4f')
        dac03_03 = EpicsReadWritePVClass('dac03_03', 'BL12I-EA-DAC-03:03', 'volt', '%.4f')
        dac03_04 = EpicsReadWritePVClass('dac03_04', 'BL12I-EA-DAC-03:04', 'volt', '%.4f')
        dac03_05 = EpicsReadWritePVClass('dac03_05', 'BL12I-EA-DAC-03:05', 'volt', '%.4f')
        dac03_06 = EpicsReadWritePVClass('dac03_06', 'BL12I-EA-DAC-03:06', 'volt', '%.4f')
        dac03_07 = EpicsReadWritePVClass('dac03_07', 'BL12I-EA-DAC-03:07', 'volt', '%.4f')
        dac03_08 = EpicsReadWritePVClass('dac03_08', 'BL12I-EA-DAC-03:08', 'volt', '%.4f')
     
        adc03_01 = DisplayEpicsPVClass('adc03_01', 'BL12I-EA-ADC-03:01', 'volt', '%.4g') #labelled according to RACK names, not EPICS
        adc03_02 = DisplayEpicsPVClass('adc03_02', 'BL12I-EA-ADC-03:02', 'volt', '%.4g')
        adc03_03 = DisplayEpicsPVClass('adc03_03', 'BL12I-EA-ADC-03:03', 'volt', '%.4g')
        adc03_04 = DisplayEpicsPVClass('adc03_04', 'BL12I-EA-ADC-03:04', 'volt', '%.4g')
        adc03_05 = DisplayEpicsPVClass('adc03_05', 'BL12I-EA-ADC-03:05', 'volt', '%.4g')
        adc03_06 = DisplayEpicsPVClass('adc03_06', 'BL12I-EA-ADC-03:06', 'volt', '%.4g')
        adc03_07 = DisplayEpicsPVClass('adc03_07', 'BL12I-EA-ADC-03:07', 'volt', '%.4g')
        adc03_08 = DisplayEpicsPVClass('adc03_08', 'BL12I-EA-ADC-03:08', 'volt', '%.4g')
      
    except:
        print "cannot create EH2 ADC/DAC scannables"
        
        
    print "--------------------------------------------------"
    print "Creating EH1/EH2 thermocouple scannables"   
    try:
        eh1therm1 = DisplayEpicsPVClass('eh1therm1', 'BL12I-OP-THERM-01:TEMP:T1', 'degree', '%.3f')
        eh1therm2 = DisplayEpicsPVClass('eh1therm2', 'BL12I-OP-THERM-01:TEMP:T2', 'degree', '%.3f')
        eh1therm3 = DisplayEpicsPVClass('eh1therm3', 'BL12I-OP-THERM-01:TEMP:T3', 'degree', '%.3f')
        eh1therm4 = DisplayEpicsPVClass('eh1therm4', 'BL12I-OP-THERM-01:TEMP:T4', 'degree', '%.3f')
        eh1therm5 = DisplayEpicsPVClass('eh1therm5', 'BL12I-OP-THERM-01:TEMP:T5', 'degree', '%.3f')
        eh1therm6 = DisplayEpicsPVClass('eh1therm6', 'BL12I-OP-THERM-01:TEMP:T6', 'degree', '%.3f')
    except:
        print "cannot create EH1 thermocouple scannables"
    try:
        eh2therm1 = DisplayEpicsPVClass('eh2therm1', 'BL12I-OP-THERM-02:TEMP:T1', 'degree', '%.3f')
        eh2therm2 = DisplayEpicsPVClass('eh2therm2', 'BL12I-OP-THERM-02:TEMP:T2', 'degree', '%.3f')
        eh2therm3 = DisplayEpicsPVClass('eh2therm3', 'BL12I-OP-THERM-02:TEMP:T3', 'degree', '%.3f')
        eh2therm4 = DisplayEpicsPVClass('eh2therm4', 'BL12I-OP-THERM-02:TEMP:T4', 'degree', '%.3f')
        eh2therm5 = DisplayEpicsPVClass('eh2therm5', 'BL12I-OP-THERM-02:TEMP:T5', 'degree', '%.3f')
        eh2therm6 = DisplayEpicsPVClass('eh2therm6', 'BL12I-OP-THERM-02:TEMP:T6', 'degree', '%.3f')
    except:
        print "cannot create EH2 thermocouple scannables"
    
    print "--------------------------------------------------"
    print "Creating Instron scannables"
    try:
        instron_position = DisplayEpicsPVClass('instron_position', 'BL12I-EA-HYD-01:CH-01:POS_RBV', 'mm', '%.3f')
        instron_load = DisplayEpicsPVClass('instron_load', 'BL12I-EA-HYD-01:CH-02:POS_RBV', 'kN', '%.3f')
        #Instron Live Displays. These can have arbitrary units depending how the user configures them on the Instron
        #Up to eight Live Displays are available. Four set up her for the time being.
        instron_live01 = DisplayEpicsPVClass('instron_live01', 'BL12I-EA-HYD-01:LD-01:POS_RBV', 'arb', '%.3f')
        instron_live02 = DisplayEpicsPVClass('instron_live02', 'BL12I-EA-HYD-01:LD-02:POS_RBV', 'arb', '%.3f')
        instron_live03 = DisplayEpicsPVClass('instron_live03', 'BL12I-EA-HYD-01:LD-03:POS_RBV', 'arb', '%.3f')
        instron_live04 = DisplayEpicsPVClass('instron_live04', 'BL12I-EA-HYD-01:LD-04:POS_RBV', 'arb', '%.3f')
    except:
        print "cannot create Instron rig scannables"
    
    print "--------------------------------------------------"
    
    print "Adding mono_bender_adjustment"
    import mono_bender_adjustment
    from mono_bender_adjustment import *
    
    print "-------------------------------------------------"
    print "Adding beamEnergy"
    import beamEnergy
    from beamEnergy import moveToBeamEnergy 
    from beamEnergy import calcBeamEnergyPositions
    print "--------------------------------------------------"
    
    print "disable 'waiting for file to be created'"
    pixium10_tif.pluginList[1].waitForFileArrival=False
    pco4000_dio_tif.setCheckFileExists(False)
    #pco4000_dio_hdf.setCheckFileExists(False)
    
    print "disable 'Path does not exist on IOC'"
    pixium10_tif.pluginList[1].pathErrorSuppressed=True
    pco4000_dio_tif.fileWriter.pathErrorSuppressed=True
    pco4000_dio_hdf.pluginList[1].pathErrorSuppressed=True
    flyScanDetector.getAdditionalPluginList()[0].pathErrorSuppressed=True
    flyScanFlatDarkDetector.getAdditionalPluginList()[0].pathErrorSuppressed=True
    
    
    print "--------------------------------------------------"
    
    pdnames = []
    from detector_control_pds import * #@UnusedWildImport
    
    for pd in pds:
        pdnames.append(str(pd.getName()))
        
    print "available Detector objects are:"
    print pdnames
    print [(str(pd.getName()), pd.getTargetPosition(), pd.getPosition()) for pd in pds]
    
    print "--------------------------------------------------"
    print "Creating Long Count Time Scaler objects:"
    
    from long_count_time_scaler_pds import I0oh2l, I0eh1l, I0eh2l
    print I0oh2l.getName(), I0eh1l.getName(), I0eh2l.getName()
    
    print "--------------------------------------------------"
    print "Creating rocking motion objects"
    from rockingMotion_class import RockingMotion #@UnresolvedImport
    rocktheta = RockingMotion("rocktheta", ss1.theta, -1, 1) #@UndefinedVariable
    rockss1y3 = RockingMotion("rockss1y3", ss1.y3, 0, 50) #@UndefinedVariable
    axis1=createScannableFromPV("axis1", "BL12I-MO-USER-01:AXIS1.VAL", addToNameSpace=True, getAsString=False, hasUnits=True)
    rockaxis1 = RockingMotion("rockaxis1", axis1, -1, 1) #@UndefinedVariable
    
    print rocktheta.getName()
    
    print "--------------------------------------------------"
    print "Creating additonal EH2 motors (for ss2)"
    from positionCompareMotorClass import PositionCompareMotorClass
    ss2x = PositionCompareMotorClass("ss2x", "BL12I-MO-TAB-06:X.VAL", "BL12I-MO-TAB-06:X.RBV", "BL12I-MO-TAB-06:X.STOP", 0.002, "mm", "%.3f")
    ss2y = PositionCompareMotorClass("ss2y", "BL12I-MO-TAB-06:Y.VAL", "BL12I-MO-TAB-06:Y.RBV", "BL12I-MO-TAB-06:Y.STOP", 0.002, "mm", "%.3f")
    ss2z = PositionCompareMotorClass("ss2z", "BL12I-MO-TAB-06:Z.VAL", "BL12I-MO-TAB-06:Z.RBV", "BL12I-MO-TAB-06:Z.STOP", 0.002, "mm", "%.3f")
    ss2rx = PositionCompareMotorClass("ss2rx", "BL12I-MO-TAB-06:PITCH.VAL", "BL12I-MO-TAB-06:PITCH.RBV", "BL12I-MO-TAB-06:PITCH.STOP", 0.002, "deg", "%.3f")
    ss2ry = PositionCompareMotorClass("ss2ry", "BL12I-MO-TAB-06:THETA.VAL", "BL12I-MO-TAB-06:THETA.RBV", "BL12I-MO-TAB-06:THETA.STOP", 0.002, "deg", "%.3f")
    
    print "--------------------------------------------------"
    print "Creating additional EH1 motors (patch)"
    t1rot = PositionCompareMotorClass("t1rot", "BL12I-MO-USER-01:AXIS1.VAL", "BL12I-MO-USER-01:AXIS1.RBV", "BL12I-MO-USER-01:AXIS1.STOP", 0.001, "deg", "%.3f")
    
    print "--------------------------------------------------"
    print "Setting PCO defaults"
    pco.setHdfFormat(False) #@UndefinedVariable
    
    #EPG - 8 March 2011 - Hack to force Nexus for edxd
    #pixium.setSRSFormat() #@UndefinedVariable
    pco.setExternalTriggered(True) #@UndefinedVariable
    
    print "--------------------------------------------------"
    print "Creating 'eurotherm1' and 'eurotherm2' scannables" 
    #eurotherm1temp = DisplayEpicsPVClass('eurotherm1temp', 'BL12I-EA-FURN-01:PV:RBV', 'c', '%.3f')
    #eurotherm2temp = DisplayEpicsPVClass('eurotherm2temp', 'BL12I-EA-FURN-02:PV:RBV', 'c', '%.3f')
    eurotherm1temp = DisplayEpicsPVClass('eurotherm1temp', 'BL12I-EA-FURN-01:EH1:PV:RBV', 'c', '%.3f')
    eurotherm2temp = DisplayEpicsPVClass('eurotherm2temp', 'BL12I-EA-FURN-01:EH2:PV:RBV', 'c', '%.3f')
    
    print "--------------------------------------------------"
    
    print "Creating Linkam scannables"
    try:
        linkamRampStatus = DisplayEpicsPVClass('linkamRampStatus','BL12I-CS-TEMPC-01:STATUS','bool','%i')
        linkamRampControl = EpicsReadWritePVClass('linkamRampControl', 'BL12I-CS-TEMPC-01:RAMP:CTRL:SET', '', '%.3g')
        linkamRampRate = EpicsReadWritePVClass('linkamRampRate', 'BL12I-CS-TEMPC-01:RAMP:RATE:SET', 'deg/min', '%.3g')
        linkamRampLimit = EpicsReadWritePVClass('linkamRampLimit', 'BL12I-CS-TEMPC-01:RAMP:LIMIT:SET', 'deg', '%.3g')
        linkamTemp = DisplayEpicsPVClass('linkamTemp','BL12I-CS-TEMPC-01:TEMP','degrees','%.3g')
        cryoTemp = DisplayEpicsPVClass('cryoTemp', "BL12I-EA-CSTRM-01:TEMP",'degrees','%.3f')
    except:
        print "cannot create linkam scannables"
    
    print "Creating HELIOS objects"
    try:
        heliosTemp = DisplayEpicsPVClass('heliosTemp','BL12I-EA-HELIO-01:LOOP1:PV:RBV','deg C','%.3f')
    except Exception, e:
        print "Error creating HELIOS objects: %s" %(str(e))
    
    print "--------------------------------------------------"
    
    print "Creating Hot-Air Blower object(s)"
    try:
        blowerTemp = DisplayEpicsPVClass('blowerTemp','BL12I-EA-BLOW-01:EH1:PV:RBV','deg C','%.3f')
    except Exception, e:
        print "Error creating Hot-Air Blower object(s): %s" %(str(e))

    print "--------------------------------------------------"
    
    print "Creating tomoScan"
    import tomographyScan
    from tomographyScan import tomoScan, reportJythonNamespaceMapping, reportTomo  #@UnusedImport
    alias("reportJythonNamespaceMapping")
    alias("reportTomo")
    
    
    tomography_additional_scannables=[]
    #try:
    #    tomography_additional_scannables.append(p2r_force)
    #    tomography_additional_scannables.append(p2r_y)
    #except:
    #    print "Unable to append p2r scannables to tomography_additional_scannables"
    
    print "--------------------------------------------------"
    print "Creating tomoAlignment"
    try:
        from tomo import tomoAlignment #@UnusedImport
    except:
        print "Unable to import 'tomoAlignment'"
    #print
    #print "setup tomographyScan:"
    #from tomo import tomographyScan
    #run("tomo/tomographyScan.py")
    
    #from pv_scannable_utils import *
    #print "added pv_scannable_utils" 
    
    print "--------------------------------------------------"
    print "Creating mass flow controller scannables"
    try:
        mfc_pressure = DisplayEpicsPVClass('mfc_pressure', 'ME08G-EA-GIR-01:MFC2:PBAR:RD', 'bar', '%5.3g')
        mfc_temperature = DisplayEpicsPVClass('mfc_temperature', 'ME08G-EA-GIR-01:MFC2:TEMP:RD', 'C', '%5.3g')
        mfc_volumetric_flow = DisplayEpicsPVClass('mfc_volumetric_flow', 'ME08G-EA-GIR-01:MFC2:VOL:FLOW:RD', 'CCM', '%5.3g')
    except:
        print "cannot create mass flow controller scannables"
        
    
    print "--------------------------------------------------"
    
    print "Creating pixium10 scannables"
    try:
        pixium10_TriggerMode=createScannableFromPV("pixium10_TriggerMode", "BL12I-EA-DET-10:CAM:TriggerMode", addToNameSpace=True, getAsString=True, hasUnits=False)
        pixium10_PUMode = DisplayEpicsPVClass('pixium10_PUMode', 'BL12I-EA-DET-10:CAM:PuMode_RBV', 'PU', '%i')
        pixium10_BaseExposure = DisplayEpicsPVClass('pixium10_BaseExposure', 'BL12I-EA-DET-10:CAM:AcquireTime_RBV', 's', '%.3f')
        pixium10_BaseAcquirePeriod = DisplayEpicsPVClass('pixium10_BaseAcquirePeriod', 'BL12I-EA-DET-10:CAM:AcquirePeriod_RBV', 's', '%.3f')
        pixium10_ExcludeEarlyFrames = createScannableFromPV("pixium10_ExcludeEarlyFrames", "BL12I-EA-DET-10:CAM:MotionBlur", addToNameSpace=True, getAsString=True, hasUnits=False)
        
        pixium10_TotalCount = DisplayEpicsPVClass('pixium10_TotalCount', 'BL12I-EA-DET-10:STAT:Total_RBV', 'count', '%.0f') 
        pixium10_TimeStamp = DisplayEpicsPVClass('pixium10_TimeStamp', 'BL12I-EA-DET-10:STAT:TimeStamp_RBV', 'time', '%.3f')
        
        pixium10_DataType=createScannableFromPV("pixium10_DataType", "BL12I-EA-DET-10:CAM:DataType", addToNameSpace=True, getAsString=True, hasUnits=False)
        pixium10_ID = DisplayEpicsPVClass('pixium10_ID', 'BL12I-EA-DET-10:STAT:UniqueId_RBV', 'no', '%.0f')
        pixium10_Counter = DisplayEpicsPVClass('pixium10_Counter', 'BL12I-EA-DET-10:CAM:ArrayCounter_RBV', 'no', '%.0f')
        pixium10_FanSpeed1 = DisplayEpicsPVClass('pixium10_FanSpeed1', 'BL12I-EA-DET-10:CAM:DetectorFan1Speed', 'rpm', '%.0f')
        pixium10_FanSpeed2 = DisplayEpicsPVClass('pixium10_FanSpeed2', 'BL12I-EA-DET-10:CAM:DetectorFan2Speed', 'rpm', '%.0f')
        pixium10_DetectorTemperature = DisplayEpicsPVClass('pixium10_DetectorTemperature', 'BL12I-EA-DET-10:CAM:DetectorTemperature', 'degree', '%.1f')
         
    except:
        print "cannot create pixium10 scannables"
    
    print "--------------------------------------------------"
    print "\n Finding requested default scannables in the Jython namespace..."
    # append items to the list below as required
    _default_scannables_names_i12 = []
    _default_scannables_names_i12.append("ring")
    _default_scannables_names_i12.append("actualTime")
    
    #_default_scannables_names_i12.append("I0eh1")
    #_default_scannables_names_i12.append("I0eh1l")
    #_default_scannables_names_i12.append("I0eh2")
    #_default_scannables_names_i12.append("I0eh2l")
    #_default_scannables_names_i12.append("I0oh2l")
    
    from types import *
    _default_scannables_i12 = []
    for sname in _default_scannables_names_i12:
        if type(Finder.find(sname)) is not NoneType:
            _default_scannables_i12.append(Finder.find(sname))
        else:
            try:
                #print sname
                eval(sname)
                _default_scannables_i12.append(eval(sname))
            except:
                msg = "\t Unable to find a default scannable named: " + sname
                print msg
    
    print "\n Adding default scannables to the list of defaults in the scan system..."
    try:
        default_scannables = []
        default_scannables.append(ring)
        default_scannables.append(actualTime)
        #default_scannables.append(I0eh1)
        #default_scannables.append(I0eh1l)
        #default_scannables.append(I0eh2)
        #default_scannables.append(I0eh2l)
        #default_scannables.append(I0oh2l)
        
        #for s in default_scannables:
        for s in _default_scannables_i12:
            add_default(s)
    except:
        exceptionType, exception, traceback = sys.exc_info()
        msg = "Unable to complete adding default scannables: "
        handle_messages.log(None, msg, exceptionType, exception, traceback, False)
    
    print "\n Completed adding default scannables."
    srv = Finder.findSingleton(Jython)
    infoAllDefaultScannables_i12 = srv.getDefaultScannables().toArray()
    print "\n ***List of all default scannables in the scan system:"
    for s in infoAllDefaultScannables_i12:
        print s.getName()
    
    print "--------------------------------------------------"
    try:
        print "\n Adding requested meta (before-scan) scannables to the list of metas in the scan system..."
        meta_scannables = []
        meta_scannables.append(cam1)
    #    meta_scannables.append(cam3)
        
        meta_scannables.append(f1)
        meta_scannables.append(f2)
        
        meta_scannables.append(mc1_bragg)
        meta_scannables.append(mc2_bragg)
        meta_scannables.append(dcm1_cap_1)
        meta_scannables.append(dcm1_cap_2)
        meta_scannables.append(mc2)
        meta_scannables.append(ss1)
        meta_scannables.append(ss2)
        meta_scannables.append(s1)
        meta_scannables.append(s2)
        meta_scannables.append(s3)
        #meta_scannables.append(s4)
        
        meta_scannables.append(t3)
        meta_scannables.append(t7)
    #    meta_scannables.append(eh1therm1)
        
        for s in meta_scannables:
            meta_add(s)
        
        print "\n Completed adding meta (before-scan) scannables."
        print "\n ***List of all meta (before-scan) scannables in the scan system:"
        infoAllMetaScannables_i12 = meta_ls()
        print infoAllMetaScannables_i12
    except:
        exceptionType, exception, traceback = sys.exc_info()
        msg = "Unable to complete adding meta (before-scan) scannables: "
        handle_messages.log(None, msg, exceptionType, exception, traceback, False)
    

def _clear_defaults():
    """To clear all current default scannables."""
    srv = Finder.findSingleton(Jython)
    all_vec = srv.getDefaultScannables()
    all_arr = all_vec.toArray()
    for s in all_arr:
        #srv.removeDefault(s)
        remove_default(s)
    return all_arr
alias("_clear_defaults")

# This should be added, but importing does not resolve ss1_x..
#print "Set up scripts for tomograhy Rotation Axis Alignment"
#import gda_sphere_alignment
#from gda_sphere_alignment import sphere_alignment
#alias("sphere_alignment")


#from i12utilities import setUpCopyPluginForPCO, setUpCopyPluginForPIXIUM
#alias("setUpCopyPluginForPCO")
#alias("setUpCopyPluginForPIXIUM")
#setUpCopyPluginForPCO()

#print "setup pco cpy plugin"
#from epics_scripts.pv_scannable_utils import caputStringAsWaveform
#caput( "BL12I-EA-DET-02:COPY:Run", 0)
#caputStringAsWaveform( "BL12I-EA-DET-02:COPY:SourceFilePath", "d:\\i12\\data\\2014")
#caputStringAsWaveform( "BL12I-EA-DET-02:COPY:DestFilePath", "t:\\i12\\data\\2014")
#caput ("BL12I-EA-DET-02:COPY:Run", 1)

#from detectorModeSwitching import moveToImagingMode, moveToDiffractionMode, moveToEndOfHutchDiagnostic

#import p2r_utilities
#from p2r_utilities import flyp2r, stepp2r

print "--------------------------------------------------"

from i12utilities import clear_defaults, i12tomoFlyScan
alias("clear_defaults")

def _i12tomoFlyScan(description="Hello World", inBeamPosition=0.,outOfBeamPosition=1., exposureTime=.05, start=0., stop=180., step=.1, imagesPerDark=20, imagesPerFlat=20, extraFlatsAtEnd=False, closeShutterAfterScan=False):
    """
    Function to perform a tomography continuous-rotation scan on i12
     Arguments:
    description - description of the scan (or the sample that is being scanned. This is generally user-specific information that may be used to map to this scan later and is available in the NeXus file)
    inBeamPosition - position of X drive to move sample into the beam to take a projection
    outOfBeamPosition - position of X drive to move sample out of the beam to take a flat field image
    exposureTime - exposure time in seconds ( default = 1)
    start - first rotation angle (default=0.)
    stop  - last rotation angle (default=180.)
    step - rotation step size (default = 0.1)
    imagesPerDark - number of images to be taken for each dark (default=20)
    imagesPerFlat - number of images to be taken for each flat (default=20)
    extraFlatsAtEnd - if true, flats are taken after the flyscan as well as before
    closeShutterAfterScan - if true, shutter is closed after the flyscan
    """
    print "Running i12tomoFlyScan"
    import i13tomographyScan
#    from gda.factory import Finder
#    zebra1=Finder.find("zebra")
    #remove_default(ring)
    #remove_default(actualTime)
    defaults_save = clear_defaults()
    try:
        i13tomographyScan.tomoFlyScan(description=description, inBeamPosition=inBeamPosition, outOfBeamPosition=outOfBeamPosition, exposureTime=exposureTime, start=start, stop=stop, step=step, imagesPerDark=imagesPerDark, imagesPerFlat=imagesPerFlat, extraFlatsAtEnd=extraFlatsAtEnd, closeShutterAfterScan=closeShutterAfterScan, beamline="I12")
    except:
        exceptionType, exception, traceback = sys.exc_info()
        handle_messages.log(None, "Exception in i12tomoFlyScan", exceptionType, exception, traceback, False)
    finally:
        #zebra1.pcDisarm()
        # set to step-scan
        #import zebra_utilities
        #zebra_utilities.setZebra2Mode(1)
        for s in defaults_save:
            add_default(s)

import os
def stress12(exposureTime=1.0,startAng=0.0, stopAng=180.0, stepAng=0.05, subDir=None, loopNum=1):
    """
    Description:
    Function to run a step scan in the TIFF format for stress test on i12 
    (all scan files are saved in the tmp sub-directory of the current visit directory) 
    
    Arguments:
    exposureTime - exposure time in seconds (default = 1.0)
    startAng - start rotation angle (default = 0.0)
    stopAng  - last rotation angle (default = 180.0)
    stepAng - rotation step size (default = 0.05)
    subDir - name of the sub-directory of the visit/tmp directory to be used for saving out images 
            (default = None, in which case data go to /dls/i12/data/yyyy/visitID/tmp/)
    loopNum - total number of scans to be run (default = 1)
    """
    print "Entering stress12"
    sub = "tmp"
    if subDir is not None:
        sub += os.sep + subDir
    setSubdirectory(sub)
    msg = pwd()
    print "Saving data in: " + msg
    try:
        for i in range(0, loopNum):
            interruptable()
            print "scan index: %i (of %i)" %(i+1,loopNum)
            tomoScan("stress12", ss1_x_dummy(), ss1_x_dummy(), exposureTime, startAng, stopAng, stepAng, darkFieldInterval=0, flatFieldInterval=0, imagesPerDark=0, imagesPerFlat=0, optimizeBeamInterval=0, pattern='default', tomoRotationAxis=0, addNXEntry=True, autoAnalyse=False, additionalScannables=[])
            interruptable()
    except:
        exceptionType, exception, traceback = sys.exc_info()
        handle_messages.log(None, "Exception in stress12", exceptionType, exception, traceback, False)
    finally:
        setSubdirectory("")
    print "Finished stress12 consisting of %i scan(s)" %(loopNum)
    
    
def stressTestNetApp(nScans=100, exposureTime=.05, startAng=0.0, stopAng=180.0, stepAng=0.1, subDir=None):
    """
    Description:
    Function to run a step scan in the TIFF format for stress test on i12 
    (all scan files are saved in the tmp sub-directory of the current visit directory) 
    
    Arguments:
    exposureTime - exposure time in seconds (default = 1.0)
    startAng - start rotation angle (default = 0.0)
    stopAng  - last rotation angle (default = 180.0)
    stepAng - rotation step size (default = 0.05)
    subDir - name of the sub-directory of the visit/tmp directory to be used for saving out images 
            (default = None, in which case data go to /dls/i12/data/yyyy/visitID/tmp/)
    nScans - total number of scans to be run (default = 1)
    """
    print "Executing stressTestNetApp..."
    sub = "tmp"
    if subDir is not None:
        sub += os.sep + subDir
    setSubdirectory(sub)
    msg = pwd()
    print "Saving data in: " + msg
    try:
        for i in range(0, nScans):
            interruptable()
            print "Running scan: %i (of %i)..." %(i+1,nScans)
            #tomoScan("stress12", ss1_x_dummy(), ss1_x_dummy(), exposureTime, startAng, stopAng, stepAng, darkFieldInterval=0, flatFieldInterval=0, imagesPerDark=0, imagesPerFlat=0, optimizeBeamInterval=0, pattern='default', tomoRotationAxis=0, addNXEntry=True, autoAnalyse=False, additionalScannables=[])
            #i12tomoFlyScan(description="Hello World", inBeamPosition=0.,outOfBeamPosition=1., exposureTime=.05, start=0., stop=180., step=.1, imagesPerDark=20, imagesPerFlat=20, extraFlatsAtEnd=False, closeShutterAfterScan=False, vetoFlatsDarksAtStart=False, helical_axis_stage=None)
            i12tomoFlyScan(description="stressTestNetApp", inBeamPosition=0.,outOfBeamPosition=1., exposureTime=.05, start=startAng, stop=stopAng, step=stepAng, imagesPerDark=0, imagesPerFlat=0)
            print "Finished running scan: %i (of %i)" %(i+1,nScans)
            interruptable()
    except:
        exceptionType, exception, traceback = sys.exc_info()
        handle_messages.log(None, "Exception in stress12", exceptionType, exception, traceback, False)
    finally:
        setSubdirectory("")
    print "Finished executing stressTestNetApp - bye!"
    
    
def stressfly12(nscans, exposureTime, start, stop, step, pathToVisitDir="/dls/i12/data/2016/cm14465-4", filesys="na", delay_sec=0):
    """
    Fn to collect a series of fly scans for testing purposes with the following:
        dummy translation stage is expected to be used!
        no flats and darks
        all scan files going to the tmp sub-directory of the input pathToVisitDir
 
    nscans = tot number of scans to be run
    exposureTime = exposure time in seconds
    start = first rotation angle
    stop = last rotation angle
    step = rotation step size
    pathToVisitDir = path to a directory which GDA can use for writing log files, ie /dls/i12/data/2016/cm14465-4
    filesys = 'na' for NetApp and 'gpfs' for GPFS03
    delay_sec = delay time in seconds between any two consecutive scans
    """
    _fn = stressfly12.__name__
    setSubdirectory("tmp")
    windowsSubString_dct = {"na": "d:\\i12\\data\\", "gpfs": "g:\\i12\\data\\"}     # was t: for GPFS01
    #flyScanDetector = Finder.find("flyScanDetector")        # probably not needed here on i12? Prob not coz got this: Exception: Trying to overwrite a Scannable: flyScanDetector
    #windowsSubString_saved = flyScanDetectorNoChunking.pluginList[1].ndFileHDF5.file.filePathConverter.getWindowsSubString()
    #print "windowsSubString_saved = %s" %(windowsSubString_saved)
    print "Setting windowsSubString to %s..." %(windowsSubString_dct[filesys])
    flyScanDetector.pluginList[1].ndFileHDF5.file.filePathConverter.setWindowsSubString(windowsSubString_dct[filesys])
    print "Current windowsSubString = %s" %(flyScanDetector.pluginList[1].ndFileHDF5.file.filePathConverter.getWindowsSubString())
    
    pv_after_scan = {"HDF5:IOSpeed": "BL12I-EA-DET-02:HDF:IOSpeed", "HDF5:DroppedArrays": "BL12I-EA-DET-02:HDF:DroppedArrays_RBV", "HDF5:RunTime": "BL12I-EA-DET-02:HDF:RunTime"}
    log_subdir_path = "rawdata/testout"
    log_dir_path = os.path.join(pathToVisitDir, log_subdir_path)  # it appears GDA can't save files in tmp or processing
    print "log_dir_path = %s" %(log_dir_path)
    if (not os.path.exists(log_dir_path)):
        try:
            os.makedirs(log_dir_path)
        except Exception, e:
            msg="Failed to create sub-directory %s: " %(log_dir_path)
            raise Exception(msg + str(e))
    log_file_name = _fn
    timestr_template = "%Y-%m-%dT%H-%M-%S"
    timestr = time.strftime(timestr_template)
    log_file_name += ("_%s_" %(filesys))
    log_file_name += timestr
    #log_file_name += ".log"
    log_file_name += ".csv"
    log_file_path = os.path.join(log_dir_path,log_file_name)
    fh = open(log_file_path, 'wt')
    print "Saving log file in: %s\n" %(log_file_path)
    
    title_saved = getTitle()
    title = _fn +"_" + filesys
    msg = wd()
    print "Saving data in: " + msg
    try:
        i =-1
        timestr_template_HMS = "%H:%M:%S"
        csv_writer = csv.writer(fh)
        #msg = "scan iter \t scan number \t start time \t end time \t elapsed (min) \t HDF5:IOSpeed \t HDF5:RunTime \t HDF5:Dropped"
        #fh.write(msg+"\n")
        csv_writer.writerow(('scan iter', 'scan number', 'start time', 'end time', 'elapsed (min)', 'HDF5:IOSpeed', 'HDF5:RunTime', 'HDF5:Dropped'))
        fh.flush()
        for i in range(nscans):
            interruptable()             # for breaking this loop when GDA Abort button is pressed
            title_tmp = title
            title_tmp += "_%d/%d" %((i+1), nscans)
            setTitle(title_tmp)
            timestr_start = time.strftime(timestr_template_HMS)
            print "Starting scan iter %d (of %d), start time: %s." %(i+1, nscans, timestr_start)
            #msg = "scan iter: %d/%d, scan number: %d, start time: %s" %((i+1), nscans, nfn(), timestr_start)
            #fh.write(msg+"\n")
            start_time = time.time()
            caput("BL12I-EA-DET-02:CAM:ArrayCounter", 0)
            i12tomoFlyScan(description=title_tmp, inBeamPosition=0., outOfBeamPosition=1., exposureTime=exposureTime, \
                                       start=start, stop=stop, step=step, \
                                       imagesPerDark=0, imagesPerFlat=0)
            end_time = time.time()
            elapsed_min = (end_time - start_time)/60.0
            timestr_end = time.strftime(timestr_template_HMS)
            #msg = "scan iter: %d/%d, scan number: %d, start time: %s, end time: %s, elapsed (min): %f, HDF5:IOSpeed: %s, HDF5:Dropped: %s" %((i+1), nscans, cfn(), timestr_start, timestr_end, elapsed_min, str(caget(pv_after_scan["HDF5:IOSpeed"])), str(caget(pv_after_scan["HDF5:DroppedArrays"])))
            #msg = "%d/%d \t %d \t %s \t %s \t %f \t %s \t %s \t %s" %((i+1), nscans, cfn(), timestr_start, timestr_end, elapsed_min, str(caget(pv_after_scan["HDF5:IOSpeed"])), str(caget(pv_after_scan["HDF5:RunTime"])), str(caget(pv_after_scan["HDF5:DroppedArrays"])))
            #fh.write(msg+"\n")
            csv_writer.writerow(("%d/%d" %((i+1), nscans), cfn(), timestr_start, timestr_end, elapsed_min, str(caget(pv_after_scan["HDF5:IOSpeed"])), str(caget(pv_after_scan["HDF5:RunTime"])), str(caget(pv_after_scan["HDF5:DroppedArrays"]))))
            fh.flush()
            print "Finished scan iter %d (of %d), end time: %s." %(i+1, nscans, timestr_end)
            if (delay_sec > 0) and (i < nscans-1):
                print "Sleeping for %.3f sec between scans..." %(delay_sec)
                time.sleep(delay_sec)
                print "Finished sleeping for %.3f sec" %(delay_sec)
            interruptable()             # for breaking this loop when GDA Abort button is pressed
    except Exception, e:
        msg = "Scan %d (of %d) has failed: " %(i+1, nscans)
        print msg + str(e)
    finally:
        fh.close()
        setTitle(title_saved)
        setSubdirectory("rawdata")
    print "\n Finished executing %s - bye!" %(_fn)


if isLive():
    geo2mot1 = EpicsReadWritePVClass('geo2mot1','BL12I-ME-BRICK-02:AXIS1.VAL','um','%.4f')
    geo2mot2 = EpicsReadWritePVClass('geo2mot2','BL12I-ME-BRICK-02:AXIS2.VAL','um','%.4f')
    geo2mot3 = EpicsReadWritePVClass('geo2mot3','BL12I-ME-BRICK-02:AXIS3.VAL','um','%.4f')
    geo2mot4 = EpicsReadWritePVClass('geo2mot4','BL12I-ME-BRICK-02:AXIS4.VAL','um','%.4f')
    geo2mot5 = EpicsReadWritePVClass('geo2mot5','BL12I-ME-BRICK-02:AXIS5.VAL','um','%.4f')
    geo2mot6 = EpicsReadWritePVClass('geo2mot6','BL12I-ME-BRICK-02:AXIS6.VAL','um','%.4f')
    geo2mot7 = EpicsReadWritePVClass('geo2mot7','BL12I-ME-BRICK-02:AXIS7.VAL','um','%.4f')
    geo2mot8 = EpicsReadWritePVClass('geo2mot8','BL12I-ME-BRICK-02:AXIS8.VAL','um','%.4f')
    
    try:
        # Lazy open for Pixium
        caput("BL12I-EA-DET-10:TIFF:LazyOpen", 1)
        caput("BL12I-EA-DET-10:HDF5:LazyOpen", 1)
    except:
        print "unable to set LazyOpen for Pixium - is Pixium IOC running?"
    
    try:
        # Lazy open for PCO
        caput("BL12I-EA-DET-02:TIF:LazyOpen", 1)
        caput("BL12I-EA-DET-02:HDF:LazyOpen", 1)
        
        caput("BL12I-EA-DET-02:HDF:CreateDirectory", 1)
    except:
        print "unable to set LazyOpen for PCO - is PCO IOC running?"

import time
from epics_scripts.pv_scannable_utils import caputStringAsWaveform


def runscan(title, nImages, expTime, visit="ee11884-1", waitsec=1):
    """
    Command to record images using Pixium with earlyFramesOFF

    title: scan description to be recorded in the scan Nexus file
    nImages: total number of images to be acquired (the total number of images actually recorded will be one more than nImages, ie nImages+1)
    expTime: exposure interval in seconds
    visit: the ID of visit, eg "ee11161-1"; default="ee11161-1"
    waitsec: interval of time in seconds to wait after required EPICS PVs are set (which may take a moment); default=1 (advanced users)  
    """
    print "running runscan with input args:..."
    print "nImages = %i" %(nImages)
    print "expTime = %3.1f" %(expTime)
    print "visit = %s" %(visit)
    print "adding default scannables..."
    add_default(eurotherm1temp)
    add_default(eh1therm1)
    add_default(eh1therm2)
    add_default(eh1therm3)
    add_default(eh1therm4)
    add_default(eh1therm5)
    add_default(eh1therm6)
    print "...finished adding default scannables"
    pvFilePath = "BL12I-EA-DET-10:TIFF:FilePath"
    #filePath = "d:\\\\i12\\data\\2015\\ee11286-1\\rawdata\\"
    filePath = "d:\\\\i12\\data\\2015\\"+visit+"\\rawdata\\"
    fileNum = nfn()
    filePath += `fileNum`
    print "filePath = %s" %(filePath)
    #caput(pvFilePath, filePath)
    caputStringAsWaveform(pvFilePath, filePath)
    time.sleep(waitsec)
    pvNextFileNum = "BL12I-EA-DET-10:TIFF:FileNumber"
    imageNum = 1
    caput(pvNextFileNum, imageNum)
    old_title = getTitle()
    setTitle(title)
    try:
        #scan ix 0 nImages 1 pixium10_tif expTime earlyFramesOFF
        pass
    except:
        print "Error in runscan function"
    finally:
        setTitle(old_title)
    print "...finished running runscan!"

if isLive():
    try:
        caput("BL12I-EA-DET-02:CAM:PIX_RATE", "286000000 Hz")
    except:
        print "unable to set pixel rate on PCO - is PCO IOC running?"
        
    flyScanDetector.readOutTime=0.011
    hdfplugin=flyScanDetector.getPluginList()[1]
    hdfplugin.rowChunks=0
    hdfplugin.framesChunks=0
    hdfplugin.colChunks=0
    
    hdfplugin_step = pco4000_dio_hdf.getAdditionalPluginList()[0]
    hdfplugin_step.rowChunks=2160
    hdfplugin_step.framesChunks=1
    hdfplugin_step.colChunks=2560
    
    ss1_theta_vel = EpicsReadWritePVClass('ss1_theta_vel','BL12I-MO-TAB-02:ST1:THETA.VELO','deg/s','%.4f')
    
    #caput("BL12I-EA-DET-02:TIF:NDArrayPort", "pco1.cam")
    try:
        print "Setting up piezo objects..."
        piezo4
        piezo4x = piezo4.piezo4X
        #piezo4x.setName("piezo4x")
        piezo4y = piezo4.piezo4Y
        #piezo4y.setName("piezo4y")
        print "Finished setting up piezo objects."
    except Exception, e:
        print "Problems setting up piezo objects: " + str(e)
        
    from p2r_utilities import p2r_telnet
    from i12utilities import i12tomoTRFlyScan, use_storage, report_storage
    alias("report_storage")
    print "--------------------------------------------------"
    use_storage(storage_name="gpfs")
    print "--------------------------------------------------"
    
    try:
        # Set ports of file-writing plugins 
        caput("BL12I-EA-DET-02:TIF:NDArrayPort", caget("BL12I-EA-DET-02:CAM:PortName_RBV"))
        caput("BL12I-EA-DET-02:HDF:NDArrayPort", caget("BL12I-EA-DET-02:CAM:PortName_RBV"))
    except:
        print "unable to set ports on file-writing plug-ins for PCO - is PCO IOC running?"
    
    try:
        setup_pixium_postprocessing() 
        i12utilities._make_subdir(dirname="rawdata")
    except Exception, e:
        msg = "Error setting up pixium post-processing: %s" %(str(e))
        print msg + str(e)
    
    #make ScanPointProvider
    import position_provider
    npositions = position_provider.ScanPositionProviderFromFile(n=5)
    
    print("Adding ring-current (beam) monitor")
    from beam_monitor import WaitWhileScannableBelowThresholdMonitorOnly
    bm = WaitWhileScannableBelowThresholdMonitorOnly("bm", ring_current, minimumThreshold=200.0, secondsBetweenChecks=1, secondsToWaitAfterBeamBackUp=10.0, shtr_obj=eh1shtr)
    
    print "--------------------------------------------------"
    print "Adding pco_preview"
    def pco_preview():
        caput("BL12I-EA-DET-02:CAM:Acquire", 0)    # 1 for START, 0 for STOP
        caput("BL12I-EA-DET-02:CAM:ImageMode", 2)   # 0 for SINGLE, 2 for CONTINUOUS
        caput("BL12I-EA-DET-02:PRO1:EnableCallbacks", 1)
        caput("BL12I-EA-DET-02:CAM:Acquire", 1)
    alias("pco_preview")
    
    print "Adding pixium_preview"
    def pixium_preview():
        caput("BL12I-EA-DET-10:CAM:Acquire", 0)    # 1 for START, 0 for STOP
        caput("BL12I-EA-DET-10:CAM:ImageMode", 2)   # 0 for SINGLE, 2 for CONTINUOUS
        caput("BL12I-EA-DET-10:PRO1:EnableCallbacks", 1)
        caput("BL12I-EA-DET-10:CAM:Acquire", 1)
    alias("pixium_preview")
    
#    from deben import *
#    deben_configure()
    from miro import miro_xgraph
    from pilatus_utilities import pilatus_dawn, pilatus_preview_on


print 
print "==================================================="
print "local station initialisation completed - GDA is now ready for use!"
