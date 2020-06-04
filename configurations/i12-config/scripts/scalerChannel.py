from gda.device.scannable import ScannableMotionBase
from gda.epics import CAClient
import time


class scalerChannel(ScannableMotionBase):
    # constructor
    def __init__(self, name, number, device):
        self.number = number
        self.setName(name) 
        self.setInputNames([name])
        self.setExtraNames([])
        self.setOutputFormat(["%5.5g"])
        self.setLevel(100)
        self.currentposition = device.readout()[number]# this template scannable represents a single number
        self.iambusy = 0 # flag to hold the status of the scannable
        self.scalerCountMode = CAClient("BL12I-EA-DET-01:SCALER.CONT")
        self.scalerCountMode.configure()
        self.device = device

    # returns the value this scannable represents
    def rawGetPosition(self):
        return self.value

    # Does the operation this Scannable represents
    def rawAsynchronousMoveTo(self, new_position):
        self.iambusy = 1
        # make sure that the counter is in the right mode
        mode = self.scalerCountMode.caget()
        self.scalerCountMode.caput(0)
        self.device.setCollectionTime(new_position)
        self.device.collectData()
        while self.device.isBusy() :
            time.sleep(0.1)
        self.value = self.device.readout()[self.number]
        # put the mode back once finished
        self.scalerCountMode.caput(mode)
        self.iambusy = 0

    # Returns the status of this Scannable
    def rawIsBusy(self):
        return self.iambusy


