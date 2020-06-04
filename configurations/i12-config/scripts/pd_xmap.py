from gda.device.scannable import ScannableMotionBase
from gda.device.detector import MultiDetectorBase

class XMap(MultiDetectorBase):
    """Device to allow control and readback of X value"""
    def __init__(self, xmap, name, position):
        ScannableMotionBase.__init__(self) #@UndefinedVariable
        self.setName(name)
        self.setInputNames([name])
        self.X = position
        
    def rawIsBusy(self):
        return 0

    def rawGetPosition(self):
        return self.X

    def rawAsynchronousMoveTo(self,new_position):
        self.X = new_position    