import os #@UnusedImport
import sys #@UnusedImport
import gdascripts #@UnusedImport
from gdascripts import installation as installation #@UnusedImport
from gda.factory import Finder
from gda.data import NumTracker
from gda.jython import InterfaceProvider
from gda.jython.commands import GeneralCommands
from gda.jython.commands.GeneralCommands import vararg_alias, alias
from gda.configuration.properties import LocalProperties
from gda.device.scannable import PVScannable

print("="*100);
print "Performing beamline specific initialisation code for p60.";
print("="*100)

from i09shared.localstation import * #@UnusedWildImport

print("Custom p60 initialisation code.");

###############################################################################
###               Configure scan data processing and scan commands          ###
###############################################################################
print("-"*100)
from gdascripts.scan.installStandardScansWithProcessing import * #@UnusedWildImport
scan_processor.rootNamespaceDict=globals()
print("")

###############################################################################
###                   Additional scan commands                              ###
###############################################################################
# the following requires new NexusScanDataWriter to work!
# from scan.MultiRegionScan import mrscan, ALWAYS_COLLECT_AT_STOP_POINT, NUMBER_OF_DECIMAL_PLACES  # @UnusedImport
from i09shared.scan.miscan import miscan  # @UnusedImport
print("")

from i09shared.scan.analyserScan import analyserscan, extraDetectors # @UnusedImport

###############################################################################
###                   Additional scannables                                 ###
###############################################################################

#check beam scannables
#ToDo - Needs to be modified
#from pseudodevices.checkbeamscannables import checkbeam, checkrc, checkfe, checktopup_time, checkbeamdetector, detectorpausecontrol, checkdetector  # @UnusedImport

print("-"*100)
# Import and setup function to create mathematical scannables
from i09shared.functions import functionClassFor2Scannables
functionClassFor2Scannables.ROOT_NAMESPACE_DICT=globals()
from i09shared.functions.functionClassFor2Scannables import ScannableFunctionClassFor2Scannables #@UnusedImport
print("Importing utility mathmatical scannable class ScannableFunctionClassFor2Scannables " + functionClassFor2Scannables.ScannableFunctionClassFor2Scannables.__doc__) #@UndefinedVariable

###############################################################################
###                  Metadata object/commands                               ###
###############################################################################

#from i09shared.scan.cvscan import cvscan  # @UnusedImport

print("-"*100)
print("Setup meta object, an instance of Metadata. Can add additional metadata to scans:")
from gdascripts.metadata.nexus_metadata_class import meta # @UnusedImport
help(meta)

print("="*100)
print "Initialisation script complete."
print("="*100)
###Must leave what after this line last.
