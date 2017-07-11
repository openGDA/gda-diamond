import java, sys
import installation
import gdascripts.scan.concurrentScanWrapper

from gdascripts.messages.handle_messages import simpleLog, log
from gdascripts.scannable.dummy import SingleInputDummy
from gdascripts.scan.installStandardScansWithProcessing import * #@UnusedWildImport
from gda.device.scannable.scannablegroup import ScannableGroup

from gdascripts.degas.degas import Degas

from gda.data import PathConstructor, NumTracker
from gda.jython.commands.GeneralCommands import alias, run
from gda.jython.commands.GeneralCommands import pause as enable_pause_or_interrupt
from gda.jython.commands.ScannableCommands import scan
from gda.factory import Finder
from time import sleep  # @UnusedImport

import os
from calibration.Energy_class import BeamEnergy
from gda.jython.commands import GeneralCommands

simpleLog("================ INITIALISING I21 GDA ================")

#global run
 
print "-----------------------------------------------------------------------------------------------------------------"
print "Set scan returns to the original positions on completion to false (0); default is 0."
print "   To set scan returns to its start positions on completion please do:"
print "      >>>scansReturnToOriginalPositions=1"
scansReturnToOriginalPositions=0;
print

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
i21NumTracker = NumTracker("scanbase_numtracker");
finder=Finder.getInstance()

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
    filenumber = i21NumTracker.getCurrentFileNumber();
    return os.path.join(cwd,str(filenumber))
    
alias("lwf")

# function to find the next working file path
def nwf():
    '''query the next working file path root'''
    cwd = PathConstructor.createFromDefaultProperty()
    filenumber = i21NumTracker.getCurrentFileNumber();
    return os.path.join(cwd,str(filenumber+1))
    
alias("nwf")

# function to find the next scan number
def nfn():
    '''query the next file number or scan number'''
    filenumber = i21NumTracker.getCurrentFileNumber();
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

def interruptable():
    GeneralCommands.pause()
    
alias("interruptable")
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

from gdascripts.scan.installStandardScansWithProcessing import * # @UnusedWildImport
scan_processor.rootNamespaceDict=globals()
gdascripts.scan.concurrentScanWrapper.ROOT_NAMESPACE_DICT = globals()
scan_processor_normal_processes = scan_processor.processors
scan_processor_empty_processes  = []

def scan_processing_on():
    scan_processor.processors = scan_processor_normal_processes

def scan_processing_off():
    scan_processor.processors = scan_processor_empty_processes

print " To manually switch on scan processor, run 'scan_processing_on()' function on Jython Terminal."
print " To manually switch off scan processor, run 'scan_processing_off()' function on Jython Terminal."
scan_processing_on()

print "Adding dummy devices x,y and z"
dummies = ScannableGroup()
dummies.setName("dummies")
dummies.setGroupMembers([SingleInputDummy("x"), SingleInputDummy("y"), SingleInputDummy("z")])

print "Adding timer devices t, dt, and w, clock"
from gdascripts.scannable.timerelated import timerelated #@UnusedImport

print 


print "create clever amplifier scannables: cleverd7femto1, cleverd7femto2, cleverm4femto1, cleverm4femto2"
from i21_utils import DisplayEpicsPVClass_neg, DisplayEpicsPVClass_pos
d7femto1_neg = DisplayEpicsPVClass_neg('d7femto1_neg', d7femto1)  # @UndefinedVariable
d7femto2_pos = DisplayEpicsPVClass_pos('d7femto2_pos', d7femto2)  # @UndefinedVariable

from scannabledevices.cleverAmplifier import CleverAmplifier
cleverd7femto1=CleverAmplifier("cleverd7femto1", d7femto1_neg, 0.5, 9.0, "%.4f", "%.4e")  # @UndefinedVariable
cleverd7femto2=CleverAmplifier("cleverd7femto2", d7femto2_pos, 0.5, 9.0, "%.4f", "%.4e")  # @UndefinedVariable
cleverm4femto1=CleverAmplifier("cleverm4femto1", m4femto1, 0.5, 9.0, "%.4f", "%.4e")  # @UndefinedVariable
cleverm4femto2=CleverAmplifier("cleverm4femto2", m4femto2, 0.5, 9.0, "%.4f", "%.4e")  # @UndefinedVariable
print


print
print "-----------------------------------------------------------------------------------------------------------------"
print "Create an 'dummyenergy' scannable which can be used for test energy scan in GDA. It moves dummy motor 'dummies.x' and 'dummies.y'"
dummyenergy=BeamEnergy("dummyenergy",idscannable, dummies.x, dummies.y)  # @UndefinedVariable
print "Create an 'energy' scannable which can be used for energy scan in GDA. It moves both ID gap and PGM energy"
energy=BeamEnergy("energy",idscannable, idgap, pgmEnergy)  # @UndefinedVariable

print "-----------------------------------------------------------------------------------------------------------------"
print "setup meta-data provider commands: meta_add, meta_ll, meta_ls, meta_rm "
from metashop import *  # @UnusedWildImport
import metashop  # @UnusedImport

print "-----------------------------------------------------------------------------------------------------------------"
print "Add meta data items"
metadatalist=[idgap] #@UndefinedVariable
m1list=[m1x,m1pitch,m1height,m1yaw,m1roll] #@UndefinedVariable
m2list=[m2x,m2pitch,m2height]# @UndefinedVariable
m4list=[m4x,m4y,m4z,m4rx,m4ry,m4rz,m4longy,m4femto1,m4femto2]  # @UndefinedVariable
m5list=[m5hqx,m5hqy,m5hqz,m5hqrx,m5hqry,m5hqrz,m5lqx,m5lqy,m5lqz,m5lqrx,m5lqry,m5lqrz,m5longy,m5tth]  # @UndefinedVariable
pgmlist=[pgmEnergy, pgmGratingSelectReal,pgmMirrorSelectReal,pgmMirrorPitch,pgmGratingPitch]  # @UndefinedVariable
s1list=[s1hsize,s1vsize,s1hcentre,s1vcentre] #@UndefinedVariable
s2list=[s2hsize,s2vsize,s2hcentre,s2vcentre] #@UndefinedVariable
s3list=[s3hsize,s3vsize,s3hcentre,s3vcentre] #@UndefinedVariable
s5list=[s5v1gap,s5v2gap,s5hgap] #@UndefinedVariable
samplelist=[sapolar,sax,say,saz,saazimuth,satilt,diodetth,draincurrent] # @UndefinedVariable
sgmlist=[sgmGratingSelect,sgmr1,sgmh,sgmpitch,sgmwedgeoffside,sgmwedgenearside] # @UndefinedVariable
spectrometerlist=[specgamma,spech,specl] # @UndefinedVariable
andorlist=[andorAccumulatePeriod,andorShutterMode,andorExtShutterTrigger,andorPreampGain,andorADCSpeed,andorVerticalShiftSpeed,andorVerticalShiftAmplitude,andorEMCCDGain,andorCoolerTemperature,andorCoolerControl,andorBinningSizeX,andorBinningSizeY,andorEffectiveHorizontal,andorEffectiveVertical]  # @UndefinedVariable

meta_data_list= metadatalist+m1list+m2list+m4list+m5list+pgmlist+s1list+s2list+s3list+s5list+samplelist+sgmlist+spectrometerlist+andorlist
# metadatalist=[s1, m1, s2, m2, s3, pgm, s5, m4, idgap, smp]  # @UndefinedVariable
for each in meta_data_list:
    meta_add(each)
alias("meta_add")
alias("meta_ll")
alias("meta_ls")
alias("meta_rm")

b2.setOutputFormat(["%7.4f"])  # @UndefinedVariable

#DiffCalc
from startup import i21 as dc  # @UnusedWildImport

#Mapping scan
from mapping_scan_commands import *

from scannabledevices.xrayBeamMonitor import XRayBeamMonitor
xbm=XRayBeamMonitor("xbm", xraywatchdog="XRayWatchdog")

if installation.isLive():
    print "Running in live mode"
    print "create camera total count scannables: d1camtotal, d2camtotal, d3acamtotal, d4camtotal, smpcam1total,smpcam2total,smpcam3total, smpcam4total"
    d1camtotal=DisplayEpicsPVClass('d1camtotal', 'BL21I-DI-DCAM-01:STAT:Total_RBV', 'counts', '%10d')
    d2camtotal=DisplayEpicsPVClass('d2camtotal', 'BL21I-DI-DCAM-02:STAT:Total_RBV', 'counts', '%10d')
    d3acamtotal=DisplayEpicsPVClass('d3acamtotal', 'BL21I-DI-DCAM-03:STAT:Total_RBV', 'counts', '%10d')
    d4camtotal=DisplayEpicsPVClass('d4camtotal', 'BL21I-DI-DCAM-04:STAT:Total_RBV', 'counts', '%10d')
    d8camtotal=DisplayEpicsPVClass('d8camtotal', 'BL21I-DI-DCAM-24:STAT:Total_RBV', 'counts', '%10d')
    smpcam1total=DisplayEpicsPVClass('smpcam1total', 'BL21I-DI-DCAM-20:STAT1:Total_RBV', 'counts', '%10d')
    smpcam2total=DisplayEpicsPVClass('smpcam2total', 'BL21I-DI-DCAM-21:STAT1:Total_RBV', 'counts', '%10d')
    smpcam3total=DisplayEpicsPVClass('smpcam3total', 'BL21I-DI-DCAM-22:STAT1:Total_RBV', 'counts', '%10d')
    smpcam4total=DisplayEpicsPVClass('smpcam4total', 'BL21I-DI-DCAM-23:STAT1:Total_RBV', 'counts', '%10d')

    from epics_scripts.pv_scannable_utils import createPVScannable
    pgmMirrorPitch_UserOffset = createPVScannable('pgmMirrorPitch_UserOffset', 'BL21I-OP-PGM-01:MIR:PITCH.OFF')
    pgmGratingPitch_UserOffset = createPVScannable('pgmGratingPitch_UserOffset', 'BL21I-OP-PGM-01:GRT:PITCH.OFF')
else:
    print "Running in dummy mode"
#     try:
#         if (isinstance(alpha, ScannableMotionBase)):  # @UndefinedVariable
#             del alpha  # @UndefinedVariable
#         if (isinstance(beta, ScannableMotionBase)):  # @UndefinedVariable
#             del beta  # @UndefinedVariable
#         if (isinstance(psi, ScannableMotionBase)):  # @UndefinedVariable
#             del psi  # @UndefinedVariable
#         if (isinstance(chi_con, diffcalc.gdasupport.scannable.parameter.DiffractionCalculatorParameter)):  # @UndefinedVariable
#             del chi_con  # @UndefinedVariable
#         if (isinstance(eta_con, diffcalc.gdasupport.scannable.parameter.DiffractionCalculatorParameter)):  # @UndefinedVariable
#             del eta_con  # @UndefinedVariable
#         if (isinstance(phi_con, diffcalc.gdasupport.scannable.parameter.DiffractionCalculatorParameter)):  # @UndefinedVariable
#             del phi_con  # @UndefinedVariable
#     except:
#         print "Cannot delete diffcalc constraint parameters"
#         
print "*"*80
print "Attempting to run localStationUser.py from users script directory"

run("localStationUser")
print "localStationUser.py completed."

simpleLog("===================== GDA ONLINE =====================")
