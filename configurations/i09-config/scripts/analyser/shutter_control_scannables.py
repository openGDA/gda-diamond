from gda.device import MotorStatus, DeviceException
from gda.device.scannable import ScannableBase
from gda.device.scannable import ScannablePositionChangeEvent 

from time import sleep

class ValueHolderScannable(ScannableBase):

    def __init__(self, name, pos):
        self.setName(name)
        self.setInputNames([name])
        self.setExtraNames([])
        self.setOutputFormat(['%s'])
        self._is_busy = False;
        self._position = pos

    def getPosition(self):
        return self._position

    def rawAsynchronousMoveTo(self, pos):
        self._is_busy = True
        if not isinstance(pos, bool):
            raise DeviceException(self.getName() + " can only take booleans, received value " + str(pos) )
        self._position = pos
        self._is_busy = False
        self.notifyIObservers(self, bool(pos))

    def isBusy(self):
        return self._is_busy

    def waitWhileBusy(self):
        while self.isBusy():
            sleep(0.1)

close_shutters_between_regions = ValueHolderScannable("close_shutters_between_regions", True)
close_shutters_at_end_of_scan = ValueHolderScannable("close_shutters_at_end_of_scan", False)