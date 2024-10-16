import os
import sys
import gdascripts
from gda.factory import Finder
from gda.data import NumTracker
from gda.jython import InterfaceProvider
from gda.jython.commands import GeneralCommands
from gda.jython.commands.GeneralCommands import vararg_alias, alias
from gda.jython.commands.ScannableCommands import scan
from gdascripts.pd.time_pds import showtimeClass, showincrementaltimeClass, \
    waittimeClass, waittimeClass2, actualTimeClass
from gda.configuration.properties import LocalProperties
from gdascripts.analysis.datasetprocessor.oned.scan_stitching import Lcen, Rcen
from i09shared.analysis.ScanDataAnalysis import FindScanCentroid, FindScanPeak
from gdascripts.analysis.datasetprocessor.oned.extractPeakParameters import ExtractPeakParameters
from gda.util import PropertyUtils
from gda.device.scannable import PVScannable
import gdascripts
import i09shared.installation as installation

print "=================================================================================================================";
print "Performing beamline specific initialisation code (i09).";
print "=================================================================================================================";

print "-----------------------------------------------------------------------------------------------------------------"
print "Set if scan returns to the original positions on completion."
print "    scansReturnToOriginalPositions=0, not return to its start position (the default);"
print "    scansReturnToOriginalPositions=1, return to its start position;"
scansReturnToOriginalPositions = 0;
print

from java.lang import System  # @UnresolvedImport

###############################################################################
###                            Generic Functions                            ###
###############################################################################
from i09shared.utils.directory_operation_commands import pwd, lwf, nwf, nfn, cfn, setSubdirectory, getSubdirectory #@UnusedImport

# ## Create time Scannables
print "Creating time scannables"
from i09shared.timerelated import clock, t, dt, w  # @UnusedImport
showtime = showtimeClass('Showtime')
inctime = showincrementaltimeClass('inctime')
waittime = waittimeClass2('Waittime')
atime = actualTimeClass('atime')

print "-----------------------------------------------------------------------------------------------------------------"
print "create 'beam' object for get/set photon beam properties such as wavelength, energy"
beam = Finder.find("beam")
print "create 'beamline' object for access beamline parameters such as data directory"
beamline = Finder.find("beamline")

print
print "-----------------------------------------------------------------------------------------------------------------"
print "load EPICS Pseudo Device utilities for creating scannable object from a PV name."
from gdascripts.pd.epics_pds import *  # @UnusedWildImport
print
print "-----------------------------------------------------------------------------------------------------------------"
print "load time utilities for creating timer objects."
from gdascripts.pd.time_pds import *  # @UnusedWildImport
print
print "-----------------------------------------------------------------------------------------------------------------"
print "Load utilities: caget(pv), caput(pv,value), attributes(object), "
print "    iterableprint(iterable), listprint(list), frange(start,end,step)"
from gdascripts.utils import *  # @UnusedWildImport
print
print "-----------------------------------------------------------------------------------------------------------------"
print "load common physical constants"
from gdascripts.constants import *  # @UnusedWildImport
print

print "-----------------------------------------------------------------------------------------------------------------"
print "function to set wavelength >>>setwavelength(value)"


def setlambda(wavelength):
    wavelength = float(wavelength)
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


print("Importing analysis commands (findpeak, findcentroid & enable scan data processes)")
findpeak = FindScanPeak
findcentroid = FindScanCentroid

# Install standard scan processing
from gdascripts.scan.installStandardScansWithProcessing import *  # @UnusedWildImport
scan_processor.rootNamespaceDict = globals()

###############################################################################
###                   Configure scannable output formats                        ###
###############################################################################
globals()['sm3pitch'].setOutputFormat(["%10.1f"])

print("-----------------------------------------------------------------------------------------------------------------")
from i09shared.functions import functionClassFor2Scannables
functionClassFor2Scannables.ROOT_NAMESPACE_DICT = globals()

if installation.isLive():
    # Create temporary devices for femtos this should be moved to Spring
    sd9iamp9 = DisplayEpicsPVClass("sd9iamp9", "BL09K-MO-SD-09:IAMP9:I", "V", "%f")
    sd9iamp36 = DisplayEpicsPVClass("sd9iamp36", "BL09K-MO-SD-09:IAMP36:I", "V", "%f")
    sd11iamp7 = DisplayEpicsPVClass("sd11iamp7", "BL09K-MO-SD-11:IAMP7:I", "V", "%f")

# Add a string to hold extra detectors it will be appended to analyser scans run from the GUI
# See uk.ac.diamond.daq.devices.specs.phoibos.ui.handlers.RunSequenceHandler
extraDetectors = ""

print("-----------------------------------------------------------------------------------------------------------------")

from pseudodevices.IDGap_Offset import jgap_offset

print "Create an 'jenergy', 'polarisation' and 'jenergypolarisation' scannables."
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

if installation.isLive():
    from detector.iseg_instances import dldv, mcp_b, kenergy, int_spec, DLD_start, DLD_stop  # @UnusedImport
    from detector.iseg_channel_scannable_instances import *  # @UnusedImport
    from pseudodevices.sampleManipulator import sx1, sx2, sx3, sy, sz1, sz2, sxc  # @UnresolvedImport
    from pseudodevices.bindingEnergyScannable import benergy,Benergy  # @UnusedImport

from i09shared.scan.miscan import miscan, clear_summed_data  # @UnusedImport

# Install regional scan
print("Installing regional scan")
from gdascripts.scan.RegionalScan import RegionalScanClass
mrscan = RegionalScanClass()
alias('mrscan')

# check beam scannables
from pseudodevices.checkbeamscannables import checkbeam, checkrc, checkfe, checktopup_time  # @UnusedImport
from i09shared.pseudodevices.checkid import checkjid # @UnusedImport

print("-"*100)
print("setup meta-data provider commands: meta_add, meta_ll, meta_ls, meta_rm ")
from metadata.metashop import meta_add, meta_ll, meta_ls, meta_rm  # @UnusedImport
meta_data_list = [jgap, topup_time, rc, beamenergy, topupstate, sm6iamp27, sm6, sm3, ss2, ss7, pgm, pgmenergy, microscope, es3x]  # @UndefinedVariable
meta_data_list += [sx1, sx2, sx3, sy, sz1, sz2]  # @UndefinedVariable
meta_data_list += [jenergy_s, polarisation]  # @UndefinedVariable
meta_data_list += [analyser_slit]  # @UndefinedVariable
for each in meta_data_list:
    meta_add(each)

from i09shared.scannable.SamplePositions import sp, SamplePositions #@UnusedImport

print("=================================================================================================================")
print("localStation.py Initialisation script complete.")

