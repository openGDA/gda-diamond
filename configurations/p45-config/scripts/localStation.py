# localStation.py
# For beamline specific initialisation code.
#

# Disables the old mscan
#from mapping_scan_commands import (
#    mscan, detector, scan_request, submit, step, grid, circ, poly, rect)

# Enables the new mscan
from gdascripts.mscanHandler import *

print "Installing standard scans with processing"
from gdascripts.scan.installStandardScansWithProcessing import * #@UnusedWildImport
scan_processor.rootNamespaceDict = globals()
