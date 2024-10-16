# file:        localStation.py
# Description: For beamline specific initialisation.
# @author: Fajin Yuan
# updated 19/06/2012
import os
import sys
import gdascripts
import i09shared.installation as installation
from gda.factory import Finder
from gda.data import NumTracker
from gda.jython import InterfaceProvider
from gda.jython.commands import GeneralCommands
from calibration.hard_energy_class import HardEnergy
from i09shared.calibration.soft_energy_class import SoftEnergy
from gda.jython.commands.GeneralCommands import vararg_alias, alias
from gda.jython.commands.ScannableCommands import scan
from gdascripts.pd.time_pds import showtimeClass, showincrementaltimeClass,waittimeClass, waittimeClass2, actualTimeClass
from gda.configuration.properties import LocalProperties
from gdascripts.analysis.datasetprocessor.oned.scan_stitching import Lcen, Rcen
from i09shared.analysis.ScanDataAnalysis import FindScanCentroid, FindScanPeak
from gdascripts.analysis.datasetprocessor.oned.extractPeakParameters import ExtractPeakParameters
from gda.util import PropertyUtils
from org.opengda.detector.electronanalyser.utils import FilenameUtil
from gdaserver import sd1_cam, sd3_cam  # @UnresolvedImport
from gda.device.scannable import PVScannable

from gdascripts.metadata.nexus_metadata_class import meta # @UnusedImport

print "=================================================================================================================";
print "Performing beamline specific initialisation code (i09).";
print "=================================================================================================================";


print "-----------------------------------------------------------------------------------------------------------------"
print "Set if scan returns to the original positions on completion."
print "    scansReturnToOriginalPositions=0, not return to its start position (the default);"
print "    scansReturnToOriginalPositions=1, return to its start position;"
scansReturnToOriginalPositions=0;
print

###############################################################################
###                            Generic Functions                            ###
###############################################################################
from i09shared.utils.directory_operation_commands import pwd, lwf, nwf, nfn, cfn, setSubdirectory, getSubdirectory #@UnusedImport

### Create time Scannables
print "Creating time scannables"
from i09shared.timerelated import clock, t, dt, w #@UnusedImport
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

from i09shared.pseudodevices.CameraExposureChanger import CameraExposureChanger

print "\nCreating camera exposure object ('sd1_camera_exposure')for SD1 camera"
sd1_camera_exposure = CameraExposureChanger(sd1_cam)

if installation.isLive():
	print "\nCreating camera exposure object ('sd3_camera_exposure')for SD3 camera"
	sd3_camera_exposure = PVScannable("sd3_camera_exposure", "BL09J-MO-SD-03:CAM:AcquireTime")
	sd3_camera_exposure.configure()

	print "\nCreating camera exposure object ('xbpm_camera_exposure')for XBPM camera"
	xbpm_camera_exposure = PVScannable("xbpm_camera_exposure", "BL09I-EA-XBPM-01:CAM:AcquireTime")
	xbpm_camera_exposure.configure()
else:
	print "\nCreating camera exposure object ('sd3_camera_exposure')for SD3 camera"
	sd3_camera_exposure = CameraExposureChanger(sd3_cam)


###############################################################################
###                   Configure scannable output formats                        ###
###############################################################################
globals()['sm3pitch'].setOutputFormat(["%10.1f"])

###############################################################################
#     Import i/j energy, harmonic order. gap and polarisation instances       #
###############################################################################
from scannable.energy_poloarisation_order_gap_instances import LH,LV,CR,CL,LH3,jenergy_s,polarisation,jenergypolarisation,ienergy_order,jenergy_order, ienergy_s  # @UnusedImport
from pseudodevices.IDGap_Offset import igap_offset, jgap_offset  # @UnusedImport

###############################################################################
#                      Import analyserscan commands                           #
###############################################################################
print "Create an 'analyserscan' command for scanning the electron analyser."
from command.analyserScan import analyserscan, zerosupplies, analyserscancheck, analyserscan_v1  # @UnusedImport
alias("zerosupplies")
alias("analyserscan")
alias("analyserscan_v1")
alias("analyserscancheck")
print "Create shutter objects 'psi2' for hard X-ray, 'psj2' for soft X-ray."

# Import and setup function to create mathmatical scannables
from i09shared.functions import functionClassFor2Scannables
functionClassFor2Scannables.ROOT_NAMESPACE_DICT=globals()

# I09-70 Create a empty string to hold detectors to be used with the GUI
extraDetectors = ""

# Install regional scan
print "Installing regional scan 'mrscan'"
from gdascripts.scan.RegionalScan import RegionalScanClass
mrscan = RegionalScanClass()
alias('mrscan')

#check beam scannables
from pseudodevices.checkbeamscannables import checkbeam, checkrc, checkfe, checktopup_time, checkbeamdetector, detectorpausecontrol, checkdetector  # @UnusedImport
from i09shared.pseudodevices.checkid import checkjid, checkiid # @UnusedImport
#create 'move' command
run("/dls_sw/i09/software/gda/config/scripts/command/checkedMotion.py")  # @UndefinedVariable

from scannable.continuous.continuous_energy_scannables import ienergy,jenergy, ienergy_move_controller, jenergy_move_controller, jI0, iI0, sdc  # @UnusedImport
from i09shared.scan.cvscan import cvscan  # @UnusedImport

print("-"*100)
print("setup meta-data provider commands: meta_add, meta_ll, meta_ls, meta_rm ")
from metashop import meta_add,meta_ll,meta_ls, meta_rm  # @UnusedImport
import metashop  # @UnusedImport
print("Can now add meta data items to be captured in data files.")
imetadata=[igap,dcm,hm1x,hm1y,hm1pitch,hm1yaw,hm2x,hm2y,hm2pitch,hm3x,hm3y,hm3pitch,hm3mainbender,hm3elipticalbender,cccx,cccy] #@UndefinedVariable
jmetadata=[jgap,polarisation,pgm,sm1fpitch,sm3fpitch,sm4x,sm4y,sm4pitch,sm5pitch,sm5bender1,sm5bender2,ss2ycentre,ss2ygap,ss4] #@UndefinedVariable
esmetadata=[hm3iamp20,sm5iamp8,hm3iamp20,sm5iamp8,smpmiamp39,smpm,lakeshore] #@UndefinedVariable
meta_data_list = imetadata + jmetadata + esmetadata
for each in meta_data_list:
	meta_add(each)

print("-"*100)
print("keithley2600 control objects:\nGeneral operation: keithley_a, keithley_b\nAverage mode: keithley_a_average_mode, keithley_b_average_mode\nSweep mode: keithley_a_sweep_mode, keithley_b_sweep_mode")

# the following requires new NexusScanDataWriter to work!
# from scan.MultiRegionScan import mrscan, ALWAYS_COLLECT_AT_STOP_POINT, NUMBER_OF_DECIMAL_PLACES  # @UnusedImport
from i09shared.scan.miscan import miscan  # @UnusedImport

from gdaserver import nixswr_repeat, nixswr_time # @UnresolvedImport @UnusedImport
print("-"*100)
print("Installed object nixswr_repeat, measure with nixswr camera that takes input the number of frames to acquire.")
print("\tSynatx: scan scannable 1 2 1 nixswr_repeat 10")
print("Installed object nixswr_time, measure with nixswr camera that takes input the amount of time to acquire over (in seconds).")
print("\tSynatx: scan scannable 1 2 1 nixswr_time 0.001")

from i09shared.scannable.SamplePositions import sp, SamplePositions # @UnusedImport

print "="*100;
print "Initialisation script complete."
print
###Must leave what after this line last.
