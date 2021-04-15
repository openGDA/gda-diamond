from gda.device.scannable import ScannableMotionBase

class EdxdBinned(ScannableMotionBase):
    # constructor
    def __init__(self, name, detector):
        self.setName(name)
        self.setLevel(9)
        self.detector = detector 
        self.setInputNames(["count","start", "stop"])
        self.setExtraNames(["e01","e02","e03","e04","e05","e06","e07","e08","e09","e10","e11","e12","e13","e14","e15","e16","e17","e18","e19","e20","e21","e22","e23", "e24"])
        self.setOutputFormat(["%5.5g"])
        self.count = 10
        self.start = 0
        self.end = 100
        # set up the cachanel

    # returns the value this scannable represents
    def rawGetPosition(self):
        values = [self.count, self.start, self.end]
        for i in range(24) :
            values += [ sum(self.data[i].getData()[self.start:self.end]) ]
        return values

    # Does the operation this Scannable represents
    def rawAsynchronousMoveTo(self, new_position):
        (self.count, self.start, self.end) = new_position
        # now modify the values for energy
        scale = self.detector.getSubDetector(0).getBinWidth()
        self.start = int(self.start/scale)
        self.end = int(self.end/scale)
        self.data = self.detector.acquire(self.count)        

    # Returns the status of this Scannable
    def isBusy(self):
        return self.detector.isBusy()
