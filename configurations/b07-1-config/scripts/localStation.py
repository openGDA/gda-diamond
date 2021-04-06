# localStation.py
# For beamline specific initialisation code.
#
import java
from gda.configuration.properties import LocalProperties

print "=================================================================================================================";
print "Performing beamline specific initialisation code (b07-1).";
print "=================================================================================================================";
print

print "Load EPICS pseudo device utilities for creating scannable object from a PV name."
from gdascripts.pd.epics_pds import * #@UnusedWildImport

print "Load time utilities."
from gdascripts.pd.time_pds import * #@UnusedWildImport
# Make time scannable 
# Example: scan timeScannable 0 3600 30 analyser - Make a scan starting now, for 1 hour, recording the analyser every 30 secs
from gdascripts.scannable.timerelated import TimeSinceScanStart
timeScannable = TimeSinceScanStart('timeScannable')

print "Load utilities: caget(pv), caput(pv,value), attributes(object), iterableprint(iterable), listprint(list), frange(start,end,step)"
from gdascripts.utils import * #@UnusedWildImport

print "Installing standard scans with processing"
from gdascripts.scan.installStandardScansWithProcessing import * #@UnusedWildImport
scan_processor.rootNamespaceDict=globals()

print "Installing regional scan"
from gdascripts.scan.RegionalScan import RegionalScanClass
mrscan = RegionalScanClass()
alias('mrscan')

print "Installing configure_analyser_fixed_transmission"
from beamline.configure_analyser_fixed_transmission import configure_analyser_fixed_transmission

print "Installing EPICS archiver client"
from gdascripts.archiver.archiver import archive
alias('archive')
from gdaserver import archiver  # @UnresolvedImport

from scannables.rga21 import rga21, rga21AR, rga21CF3, rga21CH2, rga21CH3, rga21CH4, rga21CO, rga21CO2, rga21H2, rga21H2O, rga21HE, rga21O2, rga21sumofpeaks, rga21tot  # @UnusedImport
from scannables.rga24 import rga24, rga24AR, rga24CF3, rga24CH2, rga24CH3, rga24CH4, rga24CO, rga24CO2, rga24H2, rga24H2O, rga24HE, rga24O2, rga24sumofpeaks, rga24tot  # @UnusedImport
# Add a string to hold extra detectors it will be appended to analyser scans run from the GUI
# See uk.ac.diamond.daq.devices.specs.phoibos.ui.handlers.RunSequenceHandler
extraDetectors = ""

print("-"*100)
from gda.device.scannable import PVScannable
print "To create a PVScannable from a PV:"
print "   >>> my_scannable = PVScannable('my_scannable', 'PV_name')"
print "   >>> my_scannable.configure()"

print "-----------------------------------------------------------------------------------------------------------------"
