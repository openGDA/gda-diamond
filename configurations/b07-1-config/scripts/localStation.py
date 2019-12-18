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

# Add a string to hold extra detectors it will be appended to analyser scans run from the GUI
# See uk.ac.diamond.daq.devices.specs.phoibos.ui.handlers.RunSequenceHandler
extraDetectors = ""

print "-----------------------------------------------------------------------------------------------------------------"
