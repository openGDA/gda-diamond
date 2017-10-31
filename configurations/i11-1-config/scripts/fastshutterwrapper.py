from gda.device.scannable import ScannableBase

class FastShutter(ScannableBase):
    def __init__(self, shutter):
        self.shutter = shutter
        self.name = shutter.name+"_wrapper"
        self.inputNames = []
        self.extraNames = []
        self.outputFormat = []
    def atScanStart(self):
        self.shutter('OPEN')
    def atScanEnd(self):
        self.shutter('CLOSE')
    def rawGetPosition(self):
        return None
    def rawAsynchronousMoveTo(self, posn):
        pass
    def rawIsBusy(self):
        return False