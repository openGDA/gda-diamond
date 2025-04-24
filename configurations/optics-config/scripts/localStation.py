'''
Created on 8 Feb 2017

@author: fy65
'''
#localStation.py
#For beamline specific initialisation code.

print "===================================================================";
print "Performing Optics Lab80 specific initialisation code (localStation.py).";
print

print "-"*100
print "Set scan returns to the start positions on completion"
print "   To set scan returns to its start positions on completion please do:"
print "      >>>scansReturnToOriginalPositions=1"
scansReturnToOriginalPositions=0;
print

from gdascripts.scan.installStandardScansWithProcessing import * # @UnusedWildImport
scan_processor.rootNamespaceDict=globals()


from polarimeter.polarimeterHexapod import hpx, hpy, hpz, hpa, hpb, hpc, hexapod  # @UnusedImport
from polarimeter.polarimeterTemperatureMonitor import anatemp,rettemp  # @UnusedImport

from gdascripts.scannable.timerelated import TimeSinceScanStart
timerScannable = TimeSinceScanStart("timerScannable")
print("timerScannable created.")
print("e.g. to expose diode1 every 5 seconds for 1 minute:")
print(">>> scan timerScannable 0 60 5 diode1 0.1")

from gda.device.scannable import DummyScannable
dummy = DummyScannable("dummy")

print "==================================================================="; print; 

print "Run localStation.py completed successfully!"
