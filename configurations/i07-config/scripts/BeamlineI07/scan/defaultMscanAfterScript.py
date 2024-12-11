'''
Script to remove motors from coordinate system after a malcolm scan.  This is
necessary as otherwise they will not be movable when the anticollision system
is active.
'''

from gdascripts.utils import caput

caput("BL07I-MO-STEP-08:COORDINATE_SYS_GROUP", "Empty")

if ( "BL07I-ML-SCAN-03" in scanRequest.getDetectors().keySet() ):
    caput("BL07I-EA-EIGER-01:OD:FAN:BlockSize", 1000000000)
