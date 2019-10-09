from gda.device.scannable.component import PositionValidator

from gda.device.monitor import EpicsMonitor
from gda.device.MotorStatus import READY, BUSY

class AxisGroupOkayPositionValidator(PositionValidator):
    """Checks the status of all scannableMotorsToCheck if provided. Otherwise
    the groupStatusMonitor
    """
    
    def __init__(self, groupStatusMonitor, errorMessage, scannableMotorsToCheck=None):
        self.groupStatusMonitor = groupStatusMonitor
        self.errorMessage = errorMessage
        self.scannableMotorsToCheck = scannableMotorsToCheck
        # BL16I-MO-DIFF-01:DEVSTA.STAT
        
    def checkInternalPosition(self, internalPositionObjectArray):
        # use the monitor if no motors provided
        if self.scannableMotorsToCheck==None:
            if int(self.groupStatusMonitor()) != 0:
                return self.errorMessage
            return None
        
        # Check status of all provided motors
        for scannableMotor in self.scannableMotorsToCheck:
            status = scannableMotor.getMotor().getStatus()
            if status not in (READY, BUSY):
                return self.errorMessage+" <"+scannableMotor.getName()+" status was :"+`status`+">"
        return None
    
    def __repr__(self):
        statusString = self.checkInternalPosition(None)
        statusString = ("\n" + statusString) if statusString else ""
        if self.scannableMotorsToCheck==None:
            return "Checks that status on monitor " + self.groupStatusMonitor.getName() + statusString
        else:
            motorNames = [m.getName() for m in self.scannableMotorsToCheck]
            return "Checks the status of motors: " + ', '.join(motorNames) + statusString
        