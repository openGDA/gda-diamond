# file:        localStation.py
# Description: For beamline specific initialisation.
# @author: Fajin Yuan
# updated 23/12/2010
# removed gasRig to a separate script - loadGasRig.py 10/09/2015

print "=================================================================================================================";
print "Performing beamline I11 specific initialisation.";
print
from gda.data import NumTracker
from gda.jython import InterfaceProvider
from gda.jython.commands.GeneralCommands import alias, run
from gda.jython.commands.GeneralCommands import pause as enable_pause_or_interrupt
from gda.jython.commands.ScannableCommands import scan
import os

from gdaserver import GDAMetadata as meta

import logging
logger = logging.getLogger('i11.localStation')

from userlogging import UserLog
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
i11NumTracker = NumTracker("i11");

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
    filenumber = i11NumTracker.getCurrentFileNumber();
    return os.path.join(cwd,str(filenumber))

alias("lwf")

# function to find the next working file path
def nwf():
    '''query the next working file path root'''
    cwd = InterfaceProvider.getPathConstructor().createFromDefaultProperty()
    filenumber = i11NumTracker.getCurrentFileNumber();
    return os.path.join(cwd,str(filenumber+1))

alias("nwf")

# function to find the next scan number
def nfn():
    '''query the next file number or scan number'''
    filenumber = i11NumTracker.getCurrentFileNumber();
    return filenumber+1

alias("nfn")

# the subdirectory parts
def setSubdirectory(dirname):
    '''create a new sub-directory for data collection that follows'''
    meta["subdirectory"] = dirname
    try:
        os.mkdir(pwd())
    except :
        pass

def getSubdirectory():
    return meta["subdirectory"]

def getVisit():
    return meta['visit']

def setVisit(new_visit):
    previous = meta['visit']
    meta['visit'] = new_visit
    logger.info("Visit changed from %s to %s", previous, new_visit)

alias('setVisit')
print

def setCalibrationFile(file):
    logger.info("Calibration file changed manually to %s", file)
    meta['calibration_file'] = file

def getCalibrationFile():
    return meta['calibration_file']

from gda.factory import Finder
from time import sleep  # @UnusedImport
import java #@UnresolvedImport

print "-----------------------------------------------------------------------------------------------------------------"
print "create 'beam' object for get/set photon beam properties such as wavelength, energy"
beam = Finder.find("beam")
print "create 'beamline' object for access beamline parameters such as data directory"
beamline=Finder.find("beamline")

print
print "-----------------------------------------------------------------------------------------------------------------"
print "load EPICS Pseudo Device utilities for creating scannable object from a PV name."
from gdascripts.pd.epics_pds import * #@UnusedWildImport
print
print "-----------------------------------------------------------------------------------------------------------------"
print "load time utilities for creating timer objects."
from gdascripts.pd.time_pds import * #@UnusedWildImport
timestamp = actualTimeClass('timestamp')
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
print "Create ETL detector objects, names: llimxy, ulimxy, pmtxy, "
print "    where x is MAC stage number (1,.., 5); y is detector number (1,..,9)"
from detector_control_pds import * #@UnusedWildImport
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
print

#print 'setting up PDs for QBPMs'
#execfile(gdaScriptDir+"qbpm_pd_class.py");

### set output format for scannables
globals()['tth'].setOutputFormat(["%10.7f"])

print "-----------------------------------------------------------------------------------------------------------------"
print "function to set wavelength >>>setwavelength(value)"
def setlambda(wavelength):
    wavelength=float(wavelength)
    beam.setWavelength(wavelength)

def setwavelength(wavelength):
    setlambda(wavelength)


def scantth(*args, **kwargs):
    """
    Wrapper around scan which ensures diffractometer gets set to step scan mode
    to prevent mechanical vibrations, and then puts it back to cvscan mode at
    the end of the scan.
    """
    # Change to step scan mode
    caput("BL11I-MO-DIFF-01:WRITEMODE", 1)
    try:
        scan(tth, *args, **kwargs)  # @UndefinedVariable
    finally:
        # Put back to CV scan mode at the end.
        caput("BL11I-MO-DIFF-01:WRITEMODE", 0)

alias("scantth")

print
print "-----------------------------------------------------------------------------------------------------------------"
print "Setup PSD or mythen detector system."
import gda

from gda.device.scannable import DummyScannable
ds = DummyScannable("ds")

def psd(t,n=1.0, *others):
    scan(ds, 1.0, n, 1.0, mythen, t, Io, t, Ie, delta, *others)  # @UndefinedVariable
    scaler2(1)  # @UndefinedVariable


alias("psd")

print
print "-----------------------------------------------------------------------------------------------------------------"
print "The default scannable list: "
list_defaults #@UndefinedVariable
sleep(0.5)


print
print "-----------------------------------------------------------------------------------------------------------------"
print "create detector collision prevention commands: 'move' and 'asynmove' "
print "    move -- synchronous, blocking until completed, like 'pos'        "
print "    asynmove -- asynchronous, non-blocking move                      "
#from avoidcollision import *  # @UnusedWildImport
run("avoidcollision.py")

# print
# print "-----------------------------------------------------------------------------------------------------------------"
# print "method to change MYTHEN flat field file dynamically, temporarily. "
# print "    >>>setMythenFlatFieldFile('flatfield_filename')"
# print "This must be called each time you reset_namespce or restart GDA servers"
# def setMythenFlatFieldFile(filename):
#     mythen_flat_field = gda.device.detector.mythen.data.MythenRawDataset(java.io.File(filename))
#     mythen.getDataConverter().setFlatFieldData(mythen_flat_field)  # @UndefinedVariable

# print 'Method to reprocess mythen files: process_mythen_scans'
# from mythen_processing import process_mythen_scans

print
print "---------------------------------------------------------numFrames--------------------------------------------------------"
print "Create rocking theta scannable 'rocktheta'"
print "    To change the rocking limits, use 'rocktheta.setLowerLimit(10)', 'rocktheta.setUpperLimit(10)'; "
print "    To view the rocking limits, use 'rocktheta.getLowerLimit()', 'rockthets.getUpperLimit()'."
from rockingMotion_class import RockingMotion, PmacRock
pmac = PmacRock('BL11I-MO-DIFF-01:ROCK:')
theta1=Finder.find("theta")
rocktheta=RockingMotion("rocktheta", theta1, -10, 10)
print "Create 'psdrt' command for PSD data collection with theta rocking"
def psdrt(t, n=1.0):
    scan(ds, 1.0, n, 1.0, mythen, t, rocktheta, Io, t, Ie, delta)  # @UndefinedVariable
    scaler2(1)  # @UndefinedVariable

alias("psdrt")

print
print "-----------------------------------------------------------------------------------------------------------------"
print "Create commands to enable/disable plot update from server."
print "    To enable plot update from server, use 'startupdate'"
print "    To disable plot update from server, use 'stopupdate'"
print "    The default is plot update enabled."
# set plot update rule in GDA server:
LIVE=True
def stopupdate():
    global LIVE
    LIVE=False

def startupdate():
    global LIVE
    LIVE=True

alias("startupdate")
alias("stopupdate")

print
print "-----------------------------------------------------------------------------------------------------------------"
print "Create an 'interruptable()' function which can be used to make for-loop interruptable in GDA."
print "    To use this, you must place 'interruptable()' call as the 1st or last line in your for-loop."
def interruptable():
    enable_pause_or_interrupt()
print "-----------------------------------------------------------------------------------------------------------------"
print "Create 'cvscan' command"
alias("cvscan")
print
from timerelated import clock, t, dt, w #@UnusedImport
print
print "-----------------------------------------------------------------------------------------------------------------"
print "create 'adc2' object to provide access to ADC2 device"
from peloop.adccontrol import AdcControl
adc2=AdcControl("adc2")
print "create 'fg2' object to provide access to the 2nd Function generator device"
from peloop.functiongenerator import FunctionGenerator
fg2=FunctionGenerator("fg2")

# try:
#     from gdaserver import tfg
# except ImportError:
#     print 'tfg not available - not creating peloop tfg devices'
# else:
#     print "create 'tfg2' object to provide control of Time Frame Generator device"
#     from peloop.tfg2 import TFG2
#     tfg2=TFG2("tfg2")
#
#     print "create 'pedata' object to capture the PE data from ADC2 device"
#     from peloop.pedatacapturer import DataCapturer
#     pedata=DataCapturer("pedata")
#     print "create 'pel' object for PE Loop experiment"
#     from tfg_peloop import PELoop
#     pel=PELoop("pel", tfg2, fg2, adc2, pedata, mythen)  # @UndefinedVariable
#     daserver=Finder.find("daserver")


print "-----------------------------------------------------------------------------------------------------------------"
print "create derivative scannable 'deriv' object to provide derivative value of enegry to elt1"
from scan_detetor_with_derivative import DeviceDerivativeClass
deriv = DeviceDerivativeClass("deriv", "energy", "etl1", "derivative");

print "-----------------------------------------------------------------------------------------------------------------"
print "setup meta-data provider commands:meta_add, meta_ll, meta_ls, meta_rm "
import metashop  # @UnusedImport

print '-----------------------------------------------------------------------------------------------------------------'
print 'setup barcode reader'
from barcode import reader
scanner = reader.BarcodeReader('scanner', 'BL11I-EA-BARCR-01:DATA:', 'BL11I-EA-ROBOT-01:')
print '-----------------------------------------------------------------------------------------------------------------'

##### new objects must be added above this line ###############
###Must leave what after this line last.
bm1=Finder.find("bm")
bm1.on()
sleep(2)

if bm1.isBeamOn():
    print "PHOTON BEAM IS ON SAMPLE NOW."
else:
    print "NO PHOTON BEAM ON SAMPLE."

from gda.device.enumpositioner import EpicsSimpleBinary
turbo = EpicsSimpleBinary()
turbo.name = 'turbo'
turbo.positions = ['On', 'Off']
turbo.pvName = 'BL11I-CG-CSTRM-01:TURBO'
turbo.configure()

def turboOn(): turbo('On')
def turboOff(): turbo('Off')

import exposure
radiation = exposure.RadiationExposure('radiation', fastshutter)
radiation.configure()

# Set up csb monitoring for csb2.
from csb_pid import CsbPidMonitor
csb2_p_monitor = CsbPidMonitor(csb2, upper=251, lower=249, high_p=150, low_p=300)
csb2.addIObserver(csb2_p_monitor)
add_reset_hook(lambda obs=csb2_p_monitor: csb2.deleteIObserver(obs))

from standardScan import * #@UnusedWildImport
#from gdascripts.scan.installStandardScansWithProcessing import * # @UnusedWildImport

def align_pitch(centre=None):
    if centre is not None: dcm_pitch(centre)
    rscan(dcm_pitch, -1.2, 1.2, 0.05, Io, 1, Ie, 1)
    scan_processor.go(peak)

# Run any configuration needed for things under active development
from config_tests import *
# config_tests can be found in /dls_sw/i11/scripts/config_tests

add_default delta # this is needed to angular correct the mythen_nx detector when it is used statically eg scan ds 1 1 1
add_default dcm_energy #useful to know for all experiments

try:
    from Mythen3RebootScannable import CMS
    cms1 = CMS()
except:
    pass

print
print "=================================================================================================================";
print "Initialisation script complete."
print
