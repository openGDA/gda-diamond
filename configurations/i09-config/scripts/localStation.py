# file:        localStation.py
# Description: For beamline specific initialisation.
# @author: Fajin Yuan
# updated 19/06/2012
import os
from gda.factory import Finder
import java
from gda.data import NumTracker
from gda.jython import InterfaceProvider
from gda.jython.commands import GeneralCommands
from calibration.soft_energy_class import SoftEnergy
from calibration.hard_energy_class import HardEnergy
from gda.jython.commands.GeneralCommands import vararg_alias, alias
from gda.jython.commands.ScannableCommands import scan 
from gdascripts.pd.time_pds import showtimeClass, showincrementaltimeClass,\
    waittimeClass, waittimeClass2, actualTimeClass
from gda.configuration.properties import LocalProperties
import gdascripts
from gdascripts.analysis.datasetprocessor.oned.scan_stitching import Lcen, Rcen
from analysis.ScanDataAnalysis import FindScanCentroid, FindScanPeak
from gdascripts.analysis.datasetprocessor.oned.extractPeakParameters import ExtractPeakParameters
from gda.util import PropertyUtils
import sys
from java.lang import System
from org.opengda.detector.electronanalyser.utils import FilenameUtil
from gdaserver import sd1_cam, sd3_cam

print "=================================================================================================================";
print "Performing beamline specific initialisation code (i09).";
print "=================================================================================================================";


print "-----------------------------------------------------------------------------------------------------------------"
print "Set if scan returns to the original positions on completion."
print "    scansReturnToOriginalPositions=0, not return to its start position (the default);"
print "    scansReturnToOriginalPositions=1, return to its start position;"
scansReturnToOriginalPositions=0;
print
finder=Finder.getInstance()

_epicsScriptLibraryDir = PropertyUtils.getExistingDirFromLocalProperties("gda.install.git.loc") + "/gda-epics.git/uk.ac.gda.epics/scripts" + System.getProperty("file.separator");
sys.path.append(_epicsScriptLibraryDir)

###############################################################################
###                            Generic Functions                            ###
###############################################################################

print "-----------------------------------------------------------------------------------------------------------------"
print "create directory operation commands: "
i09NumTracker = NumTracker("i09");
print "    pwd : present working directory;"
# function to find the working directory
def pwd():
    '''return the current working directory'''
    curdir = InterfaceProvider.getPathConstructor().createFromDefaultProperty()
    return curdir
    
alias("pwd")
print "    lwf : last working file path;"
# function to find the last working file path
def lwf():
    '''return the absolute path of the last working file'''
    curdir = InterfaceProvider.getPathConstructor().createFromDefaultProperty()
    filenumber = i09NumTracker.getCurrentFileNumber();
    return os.path.join(curdir,str(filenumber))
    
alias("lwf")
print "    nwf : next working file path;"
# function to find the next working file path
def nwf():
    '''query the absolute path of the next working file'''
    curdir = InterfaceProvider.getPathConstructor().createFromDefaultProperty()
    filenumber = i09NumTracker.getCurrentFileNumber();
    return os.path.join(curdir,str(filenumber+1))
    
alias("nwf")
print "    nfn : next file number;"
# function to find the next scan number
def nfn():
    '''query the next file number'''
    filenumber = i09NumTracker.getCurrentFileNumber();
    return filenumber+1
    
alias("nfn")
print "    cfn : current file number;"
# function to find the next scan number
def cfn():
    '''query the current file number'''
    filenumber = i09NumTracker.getCurrentFileNumber();
    return filenumber
    
alias("cfn")
print "    setSubdirectory('newdir/newsubdir')"
# the subdirectory parts
def setSubdirectory(dirname):
    '''create a new sub-directory for data collection that follows'''
    finder.find("GDAMetadata").setMetadataValue("subdirectory",dirname)
    try:
        os.mkdir(pwd())
    except :
        pass
print

### Create time Scannables
print "Creating time scannables"
from timerelated import clock, t, dt, w #@UnusedImport
showtime=showtimeClass('Showtime')
inctime=showincrementaltimeClass('inctime')
waittime=waittimeClass2('Waittime')
atime=actualTimeClass('atime')

### Pipeline    
def configureScanPipeline(length = None, simultaneousPoints = None):
    lengthProp = LocalProperties.GDA_SCAN_MULTITHREADED_SCANDATA_POINT_PIPElINE_LENGTH
    simultaneousProp = LocalProperties.GDA_SCAN_MULTITHREADED_SCANDATA_POINT_PIPElINE_POINTS_TO_COMPUTE_SIMULTANEOUSELY
    def show():
        print "ScanDataPoint pipeline:"
        print " " + lengthProp + " = " + LocalProperties.get(lengthProp, '4') # duplicated in ScannableCommands
        print " " + simultaneousProp + " = " + LocalProperties.get(simultaneousProp, '3') # duplicated in ScannableCommands
    if (length == None) or (simultaneousPoints == None):
        show()
    else:
        LocalProperties.set(lengthProp, `length`)
        LocalProperties.set(simultaneousProp, `simultaneousPoints`)
        show()

alias('configureScanPipeline')

print "-----------------------------------------------------------------------------------------------------------------"
print "create 'beam' object for get/set photon beam properties such as wavelength, energy"
beam = finder.find("beam")
print "create 'beamline' object for access beamline parameters such as data directory"
beamline=finder.find("beamline")

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
print

print "-----------------------------------------------------------------------------------------------------------------"
print "function to set wavelength >>>setwavelength(value)"
def setlambda(wavelength):
    wavelength=float(wavelength)
    beam.setWavelength(wavelength)

def setwavelength(wavelength):
    setlambda(wavelength)

print
print "-----------------------------------------------------------------------------------------------------------------"
print "Create an 'interruptable()' function which can be used to make for-loop interruptable in GDA."
print "    To use this, you must place 'interruptable()' call as the 1st or last line in your for-loop."
def interruptable():
    GeneralCommands.pause()

###############################################################################
###                   Configure scan data processing                        ###
###############################################################################

print "Importing analysis commands (findpeak, findcentroid & enable scan data processes)"
findpeak=FindScanPeak 
findcentroid=FindScanCentroid 

from gdascripts.scan.installStandardScansWithProcessing import * #@UnusedWildImport
scan_processor.rootNamespaceDict=globals()


###############################################################################
###                   Configure camera bases                                    ###
###############################################################################

from pseudodevices.CameraExposureChanger import CameraExposureChanger

print "\nCreating camera exposure object ('sd1_camera_exposure')for SD1 camera"
sd1_camera_exposure = CameraExposureChanger(sd1_cam)

print "\nCreating camera exposure object ('sd3_camera_exposure')for SD3 camera"
sd3_camera_exposure = CameraExposureChanger(sd3_cam)
###############################################################################
###                   Configure scannable output formats                        ###
###############################################################################
globals()['sm3pitch'].setOutputFormat(["%10.1f"])

from pseudodevices.IDGap_Offset import igap_offset, jgap_offset
print
print "-----------------------------------------------------------------------------------------------------------------"
print "Create an 'ienergy' scannable which can be used for energy scan in GDA. It moves both hard X-ray ID gap and DCM energy"
ienergy = HardEnergy("ienergy", "IIDCalibrationTable.txt", gap_offset=igap_offset, feedbackPVs=['BL09I-EA-FDBK-01:ENABLE','BL09I-EA-FDBK-02:ENABLE'])
#ienergy = HardEnergy("ienergy", "IIDCalibrationTable.txt", feedbackPVs=['BL09I-EA-FDBK-01:ENABLE','BL09I-EA-FDBK-02:ENABLE'])
# print "Create an 'dummyenergy' scannable which can be used for test energy scan in GDA. It moves dummy motor 'x' and 'y'"
# dummyenergy=BeamEnergy("dummyenergy", gap='x', dcm='y')
print "Create an 'jenergy' scannable which can be used for energy scan in GDA. It moves both soft X-ray ID gap and PGM energy"
jenergy=SoftEnergy("jenergy", "JIDCalibrationTable.txt", gap_offset=jgap_offset, feedbackPV='BL09J-EA-FDBK-01:ENABLE')
#jenergy=SoftEnergy("jenergy", "JIDCalibrationTable.txt", feedbackPV='BL09J-EA-FDBK-01:ENABLE')

print
print "-----------------------------------------------------------------------------------------------------------------"


print "Create an 'analyserscan' command for scanning the electron analyser."
from command.analyserScan import analyserscan, zerosupplies, analyserscancheck, analyserscan_v1  # @UnusedImport
alias("zerosupplies")
alias("analyserscan")
alias("analyserscan_v1")
alias("analyserscancheck")
print "Create shutter objects 'psi2' for hard X-ray, 'psj2' for soft X-ray."

nixswr=DisplayEpicsPVClass("nixswr", "BL09I-MO-ES-03:STAT:Total_RBV","","%d")

# Import and setup function to create mathmatical scannables
from functions import functionClassFor2Scannables
functionClassFor2Scannables.ROOT_NAMESPACE_DICT=globals()

# I09-70 Create a empty string to hold detectors to be used with the GUI
extraDetectors = ""

# Install regional scan
print "Installing regional scan"
from gdascripts.scan.RegionalScan import RegionalScanClass
mrscan = RegionalScanClass()
alias('mrscan')

#check beam scannables
from pseudodevices.checkbeamscannables import checkbeam, checkrc, checkfe, checktopup_time, checkbeamdetector, detectorpausecontrol, checkdetector  # @UnusedImport
#create 'move' command
run("/dls_sw/i09/software/gda/config/scripts/command/checkedMotion.py")  # @UndefinedVariable

from scannable.continuous.continuous_energy_scannables import cenergy, mcs2, mcs3, mcs4, mcs5  # @UnusedImport
from scan.cvscan import cvscan  # @UnusedImport

print
print "=================================================================================================================";
print "Initialisation script complete." 
print
###Must leave what after this line last.
