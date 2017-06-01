from gda.device.scannable import ScannableBase
from gdascripts.scannable.epics.PvManager import PvManager
from time import sleep

class DebenRig(ScannableBase):
    def __init__(self, name, pvroot, delay=5):
        self.name = name
        self.delay = delay
        self.pvManager = PvManager(pvroot=pvroot)

        self.setName(name);
        self.setInputNames(['N'])
        self.setExtraNames([]);
        self.setOutputFormat(['%6.3f'] * (len(self.getInputNames()) + len(self.getExtraNames())))
        self.setLevel(5)
        
        self.req_time = time.time()
#         self.req_val = self.getPosition()

        self.verbose = False
        self.TIMEOUT=10

    def __repr__(self):
        return "%s(name=%r, pvManager=%r)" % (self.__class__.__name__, self.name, self.pvManager)

    def getPosition(self):
        return float(self.pvManager[self.inputNames[0]+'_RBV'].caget())
    
    def _req_val(self):
        return float(self.pvManager[self.inputNames[0]].caget())
    
    req_val = property(_req_val)

    def asynchronousMoveTo(self, value):
        self.req_time = time.time()
        self.pvManager[self.inputNames[0]].caput(self.TIMEOUT, float(value))
        while abs(self.getPosition() - value) > 0.0001:
            sleep(0.1)
        self.pvManager['GOTO'].caput(self.TIMEOUT, 1)

    def isBusy(self):
        return self.req_time + self.delay > time.time()
