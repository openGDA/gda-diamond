# file:        localStation.py
# Description: For beamline specific initialisation.
# @author: Fajin Yuan
# updated 19/06/2012
import os #@UnusedImport
import sys #@UnusedImport
import gdascripts #@UnusedImport
import java #@UnresolvedImport
from gdascripts import installation as installation
from gda.factory import Finder #@UnresolvedImport @UnusedImport
from gda.data import NumTracker #@UnresolvedImport @UnusedImport
from gda.jython import InterfaceProvider #@UnresolvedImport @UnusedImport
from gda.jython.commands import GeneralCommands #@UnresolvedImport @UnusedImport
from gda.jython.commands.GeneralCommands import vararg_alias, alias #@UnresolvedImport @UnusedImport
from gda.configuration.properties import LocalProperties #@UnresolvedImport @UnusedImport
from gda.util import PropertyUtils #@UnresolvedImport @UnusedImport
from gdaserver import sd1_cam, sd3_cam  # @UnresolvedImport
from gda.device.scannable import PVScannable #@UnresolvedImport

print("="*100)
print("Performing beamline specific initialisation code (i09).")
print("="*100)

from i09shared.localstation import * #@UnusedWildImport

print "Custom i09 initialisation code.";

###############################################################################
#     Import i/j energy, harmonic order. gap and polarisation instances       #
###############################################################################
from i09_1_shared.scannable.ienergy_order_gap_instances import ienergy_order, ienergy_s, igap_offset # @UnusedImport
from i09_1_shared.scannable.continuous.ienergy_scannable_instances import ienergy, ienergy_move_controller, iI0  # @UnusedImport

from i09_2_shared.scannable.energy_polarisation_order_gap_instances import LH, LV, CR, CL, LH3, jenergy_s, polarisation,jenergypolarisation,jenergy_order, jgap_offset #@UnusedImport
from i09_2_shared.scannable.continuous.jenergy_scannable_instances import jenergy, jenergy_move_controller, jI0, sdc  # @UnusedImport

#Connect the JythonScannableWrappers for client live controls
from gdaserver import ienergy_order_wrapper, jenergy_order_wrapper, igap_offset_wrapper, jgap_offset_wrapper, polarisation_wrapper # @UnresolvedImport
ienergy_order_wrapper.connectScannable()
jenergy_order_wrapper.connectScannable()
igap_offset_wrapper.connectScannable()
jgap_offset_wrapper.connectScannable()
polarisation_wrapper.connectScannable()

###############################################################################
###               Configure scan data processing and scan commands          ###
###############################################################################
print("-"*100)
from gdascripts.scan.installStandardScansWithProcessing import * #@UnusedWildImport
scan_processor.rootNamespaceDict=globals()
print("")

###############################################################################
###                    Import additional scan commands                      ###
###############################################################################
from i09shared.scan.cvscan import cvscan  # @UnusedImport

from gdascripts.scan.installMultiRegionalScanWithProcessing import mrscan # @UnusedImport

print("-"*100)
print("Installing pathscan command:")
from gdascripts.scan.pathscanCommand import pathscan # @UnusedImport
print(pathscan.__doc__) #@UndefinedVariable

print("-"*100)
print("Installing 'analyserscan' command for the electron analyser.")
from gdaserver import ew4000 #@UnresolvedImport
from i09shared.scan.analyserScan import analyserscan, extraDetectors # @UnusedImport
analyserscan.__doc__ = analyserscan.__doc__.replace("detector", ew4000.getName()) #@UndefinedVariable
print(analyserscan.__doc__) #@UndefinedVariable

print("-"*100)
ZERO_SUPPLIES_PV = "BL09I-EA-DET-01:CAM:ZERO_SUPPLIES"
print("Installing 'zerosupplies' command which uses pv: " + ZERO_SUPPLIES_PV)

def zerosupplies():
	caput(ZERO_SUPPLIES_PV, 1)

alias("zerosupplies")
print("")

print("-"*100)
print("Installing analyserpathscan:")
from i09shared.scan.analyserpathscan import analyserpathscan #@UnusedImport
analyserpathscan.__doc__ = analyserpathscan.__doc__.replace("detector", ew4000.getName()) #@UndefinedVariable
print(analyserpathscan.__doc__) #@UndefinedVariable

# the following requires new NexusScanDataWriter to work!
# from scan.MultiRegionScan import mrscan, ALWAYS_COLLECT_AT_STOP_POINT, NUMBER_OF_DECIMAL_PLACES  # @UnusedImport
from i09shared.scan.miscan import miscan  # @UnusedImport

###############################################################################
###                         Import useful scannables                        ###
###############################################################################
print("-"*100)
# Import and setup function to create mathematical scannables
from i09shared.functions import functionClassFor2Scannables
functionClassFor2Scannables.ROOT_NAMESPACE_DICT=globals()
from i09shared.functions.functionClassFor2Scannables import ScannableFunctionClassFor2Scannables #@UnusedImport
print("Importing utility mathmatical scannable class ScannableFunctionClassFor2Scannables " + functionClassFor2Scannables.ScannableFunctionClassFor2Scannables.__doc__) #@UndefinedVariable

###############################################################################
###                          Configure camera bases                         ###
###############################################################################
from i09shared.pseudodevices.CameraExposureChanger import CameraExposureChanger
print("-"*100)
print("Creating camera exposure object ('sd1_camera_exposure')for SD1 camera")
sd1_camera_exposure = CameraExposureChanger(sd1_cam)

if installation.isLive():
	print("Creating camera exposure object ('sd3_camera_exposure')for SD3 camera")
	sd3_camera_exposure = PVScannable("sd3_camera_exposure", "BL09J-MO-SD-03:CAM:AcquireTime")
	sd3_camera_exposure.configure()

	print("Creating camera exposure object ('xbpm_camera_exposure')for XBPM camera")
	xbpm_camera_exposure = PVScannable("xbpm_camera_exposure", "BL09I-EA-XBPM-01:CAM:AcquireTime")
	xbpm_camera_exposure.configure()
else:
	print("Creating camera exposure object ('sd3_camera_exposure')for SD3 camera")
	sd3_camera_exposure = CameraExposureChanger(sd3_cam)
print("")

###############################################################################
###                       Check condition scannables                        ###
###############################################################################
from pseudodevices.checkbeamscannables import checkbeam, checkrc, checkfe, checktopup_time, checkbeamdetector, detectorpausecontrol, checkdetector  # @UnusedImport

from gdaserver import fsi1, fsj1 #@UnresolvedImport
from i09shared.pseudodevices.pauseDetectorWhileMonitorBelowThreshold import WaitForScannableStateAndHandleShutter
print("-"*100)
print("Creating 'checkjid' scannable to be used to pause or resume detector acquisition based on ID control")
from gdaserver import  jidaccesscontrol #@UnresolvedImport
checkjid = WaitForScannableStateAndHandleShutter('checkjid', [fsi1, fsj1], jidaccesscontrol, secondsBetweenChecks=1, secondsToWaitAfterBeamBackUp=5.0, readyStates=['ENABLED'])
from gdaserver import  iidaccesscontrol #@UnresolvedImport
print "Creating 'checkiid' scannable to be used to pause or resume detector acquisition based on ID control"
checkiid = WaitForScannableStateAndHandleShutter('checkiid', [fsi1, fsj1], iidaccesscontrol, secondsBetweenChecks=1, secondsToWaitAfterBeamBackUp=5.0, readyStates=['ENABLED'])
print("")

###############################################################################
###                        Metadata saved for each scan                     ###
###############################################################################
#Build I-branch metadata list. These objects involved in scan will add I-branch metadata devices to monitor per scan
from gdaserver import iid, dcm, hm1, hm2, hm3, ccc, dcmenergyEv #@UnresolvedImport
I_METADATA_SCANNABLES = [iid, dcm, hm1, hm2, hm3, ccc, dcmenergyEv, ienergy_order, ienergy_s, igap_offset, ienergy, ienergy_move_controller, iI0, checkiid]
I_METADATA_DEVICE_NAMES = ["iid", "dcm", "beam_dcm", "hm1", "hm2", "hm3", "ccc", "ienergy", "ienergy_order", "igap_offset"]

#Build J-branch metadata list. These objects involved in scan will add J-branch metadata devices to monitor per scan
from gdaserver import jid, pgm, sm1, sm3, sm4, sm5, ss2, ss4 #@UnresolvedImport
J_METADATA_SCANNABLES = [jid, pgm, sm1, sm3, sm4, sm5, ss2, ss4, jenergy_s, polarisation, jenergypolarisation, jenergy_order, jgap_offset, jenergy, jenergy_move_controller, jI0, sdc, checkjid]
J_METADATA_DEVICE_NAMES = ["jid", "pgm", "beam_pgm", "sm1", "sm3", "sm4", "sm5", "ss2", "ss4", "jenergy", "polarisation", "jenergy_order", "jgap_offset"]

#Defaults must be set to prevent any warning message
from org.eclipse.scanning.device import CommonBeamlineDevicesConfiguration #@UnresolvedImport
CommonBeamlineDevicesConfiguration.getInstance().setInsertionDeviceName(I_METADATA_DEVICE_NAMES[0])
CommonBeamlineDevicesConfiguration.getInstance().setMonochromatorName(I_METADATA_DEVICE_NAMES[1])
CommonBeamlineDevicesConfiguration.getInstance().setBeamName(I_METADATA_DEVICE_NAMES[2])

from i09shared.metadata.dynamic_metadata import DynamicScanMetadata
dynamic_meta = DynamicScanMetadata(
	sequence_detector = ew4000,
	metadata_dict = {
		"I-branch" : [I_METADATA_SCANNABLES, I_METADATA_DEVICE_NAMES],
		"J-branch" : [J_METADATA_SCANNABLES, J_METADATA_DEVICE_NAMES],
	},
)

scan.scanListeners = scan.scanListeners + [dynamic_meta]
mrscan.scanListeners = mrscan.scanListeners + [dynamic_meta]

print("-"*100)
print("I and J branch metadata is now added dynamically to scan")
print("")

from gdascripts.metadata.nexus_metadata_class import meta #@UnusedImport

###############################################################################
###                           Create move command                           ###
###############################################################################
from command.checkedMotion import move, moveWithinLimits, IENERGY_MOVE_LIMIT, JENERGY_MOVE_LIMIT # @UnusedImport

###############################################################################
###            Add help text for gdaserver keithley2600 object              ###
###############################################################################
print("-"*100)
print("keithley2600 control objects:")
print("General operation: keithley_a, keithley_b")
print("Average mode: keithley_a_average_mode, keithley_b_average_mode")
print("Sweep mode: keithley_a_sweep_mode, keithley_b_sweep_mode")
print("")

###############################################################################
###                      Reflectivity camera help text                      ###
###############################################################################
from gdaserver import nixswr_repeat, nixswr_time # @UnresolvedImport @UnusedImport
print("-"*100)
print("Installed detector nixswr_repeat, measure with nixswr camera that takes input the number of frames to acquire. Cannot be used with pos command.")
print("\tSynatx: scan scannable 1 2 1 nixswr_repeat 10")
print("Installed detector nixswr_time, measure with nixswr camera that takes input the amount of time to acquire over (in seconds). Cannot be used with pos command.")
print("\tSynatx: scan scannable 1 2 1 nixswr_time 0.001")

NIXSWR_TOTAL_PV = java.net.InetAddress.getLocalHost().getHostName().split(".")[0] + "-AD-SIM-01:STAT:Total_RBV"
if installation.isLive():
	NIXSWR_TOTAL_PV = "BL09I-MO-ES-03:STAT:Total_RBV"
print("Adding nixswr scannable of class DisplayEpicsPVClass, single exposure which gets pv: " + NIXSWR_TOTAL_PV)
nixswr = DisplayEpicsPVClass("nixswr", NIXSWR_TOTAL_PV, "", "%d")
print("")

print("-"*100)
print("Can load sequence files into dataclass to control sequence files for scripts:")
print("\tsequence = load_sequence(filename)")
print("Example:")
print("\tsequence = load_sequence(filename)")
print("\tsequence.enable('region_name1')")
print("\tsequence.disable('region_name2')")
print("\tanalyserscan ew4000 sequence")
def load_sequence(filename):
	from org.opengda.detector.electronanalyser.api import SESSequenceHelper #@UnresolvedImport
	return SESSequenceHelper.loadSequence(filename)

###############################################################################
###                   Save SamplePosition scannable                         ###
###############################################################################
from gdascripts.scannable.sample_positions import SamplePositions
from gdaserver import smpmx, smpmy, smpmz, smpmpolar #@UnresolvedImport
print("-"*100)
sp = SamplePositions("sp", [smpmx, smpmy, smpmz, smpmpolar])
print("Creating sample positioner object sp. Store sample manipulator position components in a dictionary, save them to a file and move sample manipulator to previously saved positions in the dictionary.")
help(sp)

print("="*100)
print("localStation.py Initialisation script complete.")
print("="*100)
###Must leave what after this line last.
