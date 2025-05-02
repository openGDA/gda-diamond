'''
Scannable class to support Attocube Piezo motor. It support offsets and position tolerance (which is default to 1)
This class requires EPICS PVs for setting the target and motion stop.

Created on 22 Feb 2019

@author: wvx67826

updated on 23 April 2025
@author: Fajin Yuan

'''

from gda.device.scannable import ScannableMotionBase
from gda.epics import CAClient
import math

class MEAttocubePiezo(ScannableMotionBase):
    
    # The constructor.
    def __init__(self, name, rootPvName ="ME01D-EA-ATTO-01"):
        self.setName(name)
        self.setInputNames([name])
        self.setOutputFormat(["%.2f"])
        self.offsets = 0.0
        self.val = CAClient(rootPvName +":PHI")
        self.off = CAClient(rootPvName + ":PHI.STOP")
        self.val.configure()
        self.off.configure()
        self.currentValue = None
        self.tor= 1
        self.level = 10
        self.target = None

    def setTolerance(self, tor):
        self.tor = tor

    def getTolerance(self):
        return self.tor

    def rawGetPosition(self):
        self.currentValue = float(self.val.caget()) + self.offsets
        return self.currentValue

    def rawAsynchronousMoveTo(self,new_position):
        self.target = float(new_position)
        self.val.caput(self.target)

    def stop(self):
        self.off.caput(1)

    def rawIsBusy(self):
        return math.fabs(self.target - self.rawGetPosition()) < self.tor

    def toFormattedString(self):
            return self.name + " : " + self.getInputNames()[0] +" : " + str(self.getPosition())

rasorphi = MEAttocubePiezo("rasorphi", rootPvName ="ME01D-EA-ATTO-01")