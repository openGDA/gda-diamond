'''
script provided by Francesco Maccherozzi
'''
from gda.device.scannable import PseudoDevice
from peem.LEEM2000_tcp import leem2000

class LEEM_FOV_Rotation_Class(PseudoDevice):
    def __init__(self,name):
        self.setName(name);
        self.setInputNames(['deg'])
        self.setOutputFormat(['%3u'])
        self.setLevel(6)
        self.iambusy = False
        self.pos = 0.0
       
    def atScanStart(self):
        return

    def atScanEnd(self):
        return

    def getPosition(self):
        command = "rir"
        self.pos  = float(leem2000.send(command))
        return self.pos

    def asynchronousMoveTo(self):
        return 

    def isBusy(self):
        return self.iambusy