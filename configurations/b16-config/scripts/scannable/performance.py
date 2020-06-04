#from scannable.performance import LogTimeSinceLastGetPositionLessConstant
#twrite = LogTimeSinceLastGetPositionLessConstant('twrite', 'BL18B-EA-IOC-10:TWRITE')


from gda.device.scannable import ScannableMotionBase
from gda.epics import CAClient
import time

class _Timer(object):

    def __init__(self):
        self.lastStartClock = 0
        self.start()
        
    def start(self):
        self.lastStartClock = time.time();
        
    def elapsed(self):
        return time.time() - self.lastStartClock
    
    def hasElapsed(self, deltaTime):
        return self.elapsed() >= deltaTime


class LogTimeSinceLastGetPositionLessConstant(ScannableMotionBase):

    def __init__(self, name, logPv):
        # logPv e.g.BL16I-EA-IOC-10:TWRITE
        self.name = name
        self.inputNames = [name]
        self.outputFormat = ['%6.2f']
        self.level = 9
        self.logCAC = CAClient(logPv)
        self.logCAC.configure()

        self.timer = _Timer()
        self.toSubtract = 0

    def asynchronousMoveTo(self, toSubtract):
        self.toSubtract = toSubtract

    def isBusy(self):
        return False
    
    def atScanStart(self):
        self.timer.start()
        
    def getPosition(self):
        deltaTime = self.timer.elapsed()
        self.timer.start()
        self.logCAC.caput(deltaTime - self.toSubtract)
        return deltaTime - self.toSubtract
