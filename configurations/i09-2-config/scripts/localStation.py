# file: localStation.py
# Description: For beamline specific initialisation.
# @author: Fajin Yuan / James Mudd
# updated 5/1/2017
import os
from gda.factory import Finder
import java
from gda.data import NumTracker
from gda.jython import InterfaceProvider
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
i09_2NumTracker = NumTracker("i09");
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
    filenumber = i09_2NumTracker.getCurrentFileNumber();
    return os.path.join(curdir,str(filenumber))
    
alias("lwf")
print "    nwf : next working file path;"
# function to find the next working file path
def nwf():
    '''query the absolute path of the next working file'''
    curdir = InterfaceProvider.getPathConstructor().createFromDefaultProperty()
    filenumber = i09_2NumTracker.getCurrentFileNumber();
    return os.path.join(curdir,str(filenumber+1))
    
alias("nwf")
print "    nfn : next file number;"
# function to find the next scan number
def nfn():
    '''query the next file number'''
    filenumber = i09_2NumTracker.getCurrentFileNumber();
    return filenumber+1
    
alias("nfn")
print "    cfn : current file number;"
# function to find the next scan number
def cfn():
    '''query the current file number'''
    filenumber = i09_2NumTracker.getCurrentFileNumber();
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

# Install standard scan processing
from gdascripts.scan.installStandardScansWithProcessing import * #@UnusedWildImport
scan_processor.rootNamespaceDict=globals()

# print
# print "-----------------------------------------------------------------------------------------------------------------"
# print "Create an 'dummyenergy' scannable which can be used for test energy scan in GDA. It moves dummy motor 'x' and 'y'"
# dummyenergy=BeamEnergy("dummyenergy", gap='x', dcm='y')
#print "Create an 'jenergy' scannable which can be used for energy scan in GDA. It moves both soft X-ray ID gap and PGM energy"

# 2017-10-13 James re-enable jenergy_old as the new way doesn't work. 
#jenergy=BeamEnergy("jenergy", gap='jgap',dcm="pgmenergy",undulatorperiod=60,lut="JIDCalibrationTable.txt")

print
print "-----------------------------------------------------------------------------------------------------------------"
#print "Create an 'jgap' scannable for soft X-ray ID gap"
#from pseudodevices.AppleIIIDScannable import Apple2IDScannableClass
#jgap=Apple2IDScannableClass("jgap","SR09J-MO-SERVC-01:BLGSET","SR09J-MO-SERVC-01:CURRGAPD","SR09J-MO-SERVC-01:BLGSETP","mm","%.5f", 0.002)
# James' temporary solution, this require to comment out Java PGM energy object
#from epics.motor.positionCompareMotorClass import PositionCompareMotorClass
#pgmenergy=PositionCompareMotorClass("pgmenergy", "BL09I-ENERGY-MOTOR-01.VAL", "BL09I-ENERGY-MOTOR-01.RBV", "BL09I-ENERGY-MOTOR-01.STOP", 0.015, "mm", "%.4f")

from functions import functionClassFor2Scannables
functionClassFor2Scannables.ROOT_NAMESPACE_DICT=globals()


# Create temporary devices for femtos this should be moved to Spring
sd9iamp9=DisplayEpicsPVClass("sd9iamp9", "BL09K-MO-SD-09:IAMP9:I","V","%f")
sd9iamp36=DisplayEpicsPVClass("sd9iamp36", "BL09K-MO-SD-09:IAMP36:I","V","%f")
sd11iamp7=DisplayEpicsPVClass("sd11iamp7", "BL09K-MO-SD-11:IAMP7:I","V","%f")

# Add a string to hold extra detectors it will be appended to analyser scans run from the GUI
# See uk.ac.diamond.daq.devices.specs.phoibos.ui.handlers.RunSequenceHandler
extraDetectors = ""

print "Create an 'jenergy', 'polarisation' and 'jenergypolarisation' scannables."
LH,LV,CR,CL=["LH","LV","CR","CL"]
from calibration.energy_polarisation_class import BeamEnergyPolarisationClass

jenergy=BeamEnergyPolarisationClass("jenergy", jidscannable, pgmenergy, lut="JIDEnergy2GapCalibrations.txt", polarisationConstant=True)  # @UndefinedVariable
jenergy.configure()
polarisation=BeamEnergyPolarisationClass("polarisation", jidscannable, pgmenergy, lut="JIDEnergy2GapCalibrations.txt", energyConstant=True)  # @UndefinedVariable
polarisation.configure()
jenergypolarisation=BeamEnergyPolarisationClass("jenergypolarisation", jidscannable, pgmenergy, lut="JIDEnergy2GapCalibrations.txt")  # @UndefinedVariable
jenergypolarisation.configure()
jenergypolarisation.setInputNames(["jenergy"])
jenergypolarisation.setExtraNames(["polarisation"])
print
print "=================================================================================================================";
print "Initialisation script complete."
print
###Must leave what after this line last.
