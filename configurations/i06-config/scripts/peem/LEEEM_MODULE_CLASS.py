'''
script provided by Francesco Maccherozzi
'''
from gda.device.scannable import PseudoDevice
from peem.LEEM2000_tcp import leem2000
from time import sleep

class LEEM_Scannable_Class(PseudoDevice):
    def __init__(self,name,units,module):
        self.setName(name);
        self.setInputNames([units])
        self.setOutputFormat(['%3.2f'])
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
        self.pos  = float(leem2000.send(command))
        return self.pos

    def asynchronousMoveTo(self, new_position):
        command = "set {}={}".format(self.module,new_position)
        leem2000.send(command)
        sleep(0.2)
        return 

    def isBusy(self):
        return self.iambusy