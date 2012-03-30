'''
Created on 24 Jun 2010
Please investigate why this file can not be imported from localStation.py
errors: 1. ds problem
        2. theta  warning.
@author: fy65
'''
from rockingMotion_class import RockingMotion
from rockingMotorDuringCounting import RockingMotorDuringCounting

rocktheta=RockingMotion("rocktheta", ss1.theta, -1, 1) #@UndefinedVariable
rockss1y2=RockingMotorDuringCounting("rockss1y2", ss1_y2, -1, 1) #@UndefinedVariable
rockss1y3=RockingMotorDuringCounting("rockss1y3", ss1_y3, -1, 1) #@UndefinedVariable
rockss2y=RockingMotorDuringCounting("rockss2y", ss2_y, -1, 1) #@UndefinedVariable
