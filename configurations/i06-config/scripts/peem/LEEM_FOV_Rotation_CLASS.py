'''
script provided by Francesco Maccherozzi
@deprecated: replaced by EPICS PVs on 2021-11-17
'''
from gda.device.scannable import ScannableMotionBase
from peem.LEEM2000_tcp import leem2000

class LEEM_FOV_Rotation_Class(ScannableMotionBase):
    def __init__(self,name, units, leem2000):
        self.setName(name);
        self.setInputNames([name])
        self.setOutputFormat(['%.3f'])
        self.setLevel(6)
        self.units = units
        self.iambusy = False
        self.leem2000=leem2000
       
    def atScanStart(self):
        return

    def atScanEnd(self):
        return

    def getPosition(self):
        return float(self.leem2000.send('rir'))

    def asynchronousMoveTo(self):
        return 

    def isBusy(self):
        return self.iambusy
    
    