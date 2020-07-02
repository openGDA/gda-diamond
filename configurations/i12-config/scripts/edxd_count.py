from gda.device.scannable import ScannableMotionBase
from gda.factory import Finder

class edxd_count(ScannableMotionBase):
    # constructor
    def __init__(self, name, detector):
        self.setName(name) 
        self.setLevel(9)
        self.setInputNames([name])
        self.setExtraNames([])
        self.setOutputFormat(["%5.5g"])
        self.edxd = detector
        # set up the cachanel

    # returns the value this scannable represents
    def rawGetPosition(self):
        total = 0
        for i in range(24) :
            total += self.edxd.getSubDetector(i).getEvents()
        return total

    # Does the operation this Scannable represents
    def rawAsynchronousMoveTo(self, new_position):
        self.edxd.setCollectionTime(new_position)
        self.edxd.collectData()

    # Returns the status of this Scannable
    def rawIsBusy(self):
        return self.edxd.isBusy()


