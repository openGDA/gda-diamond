from gda.device.scannable import ScannableBase
from gda.epics import CAClient

class CidPhotoDiode(ScannableBase):
    def __init__(self, name, basePvName):
        self.name = name
        self.setInputNames([])
        self.setExtraNames(["xpyp", "xpym", "xmyp", "xmym"])
        self.setOutputFormat(["%4.3f","%4.3f","%4.3f","%4.3f"])
        self.xmymPv = CAClient(basePvName + ":XM:YM:I")
        self.xmymPv.configure()
        self.xmypPv = CAClient(basePvName + ":XM:YP:I")
        self.xmypPv.configure()
        self.xpymPv = CAClient(basePvName + ":XP:YM:I")
        self.xpymPv.configure()
        self.xpypPv = CAClient(basePvName + ":XP:YP:I")
        self.xpypPv.configure()
        
    def asynchronousMoveTo(self, pos):
        pass
    
    def getPosition(self):
        return [self.xmymPv.caget(),self.xmypPv.caget(),self.xpymPv.caget(), self.xpypPv.caget()]
    
    def isBusy(self):
        return 0
    
    