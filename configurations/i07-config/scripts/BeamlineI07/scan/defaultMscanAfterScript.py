'''
Script to return motors to coordinate system after a malcolm scan so that they
can be run with deferred moves.  This is necessary as some malcolm scans remove
motors they are not using but cannot add them back at the end, so if you were 
to run a static scan immediately afterwards the motors would not move.
'''

from gdascripts.utils import caput

STATIC_SCAN_NAMES = ["BL07I-ML-SCAN-11", "BL07I-ML-SCAN-12", "BL07I-ML-SCAN-32"]

errorMessage = "Scan request not available, could not reset deferred motors."
if scanRequest is None : raise ValueError(errorMessage)

# Set of Strings of runnable device names
detectors = scanRequest.getDetectors().keySet()

for name in STATIC_SCAN_NAMES:
    if name in detectors:
        #Due to the epics setup, we have to set the axes at the same time as 
        #the coordinate system
        caput("BL07I-MO-STEP-08:M4:CsAxis", "V")
        caput("BL07I-MO-STEP-08:M5:CsAxis", "U")
        caput("BL07I-MO-STEP-08:M7:CsAxis", "C")

        caput("BL07I-MO-STEP-08:M4:CsPort", "CS2")
        caput("BL07I-MO-STEP-08:M5:CsPort", "CS2")
        caput("BL07I-MO-STEP-08:M7:CsPort", "CS2")

        break
