from gda.device.scannable import PseudoDevice
from gda.factory import Finder

finder = Finder.getInstance()

class edxd_count(PseudoDevice):
    # constructor
    def __init__(self, name, detector, nelements=24):
        self.setName(name) 
        self.setLevel(9)
        self.setInputNames([name])
        self.setExtraNames([])
        self.setOutputFormat(["%5.5g"])
        self.edxd = detector
        self.nelements = nelements
        # set up the cachanel

    # returns the value this scannable represents
    def rawGetPosition(self):
        total = 0
        for i in range(self.nelements) :
            total += self.edxd.getSubDetector(i).getEvents()
        return total

    # Does the operation this Scannable represents
    def rawAsynchronousMoveTo(self, new_position):
        self.edxd.setCollectionTime(new_position)
        self.edxd.collectData()

    # Returns the status of this Scannable
    def rawIsBusy(self):
        return self.edxd.isBusy()


