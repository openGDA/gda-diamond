import os
import sys
import gdascripts
from gda.factory import Finder
from gda.data import NumTracker
from gda.jython import InterfaceProvider
from gda.jython.commands import GeneralCommands
from gda.jython.commands.GeneralCommands import vararg_alias, alias
from gda.configuration.properties import LocalProperties
from gda.util import PropertyUtils
from gda.device.scannable import PVScannable, DummyScannable
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
print("-"*100)
if installation.isLive():
	# Create temporary devices for femtos this should be moved to Spring
	sd9iamp9 = DisplayEpicsPVClass("sd9iamp9", "BL09K-MO-SD-09:IAMP9:I", "V", "%f")
	sd9iamp36 = DisplayEpicsPVClass("sd9iamp36", "BL09K-MO-SD-09:IAMP36:I", "V", "%f")
	sd11iamp7 = DisplayEpicsPVClass("sd11iamp7", "BL09K-MO-SD-11:IAMP7:I", "V", "%f")

###############################################################################
###                         Create JID related devices                      ###
###############################################################################
print("-"*100)
from pseudodevices.IDGap_Offset import jgap_offset #@UnusedImport
print("Create an 'jenergy', 'polarisation' and 'jenergypolarisation' scannables.")
print("")
LH,LV,CR,CL=["LH","LV","CR","CL"]
from calibration.energy_polarisation_class import BeamEnergyPolarisationClass
jenergy_s = BeamEnergyPolarisationClass("jenergy_s", jidscannable, pgmenergy, lut="JIDEnergy2GapCalibrations.txt", polarisationConstant=True)  # @UndefinedVariable
jenergy_s.configure()
polarisation = BeamEnergyPolarisationClass("polarisation", jidscannable, pgmenergy, lut="JIDEnergy2GapCalibrations.txt", energyConstant=True)  # @UndefinedVariable
polarisation.configure()
jenergypolarisation = BeamEnergyPolarisationClass("jenergypolarisation", jidscannable, pgmenergy, lut="JIDEnergy2GapCalibrations.txt")  # @UndefinedVariable
jenergypolarisation.configure()
jenergypolarisation.setInputNames(["jenergy_s"])
jenergypolarisation.setExtraNames(["polarisation"])

from scannable.continuous.continuous_energy_scannables import jenergy, jenergy_move_controller, jI0, sdc  # @UnusedImport
from i09shared.scan.cvscan import cvscan  # @UnusedImport

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
	clearAccum = DummyScannable("clearAccum")
	def clear_summed_data():
		print "clear_summed_data called - dummy mode, skipping command"
	def clear_summed_data_separate():
		clear_summed_data()
###############################################################################
###                   Get sample manipulator scannables                     ###
###############################################################################
from pseudodevices.sampleManipulator import sx1, sx2, sx3, sy, sz1, sz2, sxc #@UnusedImport

###############################################################################
###                   Get check beam/control scannable                      ###
###############################################################################
from pseudodevices.checkbeamscannables import checkbeam, checkrc, checkfe, checktopup_time  # @UnusedImport
from i09shared.pseudodevices.checkid import checkjid # @UnusedImport

###############################################################################
###                       Setup metashop commands                           ###
###############################################################################
#ToDo - Should be updated to new meta and done in spring
print("-"*100)
print("setup meta-data provider commands: meta_add, meta_ll, meta_ls, meta_rm ")
from metadata.metashop import meta_add, meta_ll, meta_ls, meta_rm  # @UnusedImport
meta_data_list = [jgap, topup_time, rc, beamenergy, topupstate, sm6iamp27, sm6, sm3, ss2, ss7, pgm, pgmenergy, microscope, es3x]  # @UndefinedVariable
meta_data_list += [sx1, sx2, sx3, sy, sz1, sz2]  # @UndefinedVariable
meta_data_list += [jenergy_s, polarisation]  # @UndefinedVariable
meta_data_list += [analyser_slit]  # @UndefinedVariable
for each in meta_data_list:
		meta_add(each)
print("")

###############################################################################
###                   Save SamplePosition scannable                         ###
###############################################################################
from i09shared.scannable.SamplePositions import sp, SamplePositions # @UnusedImport

print("="*100)
print("localStation.py Initialisation script complete.")
print("="*100)

