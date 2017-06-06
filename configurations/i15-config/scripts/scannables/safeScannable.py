from gda.device.scannable import ScannableBase
from gda.device import DeviceException

class SafeScannable(ScannableBase):
    def __init__(self, name, control_scannable, check_scannable, threshold,
                 failIfGreaterNotLessThan):

        self.control_scannable = control_scannable
        self.check_scannable = check_scannable
        self.threshold = threshold
        self.failIfGreaterNotLessThan = failIfGreaterNotLessThan

        self._setNames(name)
        self.setLevel(5)

    def _setNames(self, name):
        self.setName(name);
        self.setInputNames([name])
        self.setExtraNames([self.check_scannable.name]);
        self.setOutputFormat(["%5.5g", "%5.5g"])
        
    def rawGetPosition(self):
        return [self.control_scannable.getPosition(),
                self.check_scannable.getPosition()]
        
    def rawAsynchronousMoveTo(self, new_position):
        error = self.checkPositionValid(self)
        if not error is None:
            raise DeviceException(error)
        return self.control_scannable.rawAsynchronousMoveTo(new_position)

    def isBusy(self):
        return self.control_scannable.isBusy()

    def stop(self):
        return self.control_scannable.stop()

    def atScanStart(self):
        error = self.checkPositionValid(self)
        if not error is None:
            raise DeviceException(error)

    def checkPositionValid(self, illDefinedPosObject=0):
        error = None
        check_scannable_position = self.check_scannable.getPosition()
        if self.failIfGreaterNotLessThan:
            if check_scannable_position > self.threshold:
                error = "more"
        else:
            if check_scannable_position < self.threshold:
                error = "less"

        if error is None:
            return None 
        
        return "position %s %5.5g is %s than %5.5g threshold" % (
                self.check_scannable.name, check_scannable_position,
                error, self.threshold )

    def atScanEnd(self):
        pass