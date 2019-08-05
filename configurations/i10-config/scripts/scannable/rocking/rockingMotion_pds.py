'''
Created on 24 Jun 2010
Please investigate why this file can not be imported from localStation.py
errors: 1. ds problem
        2. theta  warning.
@author: fy65
'''
from rockingMotion_class import RockingMotion
from rockingMotorDuringCounting import RockingMotorDuringCounting
from gdaserver import th
from gda.device.scannable import DummyScannable

ds = DummyScannable("ds")
rockthetascan=RockingMotion("rockthetascan", th, -1, 1) 
rockthetacounting=RockingMotorDuringCounting("rockthetacounting", th, -1, 1)


