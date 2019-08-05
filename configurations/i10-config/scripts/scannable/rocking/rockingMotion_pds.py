'''
Created on 24 Jun 2010

@author: fy65
'''
from rockingMotion_class import RockingMotion
from rockingMotorDuringCounting import RockingMotorDuringCounting
from gdaserver import th
from gda.device.scannable import DummyScannable

ds = DummyScannable("ds")
rocktheta=RockingMotion("rocktheta", th, -1, 1) 
rockthetascan=RockingMotion("rockthetascan", th, -1, 1) 
rockthetacounting=RockingMotorDuringCounting("rockthetacounting", th, -1, 1)


