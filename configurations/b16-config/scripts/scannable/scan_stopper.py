from gda.device.scannable import ScannableBase
from gda.jython import InterfaceProvider as IP

class ScanStopper(ScannableBase):
    def __init__(self, name, condition):
        self.name = name
        self.condition = condition
        self.inScan = False
        self.extraNames = []
        self.inputNames = []
        self.outputFormat = []

    def atScanStart(self):
        self.inScan = True

    def atPointEnd(self):
        if self.inScan and self.condition():
            self.inScan = False
            IP.getCurrentScanController().requestFinishEarly()

    def getPosition(self):
        return None


class ThresholdInterrupt():
    def __init__(self, callable, threshold):
        self.callable = callable
        self.threshold = threshold

    def __call__(self):
        return self.callable() > self.threshold
