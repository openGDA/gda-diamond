'''
Created on 24 Jun 2010
Please investigate why this file can not be imported from localStation.py
errors: 1. ds problem
        2. theta  warning.
@author: fy65
'''

from gdaserver import th, pimte
from scannable.rocking.rockingMotion_pds import rockthetacounting, ds
from gdascripts.scan.installStandardScansWithProcessing import scan

CCD_EXPOSURE_TIME=2.0 #seconds
ROCKING_RANGE_CENTRE=0.0
NUMBER_OF_IMAGES_TO_COLLECT=10

THETA_LOW_LIMIT=-101.0 # hardware limit
THETA_HIGH_LIMIT=189.0 #hardware limit

theta_range = th.getSpeed()*CCD_EXPOSURE_TIME

if theta_range > (THETA_HIGH_LIMIT-THETA_LOW_LIMIT):
    raise Exception("theta rocking range is greater than hardware limits permitted")

start_theta_angle=ROCKING_RANGE_CENTRE-theta_range/2.0
end_theta_angle=ROCKING_RANGE_CENTRE+theta_range/2.0
if (start_theta_angle/2.0)<THETA_LOW_LIMIT:
    raise Exception("start rocking angle is outside hardware low limit")
if (end_theta_angle/2.0) > THETA_HIGH_LIMIT:
    raise Exception("end rocking angle is outside hardware high limit")

rockthetacounting.setLowerLimit(start_theta_angle)
rockthetacounting.setUpperLimit(end_theta_angle)

scan([ds, 1, NUMBER_OF_IMAGES_TO_COLLECT, 1, pimte, CCD_EXPOSURE_TIME, rockthetacounting])