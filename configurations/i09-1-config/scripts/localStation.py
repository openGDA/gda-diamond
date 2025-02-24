# localStation.py
# For beamline specific initialisation code.
#
import java #@UnresolvedImport @UnusedImport
import os #@UnusedImport
import sys #@UnusedImport
import gdascripts #@UnusedImport
from gdascripts import installation as installation #@UnusedImport
from gda.factory import Finder # @UnusedImport @UnresolvedImport
from gda.data import NumTracker # @UnusedImport @UnresolvedImport
from gda.jython import InterfaceProvider # @UnusedImport @UnresolvedImport
from gda.jython.commands import GeneralCommands # @UnusedImport @UnresolvedImport
from gda.jython.commands.GeneralCommands import vararg_alias, alias # @UnusedImport @UnresolvedImport
from gda.configuration.properties import LocalProperties # @UnusedImport @UnresolvedImport
from gda.util import PropertyUtils # @UnusedImport @UnresolvedImport
from gda.device.scannable import PVScannable #@UnusedImport @UnresolvedImport

print("="*100);
print "Performing beamline specific initialisation code for i09-1.";
print("="*100)

from i09shared.localstation import * #@UnusedWildImport

print "Custom i09-1 initialisation code.";

###############################################################################
###               Configure scan data processing and scan commands          ###
###############################################################################
print("-"*100)
from gdascripts.scan.installStandardScansWithProcessing import * #@UnusedWildImport
scan_processor.rootNamespaceDict=globals()
print("")

from gdascripts.scan.installMultiRegionalScanWithProcessing import mrscan # @UnusedImport

print("-"*100)
print("Installing pathscan command:")
from gdascripts.scan.pathscanCommand import pathscan # @UnusedImport
print(pathscan.__doc__) #@UndefinedVariable

print("-"*100)
print("Installing 'analyserscan' command for the electron analyser.")
from gdaserver import analyser #@UnresolvedImport
from i09shared.scan.analyserScan import analyserscan, extraDetectors # @UnusedImport
analyserscan.__doc__ = analyserscan.__doc__.replace("detector", analyser.getName()) #@UndefinedVariable
print(analyserscan.__doc__) #@UndefinedVariable

print("-"*100)
print("Installing analyserpathscan:")
from i09shared.scan.analyserpathscan import analyserpathscan #@UnusedImport
analyserpathscan.__doc__ = analyserpathscan.__doc__.replace("detector", analyser.getName()) #@UndefinedVariable
print(analyserpathscan.__doc__) #@UndefinedVariable

###############################################################################
###                         Import useful scannable                         ###
###############################################################################
print("-"*100)
# Import and setup function to create mathematical scannables
from i09shared.functions import functionClassFor2Scannables
functionClassFor2Scannables.ROOT_NAMESPACE_DICT=globals()
from i09shared.functions.functionClassFor2Scannables import ScannableFunctionClassFor2Scannables #@UnusedImport
print("Importing utility mathmatical scannable class ScannableFunctionClassFor2Scannables " + functionClassFor2Scannables.ScannableFunctionClassFor2Scannables.__doc__) #@UndefinedVariable

###############################################################################
###                         Import IID functionality                        ###
###############################################################################
from i09_1_shared.scannable.ienergy_order_gap_instances import ienergy_order, ienergy_s, igap_offset # @UnusedImport
from i09_1_shared.scannable.continuous.ienergy_scannable_instances import ienergy, ienergy_move_controller, iI0  # @UnusedImport

from gdaserver import psi1, iidaccesscontrol #@UnresolvedImport
from i09shared.pseudodevices.pauseDetectorWhileMonitorBelowThreshold import WaitForScannableStateAndHandleShutter
print "Creating 'checkiid' scannable to be used to pause or resume detector acquisition based on ID control"
checkiid = WaitForScannableStateAndHandleShutter('checkiid', [psi1], iidaccesscontrol, secondsBetweenChecks=1, secondsToWaitAfterBeamBackUp=5.0, readyStates=['ENABLED'])

from i09shared.scan.cvscan import cvscan  # @UnusedImport

###############################################################################
###                   Save SamplePosition scannable                         ###
###############################################################################
from gdaserver import smpmx, smpmy, smpmz, smpmpolar #@UnresolvedImport
from i09shared.scannable.SamplePositions import SamplePositions # @UnusedImport
print("-"*100)
sp = SamplePositions("sp", [smpmx, smpmy, smpmz, smpmpolar])
print("Creating sample positioner object sp. Store sample manipulator position components in a dictionary, save them to a file and move sample manipulator to previously saved positions in the dictionary.")
print(sp.__doc__.replace("\n", "", 1))

print("="*100)
print("localStation.py Initialisation script complete.")
print("="*100)
