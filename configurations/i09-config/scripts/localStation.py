# file:        localStation.py
# Description: For beamline specific initialisation.
# @author: Fajin Yuan
# updated 19/06/2012
import os #@UnusedImport
import sys #@UnusedImport
import gdascripts #@UnusedImport
import java
from gdascripts import installation as installation
from gda.factory import Finder
from gda.data import NumTracker
from gda.jython import InterfaceProvider
from gda.jython.commands import GeneralCommands
from gda.jython.commands.GeneralCommands import vararg_alias, alias
from gda.configuration.properties import LocalProperties
from gda.util import PropertyUtils
from gdaserver import sd1_cam, sd3_cam  # @UnresolvedImport
from gda.device.scannable import PVScannable

print("="*100)
print("Performing beamline specific initialisation code (i09).")
print("="*100)

from i09shared.localstation import * #@UnusedWildImport

print "Custom i09 initialisation code.";

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
from gdascripts.scan.installMultiRegionalScanWithProcessing import mrscan # @UnusedImport

from i09shared.scan.analyserScan import analyserscan, extraDetectors # @UnusedImport
from command.analyserscancheck import zerosupplies, analyserscancheck # @UnusedImport

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
#     Import i/j energy, harmonic order. gap and polarisation instances       #
###############################################################################
from scannable.energy_poloarisation_order_gap_instances import LH,LV,CR,CL,LH3,jenergy_s,polarisation,jenergypolarisation,ienergy_order,jenergy_order, ienergy_s  # @UnusedImport
from pseudodevices.IDGap_Offset import igap_offset, jgap_offset  # @UnusedImport
from scannable.continuous.continuous_energy_scannables import ienergy, jenergy, ienergy_move_controller, jenergy_move_controller, jI0, iI0, sdc  # @UnusedImport
from i09shared.scan.cvscan import cvscan  # @UnusedImport

###############################################################################
###                        Metadata saved for each scan                     ###
###############################################################################
#ToDo - This should be changed to importing meta and this defined in springbeans
print("-"*100)
print("Setup meta-data provider commands: meta_add, meta_ll, meta_ls, meta_rm ")
from metashop import meta_add,meta_ll,meta_ls, meta_rm  # @UnusedImport
import metashop  # @UnusedImport
print("Can now add meta data items to be captured in data files.")
imetadata=[igap,dcm,hm1x,hm1y,hm1pitch,hm1yaw,hm2x,hm2y,hm2pitch,hm3x,hm3y,hm3pitch,hm3mainbender,hm3elipticalbender,cccx,cccy] #@UndefinedVariable
jmetadata=[jgap,polarisation,pgm,sm1fpitch,sm3fpitch,sm4x,sm4y,sm4pitch,sm5pitch,sm5bender1,sm5bender2,ss2ycentre,ss2ygap,ss4] #@UndefinedVariable
esmetadata=[hm3iamp20,sm5iamp8,hm3iamp20,sm5iamp8,smpmiamp39,smpm,lakeshore] #@UndefinedVariable
meta_data_list = imetadata + jmetadata + esmetadata
for each in meta_data_list:
	meta_add(each)
print("")

###############################################################################
###                       Check condition scannables                        ###
###############################################################################
from pseudodevices.checkbeamscannables import checkbeam, checkrc, checkfe, checktopup_time, checkbeamdetector, detectorpausecontrol, checkdetector  # @UnusedImport
from i09shared.pseudodevices.checkid import checkjid, checkiid # @UnusedImport

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

###############################################################################
###                   Save SamplePosition scannable                         ###
###############################################################################
from i09shared.scannable.SamplePositions import sp, SamplePositions # @UnusedImport

print("="*100)
print("localStation.py Initialisation script complete.")
print("="*100)
###Must leave what after this line last.
