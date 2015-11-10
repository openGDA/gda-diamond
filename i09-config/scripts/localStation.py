# file:        localStation.py
# Description: For beamline specific initialisation.
# @author: Fajin Yuan
# updated 19/06/2012
import os
from gda.factory import Finder
import java
from gda.data import PathConstructor, NumTracker
from gda.jython.commands import GeneralCommands
from calibration.Energy_class import BeamEnergy
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
    curdir = PathConstructor.createFromDefaultProperty()
    return curdir
    
alias("pwd")
print "    lwf : last working file path;"
# function to find the last working file path
def lwf():
    '''return the absolute path of the last working file'''
    curdir = PathConstructor.createFromDefaultProperty()
    filenumber = i09NumTracker.getCurrentFileNumber();
    return os.path.join(curdir,str(filenumber))
    
alias("lwf")
print "    nwf : next working file path;"
# function to find the next working file path
def nwf():
    '''query the absolute path of the next working file'''
    curdir = PathConstructor.createFromDefaultProperty()
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
print "Load utilities: printJythonEnvironment(), caget(pv), caput(pv,value), attributes(object), "
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
for processor in scan_processor.processors:
    scan_processor.processors.remove(processor)
peakdata=ExtractPeakParameters()
scan_processor.processors.append(peakdata)
gdascripts.scan.concurrentScanWrapper.PRINTTIME = False
gdascripts.scan.concurrentScanWrapper.ROOT_NAMESPACE_DICT = globals()
scan_processor.rootNamespaceDict=globals()
#scan_processor.duplicate_names = {'maxval':'maxpos', 'minval':'minpos'}
#scan_processor.processors.append(Lcen())
#scan_processor.processors.append(Rcen())


###############################################################################
###                   Configure scannable output formats                        ###
###############################################################################
globals()['sm3pitch'].setOutputFormat(["%10.1f"])
#globals()['bragg'].setOutputFormat(["%10.7f"])    

#print "-----------------------------------------------------------------------------------------------------------------"
#print "Setup 'plot' function for plotting collected, use 'help plot' for syntax"
#from plot import plot, plotover, plotdata #@UnusedImport
#print


print
print "-----------------------------------------------------------------------------------------------------------------"
print "Create an 'ienergy' scannable which can be used for energy scan in GDA. It moves both hard X-ray ID gap and DCM energy"
ienergy=BeamEnergy("ienergy", gap='igap',dcm="dcmenergy",undulatorperiod=27,lut="IIDCalibrationTable.txt")
print "Create an 'dummyenergy' scannable which can be used for test energy scan in GDA. It moves dummy motor 'x' and 'y'"
dummyenergy=BeamEnergy("dummyenergy", gap='x', dcm='y')
print "Create an 'jenergy' scannable which can be used for energy scan in GDA. It moves both soft X-ray ID gap and PGM energy"
jenergy=BeamEnergy("jenergy", gap='jgap',dcm="pgmenergy",undulatorperiod=60,lut="JIDCalibrationTable.txt")

print
print "-----------------------------------------------------------------------------------------------------------------"
#print "Create an 'jgap' scannable for soft X-ray ID gap"
#from pseudodevices.AppleIIIDScannable import Apple2IDScannableClass
#jgap=Apple2IDScannableClass("jgap","SR09J-MO-SERVC-01:BLGSET","SR09J-MO-SERVC-01:CURRGAPD","SR09J-MO-SERVC-01:BLGSETP","mm","%.5f", 0.002)
# James' temporary solution, this require to comment out Java PGM energy object
#from epics.motor.positionCompareMotorClass import PositionCompareMotorClass
#pgmenergy=PositionCompareMotorClass("pgmenergy", "BL09I-ENERGY-MOTOR-01.VAL", "BL09I-ENERGY-MOTOR-01.RBV", "BL09I-ENERGY-MOTOR-01.STOP", 0.015, "mm", "%.4f")

    

print "Create an 'analyserscan' command for scanning the electron analyser."
#from command.analyser_scan import analyserscan, analyserscan_v1, zerosupplies, analyserscancheck # @UnusedImport
from command.analyserScan import analyserscan, zerosupplies, analyserscancheck, analyserscan_v1  # @UnusedImport
alias("zerosupplies")
alias("analyserscan")
alias("analyserscan_v1")
alias("analyserscancheck")
print "Create shutter objects 'psi2' for hard X-ray, 'psj2' for soft X-ray."
#from pseudodevices.shutter import EpicsShutterClass, psi2,psj2  # @UnusedImport
nixswr=DisplayEpicsPVClass("nixswr", "BL09I-MO-ES-03:STAT:Total_RBV","","%d")
lakeshoreC0=DisplayEpicsPVClass("lakeshoreC0", "BL09L-VA-LAKE-01:KRDG0","K","%f")
lakeshoreC1=DisplayEpicsPVClass("lakeshoreC1", "BL09L-VA-LAKE-01:KRDG1","K","%f")
lakeshoreC2=DisplayEpicsPVClass("lakeshoreC2", "BL09L-VA-LAKE-01:KRDG2","K","%f")
lakeshoreC3=DisplayEpicsPVClass("lakeshoreC3", "BL09L-VA-LAKE-01:KRDG3","K","%f")

# Import and setup function to create mathmatical scannables
from functions import functionClassFor2Scannables
functionClassFor2Scannables.ROOT_NAMESPACE_DICT=globals()

# These scannables have been removed as I believe they are not used
#print "Create a 'ratioi20toi19' scannable for the ratio of hm3iamp20 to bfmiamp19."
#from functions.ratioscannable import ratioi20toi19  # @UnusedImport
#print "Create a 'dri20toi19' scannable for the derivative of hm3iamp20 to bfmiamp19."
#from functions.derivativescannable import dri20toi19  # @UnusedImport


##### new objects must be added above this line ###############
def enablefeedbackdcmfroll():
    caput("BL09I-EA-FDBK-01:ENABLE",0)
def disablefeedbackdcmfroll():
    caput("BL09I-EA-FDBK-01:ENABLE",1)
def enablefeedbackdcmfpitch():
    caput("BL09I-EA-FDBK-02:ENABLE",0)
def disablefeedbackdcmfpitch():
    caput("BL09I-EA-FDBK-02:ENABLE",1)
def enablefeedbacksm1fpitch():
    caput("BL09J-EA-FDBK-01:ENABLE",0)
def disablefeedbacksm1fpitch():
    caput("BL09J-EA-FDBK-01:ENABLE",1)
    
alias("enablefeedbackdcmfroll")
alias("disablefeedbackdcmfroll")
alias("enablefeedbackdcmfpitch")
alias("disablefeedbackdcmfpitch")
alias("enablefeedbacksm1fpitch")
alias("disablefeedbacksm1fpitch")
print
print "=================================================================================================================";
print "Initialisation script complete." 
print
###Must leave what after this line last.
