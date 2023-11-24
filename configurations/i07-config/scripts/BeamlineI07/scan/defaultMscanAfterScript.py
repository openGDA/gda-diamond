'''
Script to remove motors from coordinate system after a malcolm scan.  This is
necessary as otherwise they will not be movable when the anticollision system
is active.
'''

from gdascripts.utils import caput

caput("BL07I-MO-STEP-08:COORDINATE_SYS_GROUP", "Empty")
