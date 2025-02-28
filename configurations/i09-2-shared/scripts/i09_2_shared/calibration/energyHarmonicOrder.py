from gda.device import MotorStatus
from gda.device.scannable import ScannableMotionBase

from time import sleep

class EnergyHarmonicOrder(ScannableMotionBase):

    def __init__(self, name):
        self.setName(name)
        self.setInputNames([name])
        self.setExtraNames([])
        self.setOutputFormat(['%.0f'])
        self._is_busy = False;
        self._harmonicOrder = 1

    def getPosition(self):
        return self._harmonicOrder

    def rawAsynchronousMoveTo(self, n):

        #Check that the move is an integer
        if (n % 1) != 0:
            raise TypeError("New position " + str(n) + " should be an integer")

        self.notifyIObservers(self, MotorStatus.BUSY);
        self._is_busy = True
        self._harmonicOrder = n
        self._is_busy = False
        self.notifyIObservers(self, MotorStatus.READY);

    def isBusy(self):
        return self._is_busy

    def waitWhileBusy(self):
        while self.isBusy():
            sleep(0.1)
