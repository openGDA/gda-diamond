# localStation.py
# For beamline specific initialisation code.
#
import java #@UnresolvedImport @UnusedImport
import os #@UnusedImport
import sys #@UnusedImport
import gdascripts #@UnusedImport
from gdascripts import installation as installation #@UnusedImport
from gda.factory import Finder # @UnusedImport
from gda.data import NumTracker # @UnusedImport
from gda.jython import InterfaceProvider # @UnusedImport
from gda.jython.commands import GeneralCommands # @UnusedImport
from gda.jython.commands.GeneralCommands import vararg_alias, alias # @UnusedImport
from gda.configuration.properties import LocalProperties # @UnusedImport
from gda.util import PropertyUtils # @UnusedImport
from gda.device.scannable import PVScannable #@UnusedImport

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

from i09shared.scan.analyserScan import analyserscan, extraDetectors #@UnusedImport

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
from calibration.hard_energy_class import ienergy #@UnusedImport
from i09shared.pseudodevices.checkid import checkiid #@UnusedImport

###############################################################################
###                   Save SamplePosition scannable                         ###
###############################################################################
from i09shared.scannable.SamplePositions import sp, SamplePositions # @UnusedImport

print("="*100)
print("localStation.py Initialisation script complete.")
print("="*100)
