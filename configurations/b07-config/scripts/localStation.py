# localStation.py
# For beamline specific initialisation code.
#
import java
from gda.configuration.properties import LocalProperties
from gda.device.scannable import DummyScannable

print "=================================================================================================================";
print "Performing beamline specific initialisation code (b07).";
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

# Add a string to hold extra detectors it will be appended to analyser scans run from the GUI
# See uk.ac.diamond.daq.devices.specs.phoibos.ui.handlers.RunSequenceHandler
extraDetectors = ""

from scannables.detector_output_processing import BekhoffAdcOutputProcessing
#dummy_quotient = BekhoffAdcOutputProcessing('dummy_quotient', ds1, ds2, 'divide_detector_output')
ca35b_ca18b_quotient = BekhoffAdcOutputProcessing('ca35b_ca18b_quotient', ca35b, ca18b, 'divide_detector_output')
ca36b_ca18b_quotient = BekhoffAdcOutputProcessing('ca36b_ca18b_quotient', ca36b, ca18b, 'divide_detector_output')

print "-----------------------------------------------------------------------------------------------------------------"
