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

from polarimeter.polarimeterHexapod import hpx, hpy, hpz, hpa, hpb, hpc, hexapod  # @UnusedImport
from polarimeter.polarimeterTemperatureMonitor import anatemp,rettemp  # @UnusedImport
from polarimeter.Scaler8512 import ca1sr,ca2sr,ca3sr,ca4sr,ca5sr,ca6sr,ca7sr,ca8sr,scaler  # @UnusedImport @UnresolvedImport

print "==================================================================="; print; 

print "Run localStation.py completed successfully!"
