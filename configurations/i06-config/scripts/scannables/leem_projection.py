'''
Created on 30 Jan 2026

@author: fy65
'''
from gda.device.scannable import ScannableMotionBase
from gda.epics import CAClient
from i06shared import installation

class ProjectionInLeem(ScannableMotionBase):
    '''
    get PresetA value from LEEM device
    '''


    def __init__(self, name, pv = "BL06I-EA-LEEM-01:PRESETA:RBV.SVAL"):
        '''
        Constructor
        '''
        self.setName(name)
        self.setInputNames([name])
        self.setOutputFormat(["%s"])
        self.cli = CAClient(pv)

    def getPosition(self):
        if installation.isDummy():
            return "real"
        if not self.cli.isConfigured():
            self.cli.configure()
        val = self.cli.caget()
        if val.contains("LEEM"):
            return "reciprocal"
        elif val.contains("disp"):
            return "energy"
        else:
            return "real"

    def asynchronousMoveTo(self, v):
        raise ValueError("This is a Read-Only scannable")

    def isBusy(self):
        return False

leem_presetA = ProjectionInLeem("leem_presetA")