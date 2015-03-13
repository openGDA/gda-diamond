from gda.device.scannable import PassthroughScannableMotionUnitsDecorator
from gda.device import DeviceException

class MoveThroughOriginScannable(PassthroughScannableMotionUnitsDecorator):
    def asynchronousMoveTo(self, target):
        report = self.checkPositionValid(target)
        if report != None:
            raise DeviceException(report)
        target = float(target)
        currentPosition = self.getPosition()
        signsDiffer = (currentPosition > 0) != (target > 0)
        if signsDiffer:
            self.getDelegate().asynchronousMoveTo(0)
            self.waitWhileBusy()
        self.getDelegate().asynchronousMoveTo(target)
