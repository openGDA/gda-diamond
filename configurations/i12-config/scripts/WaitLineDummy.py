from gda.device.scannable import ScannableMotionBase
from time import sleep

class WaitLineDummy(ScannableMotionBase):
    # constructor
    def __init__(self, name,wait=30):
        self.setName(name) 
        self.setInputNames([name])
        self.setExtraNames([])
        self.setOutputFormat(["%5.5g"])
        self.myposition = 0
        self.prelinewait = wait


    # returns the value this scannable represents
    def rawGetPosition(self):
        return self.myposition

    # Does the operation this Scannable represents
    def rawAsynchronousMoveTo(self, new_position):
        self.myposition = new_position

    # Returns the status of this Scannable
    def rawIsBusy(self):
        return False

    def atScanLineStart(self):
        sleep(self.prelinewait)


