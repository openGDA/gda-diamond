# file:        localStation.py
# Description: For beamline specific initialisation.
# @author: Fajin Yuan
# updated 23/12/2010


print "=================================================================================================================";
print "Performing beamline I11 specific initialisation.";
print
from gda.data import PathConstructor, NumTracker
from gda.jython.commands.GeneralCommands import alias, run
from gda.jython.commands.GeneralCommands import pause as enable_pause_or_interrupt
from gda.jython.commands.ScannableCommands import scan 
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
    cwd = PathConstructor.createFromDefaultProperty()
    return cwd
    
alias("pwd")

# function to find the last working file path
def lwf():
    '''return the last working file path root'''
    cwd = PathConstructor.createFromDefaultProperty()
    filenumber = i11NumTracker.getCurrentFileNumber();
    return os.path.join(cwd,str(filenumber))
    
alias("lwf")

# function to find the next working file path
def nwf():
    '''query the next working file path root'''
    cwd = PathConstructor.createFromDefaultProperty()
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
    finder.find("GDAMetadata").setMetadataValue("subdirectory",dirname)
    try:
        os.mkdir(pwd())
    except :
        pass
    
def getSubdirectory():
    return finder.find("GDAMetadata").getMetadataValue("subdirectory")

print

from gda.factory import Finder
from time import sleep  # @UnusedImport
import java #@UnresolvedImport

finder=Finder.getInstance()
print "-----------------------------------------------------------------------------------------------------------------"
print "create 'beam' object for get/set photon beam properties such as wavelength, energy"
beam = finder.find("beam")
print "create 'beamline' object for access beamline parameters such as data directory"
beamline=finder.find("beamline")
print "create 'sampleinfo' object for accessing Sample Information users provided in a spreadsheet."
sampleinfo=finder.find("SampleInfo")

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
print "Create method for load sample information spreadsheet to GDA system."
from loadfile import * #@UnusedWildImport
print

print "-----------------------------------------------------------------------------------------------------------------"
print "Enable automatic beamline energy setting for all devices by e.g. 'pos setenergy 15.0'."
ALL, BEAM_ENERGY, STAGE_ANGLE, DETECTOR=range(4)
from Automation_class import Automation
setenergy=Automation('setenergy','energytable', ALL, rootNameSpace=globals())
print "To set/get Mono and ID energy only, use 'energy_gap' object"
energy_gap=Automation('energy_gap','energytable', BEAM_ENERGY, rootNameSpace=globals())
print "To set/get MAC stage angles to specific energy, use 'mac_energy' object"
mac_energy=Automation('mac_energy','energytable', STAGE_ANGLE, rootNameSpace=globals())
print "To set/get ETL detector voltages to specific energy, use 'det_energy' object"
det_energy=Automation('det_energy','energytable', DETECTOR, rootNameSpace=globals())
pds.append(setenergy) 
pds.append(energy_gap) 
pds.append(mac_energy) 
pds.append(det_energy) 
print

#print 'setting up PDs for QBPMs'
#execfile(gdaScriptDir+"qbpm_pd_class.py");

### set output format for scannables
globals()['tth'].setOutputFormat(["%10.7f"])
globals()['energy'].setOutputFormat(["%10.7f"])
globals()['bragg'].setOutputFormat(["%10.7f"])    

print "-----------------------------------------------------------------------------------------------------------------"
print "Setup 'plot' function for plotting collected, rebinned MAC data. use 'help plot' for syntax"
from plot import plot, plotover, plotdata, PSD,MAC,SRS #@UnusedImport
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
print "Setup PSD or mythen detector system."
import gda

# These can be changed
mythen_bad_channels_file = "/dls/i11/software/mythen/diamond/calibration/badchannel_detector_standard.list"
mythen_ang_cal_params_file = "/dls/i11/software/mythen/diamond/calibration/ang.off"
# Flat field file
mythen_flat_field_file = "/dls/i11/software/mythen/diamond/flatfield/current_flat_field_calibration"
# E=12 keV
#mythen_flat_field_file = "/dls/i11/software/mythen/diamond/flatfield/Sum_Flat_Field_E12keV_T6keV_2011May09.raw"
#mythen_flat_field_file = "/dls/i11/software/mythen/diamond/flatfield/Flat_Field_Sum_E12keV_09Jul2012.raw"
# E = 25 keV
# mythen_flat_field_file = "/dls/i11/data/2010/ee0/PSD/20100707/sum_flat_field_E25keV_T12500eV_2010July07.raw"
# E=15 keV 15 Sep 2011 file
#mythen_flat_field_file = "/dls/i11/software/mythen/diamond/flatfield/Sum_Flat_Field_E15keV_T_7500eV_2011Sep15.raw"
# E=15 keV 09 Dec 2011 file
#mythen_flat_field_file = "/dls/i11/software/mythen/diamond/flatfield/Sum_Flat_Field_E15keV_T7500eV_2011Dec09.raw"
#mythen_flat_field_file = "/dls/i11/software/mythen/diamond/flatfield/Sum_Flat_Field_E15keV_T7500eV_19Apr2012.raw"
#flat filed file 03 May 2012 with new controller
#mythen_flat_field_file = "/dls/i11/software/mythen/diamond/flatfield/Sum_Flat_Field_E15keV_T7500eV_03May2012.raw"
mythen_data_directory = "/dls/i11/data/2009/ee0"

mythen_client = gda.device.detector.mythen.client.TextClientMythenClient()
mythen_client.setHost("i11-mcs02")
#mythen_client = gda.device.detector.mythen.client.DummyMythenClient(18)

mythen_bad_channels = gda.device.detector.mythen.data.FileBadChannelProvider(java.io.File(mythen_bad_channels_file))
mythen_ang_cal_params = gda.device.detector.mythen.data.AngularCalibrationParametersFile(java.io.File(mythen_ang_cal_params_file))
mythen_flat_field = gda.device.detector.mythen.data.MythenRawDataset(java.io.File(mythen_flat_field_file))

mythen_data_converter = gda.device.detector.mythen.data.DataConverter()
mythen_data_converter.setBadChannelProvider(mythen_bad_channels)
mythen_data_converter.setAngularCalibrationParameters(mythen_ang_cal_params)
mythen_data_converter.setFlatFieldData(mythen_flat_field)
mythen_data_converter.setBeamlineOffset(0.08208)

fastshutter1=finder.find("fastshutter")
# task that opens the fast shutter
mythen_open_shutter_task = gda.device.detector.mythen.tasks.OpenShutterTask()
mythen_open_shutter_task.setShutterScannable(fastshutter1)

# task that closes the fast shutter
mythen_close_shutter_task = gda.device.detector.mythen.tasks.CloseShutterTask()
mythen_close_shutter_task.setShutterScannable(fastshutter1)

#added safty object for detectors
macsafeposition=finder.find("macsafeposition")
psdsafeposition=finder.find("psdsafeposition")
# task that checks MAC detector position to avoid collision
mythen_check_collision_task=gda.hrpd.pmac.CheckCollisionTask()
mythen_check_collision_task.setCheckedScannable(tth) #@UndefinedVariable
mythen_check_collision_task.setSafePosition(macsafeposition) #@UndefinedVariable

# task that plots the last data point into a panel
mythen_plot_last_data_task = gda.device.detector.mythen.tasks.PlotLastPointTask()
mythen_plot_last_data_task.setPanelName("Mythen")

delta1=finder.find("delta")
def normal_mythen():
    mythen = gda.device.detector.mythen.MythenDetectorImpl()
    mythen.configure()
    mythen.setName("mythen")
    mythen.setDetectorID("mcs02")
    mythen.setMythenClient(mythen_client)
    mythen.setDataConverter(mythen_data_converter)
    mythen.setDeltaScannable(delta1)
    mythen.setAtScanStartTasks([mythen_open_shutter_task, mythen_check_collision_task])
    mythen.setAtPointEndTasks([mythen_plot_last_data_task])
    mythen.setAtScanEndTasks([mythen_close_shutter_task])
    mythen.setHasChannelInfo(False)
    return mythen

def summing_mythen():
    mythen = gda.device.detector.mythen.SummingMythenDetector()
    mythen.configure()
    mythen.setName("smythen")
    mythen.setDetectorID("mcs02")
    mythen.setMythenClient(mythen_client)
    mythen.setDataConverter(mythen_data_converter)
    mythen.setDeltaScannable(delta1)
    mythen.setNumberOfModules(18)
    mythen.setAtScanStartTasks([mythen_open_shutter_task, mythen_check_collision_task])
    mythen.setAtPointEndTasks([mythen_plot_last_data_task])
    mythen.setAtScanEndTasks([mythen_close_shutter_task])
    mythen.step = 0.004
    mythen.setHasChannelInfo(False)
    return mythen

def shutter_mythen():
    mythen = gda.device.detector.mythen.ShutterControlledMythenDetectorImpl()
    mythen.configure()
    mythen.setName("shmythen")
    mythen.setDetectorID("mcs02")
    mythen.setMythenClient(mythen_client)
    mythen.setDataConverter(mythen_data_converter)
    mythen.setDeltaScannable(delta1)
    mythen.setAtScanStartTasks([mythen_open_shutter_task, mythen_check_collision_task])
    mythen.setAtPointEndTasks([mythen_plot_last_data_task])
    mythen.setAtScanEndTasks([mythen_close_shutter_task])
    mythen.setHasChannelInfo(False)
    return mythen

mythen = normal_mythen()
smythen = summing_mythen()
shmythen = shutter_mythen()

from gda.device.scannable import DummyScannable
ds = DummyScannable("ds")

def psd(t,n=1.0):
    scan(ds, 1.0, n, 1.0, mythen, t, Io, t, Ie)  # @UndefinedVariable
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

print
print "-----------------------------------------------------------------------------------------------------------------"
print "method to change MYTHEN flat field file dynamically, temporarily. "
print "    >>>setMythenFlatFieldFile('flatfield_filename')"
print "This must be called each time you reset_namespce or restart GDA servers"
def setMythenFlatFieldFile(filename):
    mythen_flat_field = gda.device.detector.mythen.data.MythenRawDataset(java.io.File(filename))
    mythen_data_converter.setFlatFieldData(mythen_flat_field)
    mythen.setDataConverter(mythen_data_converter)

print
print "---------------------------------------------------------numFrames--------------------------------------------------------"
print "Create rocking theta scannable 'rocktheta'"
print "    To change the rocking limits, use 'rocktheta.setLowerLimit(10)', 'rocktheta.setUpperLimit(10)'; "
print "    To view the rocking limits, use 'rocktheta.getLowerLimit()', 'rockthets.getUpperLimit()'."
from rockingMotion_class import RockingMotion
theta1=finder.find("theta")
rocktheta=RockingMotion("rocktheta", theta1, -10, 10)
print "Create 'psdrt' command for PSD data collection with theta rocking"
def psdrt(t, n=1.0):
    scan(ds, 1.0, n, 1.0, mythen, t, rocktheta, Io, t, Ie)  # @UndefinedVariable
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
print "create 'tfg2' object to provide control of Time Frame Generator device"
from peloop.tfg2 import TFG2
tfg2=TFG2("tfg2")

print "create 'pedata' object to capture the PE data from ADC2 device"
from peloop.pedatacapturer import DataCapturer
pedata=DataCapturer("pedata")
print "create 'pel' object for PE Loop experiment"
from tfg_peloop import PELoop
pel=PELoop("pel", tfg2, fg2, adc2, pedata, mythen)
daserver=finder.find("daserver")

print "-----------------------------------------------------------------------------------------------------------------"
print "create derivative scannable 'deriv' object to provide derivative value of enegry to elt1"
from scan_detetor_with_derivative import DeviceDerivativeClass
deriv = DeviceDerivativeClass("deriv", "energy", "etl1", "derivative");

##### new objects must be added above this line ###############
print
print "=================================================================================================================";
print "Initialisation script complete." 
print
###Must leave what after this line last.
bm1=finder.find("bm")
if bm1.isBeamOn():
    print "PHOTON BEAM IS ON SAMPLE NOW."
else:
    print "NO PHOTON BEAM ON SAMPLE."
# setup I11 specific scans
#### The XPS CVScan commands and objects - replaced by PMAC CVScan object
#print "---------------------------------------------------------------------------------------------"
#print "create I11 specific XPS scan commands: cvscan, robotscan, robotscan2d, stagescan, tempscan"
#from gda.hrpd.commands.ScanCommands import cvscan, robotscan, robotscan2d, stagescan, tempscan #@UnusedImport
# create command alias

#vararg_alias("robotscan") 
#vararg_alias("robotscan2d") 
#vararg_alias("stagescan") 
#vararg_alias("tempscan") 
#print
#print "---------------------------------------------------------------------------------------------"
#print "create MAC data processing object 'rebin' to control MAC data rebin and plotting"
#print "To enable rebinning and plotting during data collection, use >>>rebin.enable()"
#print "To disable rebinning and plotting during data collection, use >>>rebin.disable()"
#print "The default is enabled"
#from gda.hrpd.data import MacDataProcessing
#rebin=MacDataProcessing.getInstance()
#print
#print "---------------------------------------------------------------------------------------------"
#print "create Scan File Holder object 'sfh' for scan data file load."
#from gda.analysis import ScanFileHolder
#sfh=ScanFileHolder()
#print "To load in a MAC data file, use >>>sfh.loadMAC('absolute/path/to/file')"
#print "To plot these data in MAC panel, use >>>Plotter.plot('MAC', sfh.getAxis(0), sfh.getAxis(1))"
#print
