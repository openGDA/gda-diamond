'''
Created on 24 Jun 2010
Please investigate why this file can not be imported from localStation.py
errors: 1. ds problem
        2. theta  warning.
@author: fy65
'''
from rockingMotion_class import RockingMotion

rocktheta=RockingMotion("rocktheta", theta, -5, 5)

def psdrt(t, n=1.0):
    scan ds 1.0 n 1.0 mythen t rocktheta

alias psdrt

#direct scan with rocking command
#scan ds 1.0 2.0 1.0 mythen 10.0 rocktheta 