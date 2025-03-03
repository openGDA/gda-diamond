# file:        localStation.py
# Description: For beamline specific initialisation.
# @author: Fajin Yuan
# updated 26/06/2014
from types import NoneType
from java.io import File


print "=================================================================================================================";
print "Performing beamline I11-1 specific initialisation.";
print
from gda.data import NumTracker
from gda.jython import InterfaceProvider
from gda.jython.commands.GeneralCommands import alias, run
from gda.jython.commands.GeneralCommands import pause as enable_pause_or_interrupt
from gda.jython.commands.ScannableCommands import scan

from gda.configuration.properties import LocalProperties

from gdaserver import GDAMetadata as meta
print "-----------------------------------------------------------------------------------------------------------------"
print "Set scan returns to the original positions on completion to false (0); default is 0."
print "   To set scan returns to its start positions on completion please do:"
print "      >>>scansReturnToOriginalPositions=1"
scansReturnToOriginalPositions=0;
print
#Please change the following lines to add default scannables to i11 GDA server engine
#print "-----------------------------------------------------------------------------------------------------------------"
#print "Adding default scannable objects to GDA system: Io, Te"
#add_default Io #@UndefinedVariable
#add_default Ie #@UndefinedVariable

print "-----------------------------------------------------------------------------------------------------------------"
print "commands for directory/file operations: "
print "   >>>pwd - return the current data directory"
print "   >>>lwf - return the full path of the last working data file"
print "   >>>nwf - return the full path of the next working data file"
print "   >>>nfn - return the next data file number to be collected"
print "   >>>setSubdirectory('test') - change data directory to a sub-directory named 'test', created first if not exist"
print "   >>>getSubdirectory() - return the current sub-directory setting if exist"
print "Please note: users can only create sub-directory within their permitted visit data directory via GDA, not themselves."
print "To create another sub-directory 'child-test' inside a sub-directory 'test', you must specify the full path as 'test/child-test' "
# set up a nice method for getting the latest file path
i11JNumTracker = NumTracker("i11-1");

# function to find the working directory
def pwd():
    '''return the working directory'''
    cwd = InterfaceProvider.getPathConstructor().createFromDefaultProperty()
    return cwd

alias("pwd")

# function to find the last working file path
def lwf():
    '''return the last working file path root'''
    cwd = InterfaceProvider.getPathConstructor().createFromDefaultProperty()
    filenumber = i11JNumTracker.getCurrentFileNumber();
    return os.path.join(cwd,str(filenumber))

alias("lwf")

# function to find the next working file path
def nwf():
    '''query the next working file path root'''
    cwd = InterfaceProvider.getPathConstructor().createFromDefaultProperty()
    filenumber = i11JNumTracker.getCurrentFileNumber();
    return os.path.join(cwd,str(filenumber+1))

alias("nwf")

# function to find the next scan number
def nfn():
    '''query the next file number or scan number'''
    filenumber = i11JNumTracker.getCurrentFileNumber();
    return filenumber+1

alias("nfn")

# the subdirectory parts
def setSubdirectory(dirname):
    '''create a new sub-directory for data collection that follows'''
    Finder.find("GDAMetadata").setMetadataValue("subdirectory",dirname)
    try:
        os.mkdir(pwd())
    except :
        pass

def getSubdirectory():
    return Finder.find("GDAMetadata").getMetadataValue("subdirectory")

def setVisit(visit):
    meta['visit'] = visit

def getVisit():
    return meta['visit']

def resetDataDirectory():
    LocalProperties.set(LocalProperties.GDA_DATAWRITER_DIR, "/dls/i11-1/data/$year$/$visit$/$subdirectory$/")


def abspath(*bits):
    return os.path.abspath(os.path.join(*bits))

from gda.factory import Finder
from time import sleep  # @UnusedImport
import time
import java #@UnresolvedImport

print "-----------------------------------------------------------------------------------------------------------------"
print "create 'beam' object for get/set photon beam properties such as wavelength, energy"
beam = Finder.find("beam")
print "create 'beamline' object for access beamline parameters such as data directory"
beamline=Finder.find("beamline")
print "create 'sampleinfo' object for accessing Sample Information users provided in a spreadsheet."
sampleinfo=Finder.find("SampleInfo")

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
print "Create ETL detector objects, names: llimIe2, ulimIe2, pmtIe2"
from detector_control_pds import llimIe2, ulimIe2, pmtIe2, pds # pds is a list containing the other three
print "Available Detector objects are:"
print pds
print
print "-----------------------------------------------------------------------------------------------------------------"
print "Create ETL Detector voltage diagnose object"
from diagnostics import macDetectorDiagnostics
diagnoseMAC=macDetectorDiagnostics.MACDetectorDiagnostics("diagnoseMAC", pds, 100)
print "To diagnose MAC run: " + diagnoseMAC.getName()+".run()"
from diagnostics.diagnose import listOfDiagnoseticsObjects, rundiagnose #@UnusedImport
listOfDiagnoseticsObjects.append(diagnoseMAC)
print "To run all diagnose implemented for I11, use: rundiagnose() on command line."
print

print "-----------------------------------------------------------------------------------------------------------------"
print "Create method for load sample information spreadsheet to GDA system."
from loadfile import * #@UnusedWildImport
print

### set output format for scannables
globals()['dcm_energy'].setOutputFormat(["%10.7f"])
globals()['dcm_bragg'].setOutputFormat(["%10.7f"])

print "-----------------------------------------------------------------------------------------------------------------"
print "function to set wavelength >>>setwavelength(value)"
def setlambda(wavelength):
    wavelength=float(wavelength)
    beam.setWavelength(wavelength)

def setwavelength(wavelength):
    setlambda(wavelength)

print
print "-----------------------------------------------------------------------------------------------------------------"
import gda

from gda.device.scannable import DummyScannable
ds = DummyScannable("ds")

print
print "-----------------------------------------------------------------------------------------------------------------"
print "The default scannable list: "
list_defaults #@UndefinedVariable
print
print "-----------------------------------------------------------------------------------------------------------------"
print "Create an 'interruptable()' function which can be used to make for-loop interruptable in GDA."
print "    To use this, you must place 'interruptable()' call as the 1st or last line in your for-loop."
def interruptable():
    enable_pause_or_interrupt()

print
from timerelated import clock, t, dt, w #@UnusedImport

print "-----------------------------------------------------------------------------------------------------------------"
print "create extra pixium scannables: pixium_PUMode, pixium_BaseExposure, pixium_BaseAcquirePeriod, pixium_EarlyFrames, pixium_TotalCount,pixium_FanSpeed1,pixium_FanSpeed2,pixium_DetectorTemperature"
from i11utilities import createScannableFromPV, ConstantScannable, CalibrantScannable
try:
    pixium_TriggerMode=createScannableFromPV("pixium_TriggerMode", "BL11J-EA-DET-10:CAM:TriggerMode", addToNameSpace=True, getAsString=True, hasUnits=False)
    pixium_PUMode = DisplayEpicsPVClass('pixium_PUMode', 'BL11J-EA-DET-10:CAM:PuMode_RBV', 'PU', '%i')
    pixium_BaseExposure = DisplayEpicsPVClass('pixium_BaseExposure', 'BL11J-EA-DET-10:CAM:AcquireTime_RBV', 's', '%.3f')
    pixium_BaseAcquirePeriod = DisplayEpicsPVClass('pixium_BaseAcquirePeriod', 'BL11J-EA-DET-10:CAM:AcquirePeriod_RBV', 's', '%.3f')
    pixium_ExcludeEarlyFrames = createScannableFromPV("pixium_ExcludeEarlyFrames", "BL11J-EA-DET-10:CAM:MotionBlur", addToNameSpace=True, getAsString=True, hasUnits=False)

    pixium_TotalCount = DisplayEpicsPVClass('pixium_TotalCount', 'BL11J-EA-DET-10:STAT:Total_RBV', 'count', '%.0f')
    pixium_TimeStamp = DisplayEpicsPVClass('pixium_TimeStamp', 'BL11J-EA-DET-10:STAT:TimeStamp_RBV', 'time', '%.3f')

    pixium_DataType=createScannableFromPV("pixium_DataType", "BL11J-EA-DET-10:CAM:DataType", addToNameSpace=True, getAsString=True, hasUnits=False)
    pixium_ID = DisplayEpicsPVClass('pixium_ID', 'BL11J-EA-DET-10:STAT:UniqueId_RBV', 'no', '%.0f')
    pixium_Counter = DisplayEpicsPVClass('pixium_Counter', 'BL11J-EA-DET-10:CAM:ArrayCounter_RBV', 'no', '%.0f')
    pixium_FanSpeed1 = DisplayEpicsPVClass('pixium_FanSpeed1', 'BL11J-EA-DET-10:CAM:DetectorFan1Speed', 'rpm', '%.0f')
    pixium_FanSpeed2 = DisplayEpicsPVClass('pixium_FanSpeed2', 'BL11J-EA-DET-10:CAM:DetectorFan2Speed', 'rpm', '%.0f')
    pixium_DetectorTemperature = DisplayEpicsPVClass('pixium_DetectorTemperature', 'BL11J-EA-DET-10:CAM:DetectorTemperature', 'degree', '%.1f')
#     calibrant_name=CalibrantScannable("calibrant_name", "CeO2(NIST SRM 674b)")
#     sample_name=CalibrantScannable("sample_name", "Undefined")
except:
    print "cannot create extra pixium scannables"

from pixium_utils import checkPixiumMode
print "-----------------------------------------------------------------------------------------------------------------"
print "setup meta-data provider commands:meta_add, meta_ll, meta_ls, meta_rm "
from metashop import *  # @UnusedWildImport
import metashop

print "-----------------------------------------------------------------------------------------------------------------"
print "adding meta scannables to PIXIUM use: meta_add_allPIXIUM()"
_meta_scannables_names_PIXIUM = []
# append items to the list below as required
#_meta_scannables_names_PIXIUMi12.append("ring")
_meta_scannables_names_PIXIUM.append("pixium_PUMode")
_meta_scannables_names_PIXIUM.append("pixium_BaseExposure")
_meta_scannables_names_PIXIUM.append("pixium_BaseAcquirePeriod")
_meta_scannables_names_PIXIUM.append("pixium_EarlyFrames")

_meta_scannables_PIXIUM = []
def meta_add_allPIXIUM():
    for sname in _meta_scannables_names_PIXIUM:
        if type(Finder.find(sname)) is not NoneType:
            _meta_scannables_PIXIUM.append(Finder.find(sname))
        else:
            try:
                print "at adding: " + sname
                eval(sname)
                _meta_scannables_PIXIUM.append(eval(sname))
            except:
                msg = "\t Unable to find a meta scannable named: " + sname
                print msg
    for s in _meta_scannables_PIXIUM:
        metashop.meta_add(s)
alias("meta_add_allPIXIUM")

print "Remove meta scannables from PIXIUM, use: meta_rm_allPIXIUM()"
def meta_rm_allPIXIUM():
    for sname in _meta_scannables_names_PIXIUM:
        try:
            print "at removing: " + sname
            eval(sname)
            metashop.meta_rm(eval(sname))
        except:
            msg = "\t Unable to find a meta scannable named: " + sname
            print msg
alias("meta_rm_allPIXIUM")

def pad_hdf(t,n=1.0):
    scan(ds, 1.0, n, 1.0, pixium_hdf, t)  # @UndefinedVariable
    scaler2(1)  # @UndefinedVariable


alias("pad_hdf")
from lde.ldescan import *  # @UnusedWildImport
from lde import wait_for_calibration
alias("ldescan")

NDR=0
CAL=1
SAM=2

def lde(t, collectionType=SAM, n=1.0, det=pixium_hdf):  # @UndefinedVariable
    if (collectionType==NDR):
        #just collect raw image, no data reduction
        scan(ds, 1.0,n,1.0, det, t)  # @UndefinedVariable
    else:
        if (collectionType==CAL):
            meta['calibration_file'] = ''
            if (str(calibrantName.getPosition())=="Undefined"):  # @UndefinedVariable
                raise Exception("Calibrant name is not defined.")
            
            scan(ds, 1.0,n,1.0, det, t, calibration)  # @UndefinedVariable
            wait_for_calibration()      
        
        else:
            scan(ds, 1.0,n,1.0, det, t, process)  # @UndefinedVariable
            
alias("lde")

def lde_slugs(duration):
    lde(duration, SAM)
    return lastScanDataPoint().scanIdentifier

##### new objects must be added above this line ###############
print
print "=================================================================================================================";
print "Initialisation script complete."
print
###Must leave what after this line last.
bm1=Finder.find("bm")
if bm1.isBeamOn():
    print "PHOTON BEAM IS ON SAMPLE NOW."
else:
    print "NO PHOTON BEAM ON SAMPLE."

from fastshutterwrapper import FastShutter
fs = FastShutter(fastshutter1)

from perkin import perkin_dark_frame

import butlerWarning
butler_position_warning = butlerWarning.PositionerWarning('butler_position_warning', butlerArm, 'Retract')
add_default butler_position_warning

from lde.stageManagement import *
from lde.lde_robot import LdeRobot
sample = LdeRobot('sample', 'BL11J-EA-ROBOT-01:', robot_stage=((rsx, -239.934), (rsy, 0)))

from standardScan import * #@UnusedWildImport

from config_tests import slug_trigger

def get_wavelength_from_poni(poni_file=None):
    wavelength = 0.0
    if poni_file is None:
        # get the poni from the meta
        poni_file = meta.getMetadataValue("calibration_file")
        if str(poni_file) == "":
            print "no poni file supplied and none in the meta object" 
            return wavelength
    try:
        with open(poni_file, 'r') as f:
            file_contents = f.readlines()
        for line in file_contents:
            if "Wavelength" in line:
                wavelength = float(line.split(' ')[1].replace("\n", ""))
    except:
        print("get_wavelength_from_poni() has been run, but could not extract wavelength from file")
    return wavelength * 1e10

wavelength = get_wavelength_from_poni()

if wavelength == 0:
    print("running 'lde n CAL' first will set the wavelength calibration file")




