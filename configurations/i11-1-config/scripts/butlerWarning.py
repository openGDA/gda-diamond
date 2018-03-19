from gdascripts.pd.dummy_pds import ZeroInputExtraFieldsDummyPD
from time import sleep

class PositionerWarning(ZeroInputExtraFieldsDummyPD):
    def __init__(self, name, device, allowed_position):
        ZeroInputExtraFieldsDummyPD.__init__(self, name)
        self._device = device
        self._allowed = allowed_position

    def atScanStart(self):
        if self._device() != self._allowed:
            print("Can't start scan while %s is in %s position" %(self._device.name, self._device()))
            while self._device() != self._allowed:
                sleep(1)
            sleep(10)
            print("Continuing scan")
                
        