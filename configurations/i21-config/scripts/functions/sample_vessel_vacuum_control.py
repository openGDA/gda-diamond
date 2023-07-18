'''
define function to control the sample vessel vacuum valves for sample changes
Created on 18 Jul 2023

@author: fy65
'''
import installation
from gda.device.scannable import ScannableMotionBase
from gda.epics import CAClient

# control PV = BL21I-EA-SMPL-01:SEQ:CTRL
# state PV = BL21I-EA-SMPL-01:SEQ:CTRL:STATE_RBV

class SampleVesselValvesControl(ScannableMotionBase):
    
    def __init__(self, name, pv):
        self.setName(name)
        self.setInputNames([name])
        self.setOutputFormat(["%d"])
        self.control = CAClient(pv)
        self.state = CAClient(pv + ":STATE_RBV")
        self.control.configure()
        self.state.configure()
        self.val = 0
        
    def getPosition(self):
        if installation.isLive():
            return int(self.control.get()) #0 - Close, 1 - Open
        if installation.isDummy():
            return self.val
    
    def asynchronousMoveTo(self, val):
        if installation.isLive():
            self.control.caput(int(val))
        if installation.isDummy():
            self.val = val
            if val == 1:
                print("Open sample vessel valves")
            if val == 0:
                print("Close sample vessel valves")
        
    def isBusy(self):
        if installation.isLive():
            return int(self.state.caget()) != 2 #2 - Ready, 1 - Opening, 0 - Closing
        if installation.isDummy():
            return False
        
        
sample_vessel_valves = SampleVesselValvesControl("sample_vessel_valves", "BL21I-EA-SMPL-01:SEQ:CTRL")
