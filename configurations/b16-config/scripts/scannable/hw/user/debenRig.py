from gda.device.scannable import ScannableBase
from gdascripts.scannable.epics.PvManager import PvManager

class DebenRig(ScannableBase):
    def __init__(self, name, pvroot):
        self.name = name
        self.pvManager = PvManager(pvroot=pvroot)

        self.setName(name);
        self.setInputNames(['N'])
        self.setExtraNames([]);
        self.setOutputFormat(['%6.3f'] * (len(self.getInputNames()) + len(self.getExtraNames())))
        self.setLevel(5)

        self.verbose = False
        self.TIMEOUT=5

    def __repr__(self):
        return "%s(name=%r, pvManager=%r)" % (self.__class__.__name__, self.name, self.pvManager)

    def getPosition(self):
        return float(self.pvManager[self.inputNames[0]+'_RBV'].caget())

    def asynchronousMoveTo(self, value):
        self.pvManager[self.inputNames[0]].caput(self.TIMEOUT, float(value))
        self.pvManager['GOTO'].caput(self.TIMEOUT, 1)

    def isBusy(self):
        return False
