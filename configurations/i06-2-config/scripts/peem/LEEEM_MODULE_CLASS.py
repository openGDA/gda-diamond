'''
script provided by Francesco Maccherozzi
'''
from gda.device.scannable import ScannableMotionBase
from time import sleep

class LEEM_Scannable_Class(ScannableMotionBase):
    def __init__(self,name,units,module,leem2000):
        self.setName(name);
        self.setInputNames([name])
        self.setOutputFormat(['%3.2f'])
        self.units=units
        self.leem2000=leem2000
        self.setLevel(6)
        self.module = module
        self.iambusy = False
        self.pos = 0.0
       
    def atScanStart(self):
        return

    def atScanEnd(self):
        return

    def getPosition(self):
        command = "get {0}".format(self.module)
        self.pos  = float(self.leem2000.send(command))
        return self.pos

    def asynchronousMoveTo(self, new_position):
        command = "set {}={}".format(self.module, new_position)
        self.leem2000.send(command)
        sleep(0.2)
        return 

    def isBusy(self):
        return self.iambusy
    
    def toString(self):
        return '{}: {} {}'.format(self.getName(),self.getPosition(),self.units)