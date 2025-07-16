import os #@UnusedImport
import sys #@UnusedImport
import gdascripts #@UnusedImport
from gda.factory import Finder #@UnusedImport @UnresolvedImport
from gda.data import NumTracker #@UnusedImport @UnresolvedImport
from gda.jython import InterfaceProvider #@UnusedImport @UnresolvedImport
from gda.jython.commands import GeneralCommands #@UnusedImport @UnresolvedImport
from gda.jython.commands.GeneralCommands import vararg_alias, alias #@UnusedImport @UnresolvedImport
from gda.configuration.properties import LocalProperties #@UnusedImport @UnresolvedImport
from gda.util import PropertyUtils #@UnusedImport @UnresolvedImport
from gda.device.scannable import PVScannable, DummyScannable #@UnusedImport @UnresolvedImport
from gdascripts import installation

print("="*100);
print "Performing beamline specific initialisation code for i09-2.";
print("="*100)

from i09shared.localstation import * #@UnusedWildImport

print "Custom i09-2 initialisation code.";

###############################################################################
###               Configure scan data processing and scan commands          ###
###############################################################################
print("-"*100)
from gdascripts.scan.installStandardScansWithProcessing import * #@UnusedWildImport
scan_processor.rootNamespaceDict=globals()
print("")

from gdascripts.scan.installMultiRegionalScanWithProcessing import mrscan # @UnusedImport

from i09shared.scan.miscan import miscan  # @UnusedImport

print("-"*100)
print("Installing pathscan command:")
from gdascripts.scan.pathscanCommand import pathscan # @UnusedImport
print(pathscan.__doc__) #@UndefinedVariable

###############################################################################
###                         Import useful scannables                        ###
###############################################################################
print("-"*100)
# Import and setup function to create mathematical scannables
from i09shared.functions import functionClassFor2Scannables
functionClassFor2Scannables.ROOT_NAMESPACE_DICT=globals()
from i09shared.functions.functionClassFor2Scannables import ScannableFunctionClassFor2Scannables #@UnusedImport
print("Importing utility mathematical scannable class ScannableFunctionClassFor2Scannables " + functionClassFor2Scannables.ScannableFunctionClassFor2Scannables.__doc__) #@UndefinedVariable

###############################################################################
###                   Configure scannable output formats                        ###
###############################################################################
globals()['sm3pitch'].setOutputFormat(["%10.1f"])
###############################################################################
###                         Create epics devices                            ###
###############################################################################
if installation.isLive():
	# Create temporary devices for femtos this should be moved to Spring
	sd9iamp9 = DisplayEpicsPVClass("sd9iamp9", "BL09K-MO-SD-09:IAMP9:I", "V", "%f")
	sd9iamp36 = DisplayEpicsPVClass("sd9iamp36", "BL09K-MO-SD-09:IAMP36:I", "V", "%f")
	sd11iamp7 = DisplayEpicsPVClass("sd11iamp7", "BL09K-MO-SD-11:IAMP7:I", "V", "%f")

###############################################################################
###                         Create JID related devices                      ###
###############################################################################
from i09_2_shared.scannable.energy_polarisation_order_gap_instances import LH, LV, CR, CL, LH3, jenergy_s, polarisation,jenergypolarisation,jenergy_order, jgap_offset #@UnusedImport
from i09_2_shared.scannable.continuous.jenergy_scannable_instances import jenergy, jenergy_move_controller, jI0, sdc # @UnusedImport
from i09shared.scan.cvscan import cvscan #@UnusedImport

###############################################################################
###                   Get channel voltage control scannables                ###
###############################################################################
from uk.ac.diamond.daq.configuration import ConfigUtils #@UnresolvedImport

if installation.isLive():
	from detector.iseg_instances import dldv, mcp_b, kenergy, int_spec, DLD_start, DLD_stop  # @UnusedImport
	from detector.iseg_channel_scannable_instances import *  # @UnusedWildImport
	from pseudodevices.bindingEnergyScannable import benergy,Benergy  # @UnusedImport

	########################################################################################
	###                   Create scannable/commands to reset average filter              ###
	########################################################################################
	try:
		if ConfigUtils.profileActive("V2"):
			clearAccum = EpicsReadWritePVClass("clearAccum","BL09K-EA-DET-01:SUM1:ResetFilter","","%f")
			print "V2 profile loaded, 'clearAccum' scannable created"
		if ConfigUtils.profileActive("V1"):
			clearAccum = EpicsReadWritePVClass("clearAccum","BL09K-EA-D-01:cam1:ZeroCube","","%f")
			print "V1 profile loaded, 'clearAccum' scannable created"
	except:
		print "No profile loaded, 'clearAccum' scannable is not created - going further"

	def clear_summed_data():
		if ConfigUtils.profileActive("V2"):
			#print("Clear accumulated data")
			caput("BL09K-EA-DET-01:SUM1:ResetFilter", 1)
		if ConfigUtils.profileActive("V1"):
			# commenting this out as caget to this PV crashes further scan in GDA
			caput("BL09K-EA-D-01:cam1:ZeroCube", 1)

	def clear_summed_data_separate():
		if ConfigUtils.profileActive("V2"):
			print("Clear accumulated data")
			caput("BL09K-EA-DET-01:SUM1:ResetFilter", 1)
		if ConfigUtils.profileActive("V1"):
			print("Clear accumulated data")
			caput("BL09K-EA-D-01:cam1:ZeroCube", 1)
else:
	focus = DummyScannable("focus")
	kenergy = DummyScannable("kenergy")
	clearAccum = DummyScannable("clearAccum")
	def clear_summed_data():
		print "clear_summed_data called - dummy mode, skipping command"
	def clear_summed_data_separate():
		clear_summed_data()
	def MM_on():
		print "MM turned ON"
	def MM_off():
		print "MM turned OFF"
	alias("MM_on")
	alias("MM_off")

###############################################################################
###                   Get sample manipulator scannables                     ###
###############################################################################
from pseudodevices.sampleManipulator import sx1, sx2, sx3, sy, sz1, sz2 #@UnusedImport
from gdaserver import sxc, szc # @UnresolvedImport
sx1.configure()
sx2.configure()
sx3.configure()
sy.configure()
sz1.configure()
sz2.configure()

###############################################################################
###                   Creat time scannable                                  ###
###############################################################################
from gdascripts.scannable.timerelated import TimeSinceScanStart
print("-"*100)
print("Creating time scannable timeStart")
timeStart = TimeSinceScanStart('timeStart')
print("")

###############################################################################
###                   Get check beam/control scannable                      ###
###############################################################################
from pseudodevices.checkbeamscannables import checkbeam, checkrc, checkfe, checktopup_time  # @UnusedImport
from i09shared.pseudodevices.pauseDetectorWhileMonitorBelowThreshold import WaitForScannableStateAndHandleShutter
print("-"*100)
print("Creating 'checkjid' scannable to be used to pause or resume detector acquisition based on ID control")
from gdaserver import fsk1, psk1 #@UnresolvedImport
from gdaserver import  jidaccesscontrol #@UnresolvedImport
checkjid = WaitForScannableStateAndHandleShutter('checkjid', [fsk1, psk1], jidaccesscontrol, secondsBetweenChecks=1, secondsToWaitAfterBeamBackUp=5.0, readyStates=['ENABLED'])
print("")

###############################################################################
###                       Setup metashop commands                           ###
###############################################################################
print("-"*100)
from gdascripts.metadata.nexus_metadata_class import meta #@UnusedImport
print("setup meta-data provider object \"meta\".")
print("")

###############################################################################
###                   Save SamplePosition scannable                         ###
###############################################################################
from gdascripts.scannable.sample_positions import SamplePositions
print("-"*100)
sp = SamplePositions("sp", [sx1, sx2, sx3, sy, sz1, sz2, sxc])
print("Creating sample positioner object sp. Store sample manipulator position components in a dictionary, save them to a file and move sample manipulator to previously saved positions in the dictionary.")
help(sp)

from pseudodevices.delayedGetPositionScannable import delayedGetPositionScannable # @UnusedImport

#Connect the JythonScannableWrappers for client live controls
from gdaserver import polarisation_wrapper,sy_wrapper # @UnresolvedImport
polarisation_wrapper.connectScannable()
sy_wrapper.connectScannable()

print("="*100)
print("localStation.py Initialisation script complete.")
print("="*100)