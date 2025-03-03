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
from i09shared.scan.miscan import miscan  # @UnusedImport

from gdascripts.scan.installMultiRegionalScanWithProcessing import mrscan # @UnusedImport

print("-"*100)
print("Installing pathscan command:")
from gdascripts.scan.pathscanCommand import pathscan # @UnusedImport
print(pathscan.__doc__) #@UndefinedVariable

print("-"*100)
print("Installing 'analyserscan' command for the electron analyser.")
from gdaserver import r4000 #@UnresolvedImport
from i09shared.scan.analyserScan import analyserscan, extraDetectors # @UnusedImport
analyserscan.__doc__ = analyserscan.__doc__.replace("detector", r4000.getName()) #@UndefinedVariable
print(analyserscan.__doc__) #@UndefinedVariable

print("-"*100)
print("Installing analyserpathscan:")
from i09shared.scan.analyserpathscan import analyserpathscan #@UnusedImport
analyserpathscan.__doc__ = analyserpathscan.__doc__.replace("detector", r4000.getName()) #@UndefinedVariable
print(analyserpathscan.__doc__) #@UndefinedVariable

###############################################################################
###                   Additional scannables                                 ###
###############################################################################
print("-"*100)
# Import and setup function to create mathematical scannables
from i09shared.functions import functionClassFor2Scannables
functionClassFor2Scannables.ROOT_NAMESPACE_DICT=globals()
from i09shared.functions.functionClassFor2Scannables import ScannableFunctionClassFor2Scannables #@UnusedImport
print("Importing utility mathmatical scannable class ScannableFunctionClassFor2Scannables " + functionClassFor2Scannables.ScannableFunctionClassFor2Scannables.__doc__) #@UndefinedVariable

###############################################################################
###                  Metadata object/commands                               ###
###############################################################################
from gdaserver import al_kalpha_energy #@UnresolvedImport
AL_KALPHA_METADATA_SCANNABLES = [al_kalpha_energy]
AL_KALPHA_METADATA_DEVICE_NAMES = ["beam_al_kalpha"]

from gdaserver import mg_kalpha_energy #@UnresolvedImport
MG_KALPHA_METADATA_SCANNABLES = [mg_kalpha_energy]
MG_KALPHA_METADATA_DEVICE_NAMES = ["beam_mg_kalpha"]

#Defaults must be set to prevent any warning message
from org.eclipse.scanning.device import CommonBeamlineDevicesConfiguration #@UnresolvedImport
CommonBeamlineDevicesConfiguration.getInstance().setBeamName(AL_KALPHA_METADATA_DEVICE_NAMES[0])

from i09shared.metadata.dynamic_metadata import DynamicScanMetadata
dynamic_meta = DynamicScanMetadata(
    sequence_detector = r4000,
    metadata_dict = {
        "Aluminium K-Alpha" : [AL_KALPHA_METADATA_SCANNABLES, AL_KALPHA_METADATA_DEVICE_NAMES],
        "Magnesium K-Alpha" : [MG_KALPHA_METADATA_SCANNABLES, MG_KALPHA_METADATA_DEVICE_NAMES],
    },
)
scan.scanListeners = scan.scanListeners + [dynamic_meta]
mrscan.scanListeners = mrscan.scanListeners + [dynamic_meta]

print("-"*100)
print("Setup meta object, an instance of Metadata. Can add additional metadata to scans:")
from gdascripts.metadata.nexus_metadata_class import meta # @UnusedImport
help(meta)

print("="*100)
print "Initialisation script complete."
print("="*100)
###Must leave what after this line last.
