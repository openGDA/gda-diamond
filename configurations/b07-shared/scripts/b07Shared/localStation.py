# localStation.py
# For beamline specific initialisation code.
#
from gda.configuration.properties import LocalProperties #@UnusedImport
from gda.device.scannable import DummyScannable #@UnusedImport
from gdascripts import installation #@UnusedImport

print(""*100);
print("="*100);
print "Performing general initialisation code for b07-shared";
print("")


print("-"*100)
print "load EPICS Pseudo Device utilities for creating scannable object from a PV name."
from gdascripts.pd.epics_pds import * #@UnusedWildImport
from gdascripts.pd.dummy_pds import * #@UnusedWildImport
print("")

print("-"*100)
print "load time utilities for creating timer objects."
from gdascripts.pd.time_pds import * #@UnusedWildImport
from gdascripts.scannable.timerelated import TimeSinceScanStart, clock, epoch  # @UnusedImport
print("-"*100)
print("creating timeScannable")
timeScannable = TimeSinceScanStart('timeScannable')
print("")

print("-"*100)
print "load utilities: caget(pv), caput(pv,value), attributes(object), "
from gdascripts.utils import * #@UnusedWildImport
print("")

print("-"*100)
from gdascripts.scan.installMultiRegionalScanWithProcessing import mrscan # @UnusedImport
print("")

#check beam scannables
from scannables.checkbeamscannables import checkbeam, checkfe, checkrc, checktopup_time  # @UnusedImport

print("-"*100)
# Add a string to hold extra detectors it will be appended to analyser scans run from the GUI
# See uk.ac.diamond.daq.devices.specs.phoibos.ui.handlers.RunSequenceHandler
extraDetectors = ""

print("-"*100)
print("To create a PVScannable from a PV:")
print("   >>> my_scannable = PVScannable('my_scannable', 'PV_name')")
print("   >>> my_scannable.configure()")
from gda.device.scannable import PVScannable  # @UnusedImport


###############################################################################
###                            Core utilities and constants                 ###
###############################################################################

print("-"*100)
print("Load drange:")
from b07Shared.utils.dRangeUtil import drange #@UnusedImport
print("    Decimal version of range():   drange(start,end,step) to provide exact number of decimal places as step value inputed")
print("")

print("-"*100)
print "load common physical constants"
from gdascripts.constants import * #@UnusedWildImport
print("")

#beam metadata scannables
from gdascripts.scannable.beam.beamDivergence import BeamDivergence
beam_divergence_at_sample = BeamDivergence("beam_divergence_at_sample", horizontal = 3.3, vertical = 4.9)
from gdascripts.scannable.beam.beamFlux import BeamFlux
beam_flux_at_sample = BeamFlux("beam_flux_at_sample", flux = 0.0)
from gdascripts.scannable.beam.beamExtent import BeamExtent
beam_size_at_sample =  BeamExtent("beam_size_at_sample", horizontal_size = 6.0, vertical_size = 10.0)

from gdascripts.scannable.virtual_scannable import VirtualScannable
comment = VirtualScannable("comment", initial_value="Not set", value_format="%s")
sample_name = VirtualScannable("sample_name", initial_value="Not set", value_format="%s")

ds = DummyScannable("ds")

print("-"*100)
print "Finished general initialisation code for b07-shared.";
print("")