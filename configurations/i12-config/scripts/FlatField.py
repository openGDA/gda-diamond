from gda.device.detector import DetectorBase

class FlatField(DetectorBase) :

    def __init__(self, count, device, distance):
        self.setName("temp")
        self.setInputNames(["temp"])
        self.setExtraNames([])
        self.setOutputFormat(["%s"])

        # flag which counts down till the next flatfield
        self.countDown = 0 
        # flag which specifies whether the scannable is busy
        self.iAmBusy = 0
        # filename which contains the latest flatfield image
        self.filename = "Not Yet Specified"
        self.countMax = count
        self.driveDevice = device
        self.driveDistance = distance

    def collectData(self):
        self.iAmBusy = 1
        self.countDown-=1
        if self.countDown < 0:
            self.countDown = self.countMax
            self.originalPosition = self.driveDevice.getPosition()
            # move the device out of the way
            self.driveDevice.moveTo(self.originalPosition + self.driveDistance)
            self.filename = PCO4000.readout()
            # move the device out of the way
            self.driveDevice.moveTo(self.originalPosition)
        self.iAmBusy = 0
        return

    def readout(self) :
        return self.filename
    
    def createsOwnFiles(self):
        return 1 
    
    def getStatus(self):
        return self.iAmBusy



