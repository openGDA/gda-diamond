# Fast shutter operation on a point-by-point basis
# Jonathan Rawle, Beamline I07, October 2010

from gda.device.detector import DetectorBase
from gda.device.scannable import ScannableMotionBase
from gda.epics import CAClient 
from time import sleep

# To use the fast shutter, use a scan line such as:
#
# scan motor 1 10 1 fs1 1 pil2roi 5 fs2
#
# Note that fs1 MUST be given an integration time (i.e. 1)
# and that you can't add these to the defaults list,
# they must be included every scan line.
# The order is also important.
#
# In addition, any PseudoDevices that you want to trigger
# before the fast shutter must have a level lower than 7,
# for example waitTimer has its level changed at the end of
# this script. That means a waitTimer will complete before
# the shutter opens.

class FastShutterOpenClass(ScannableMotionBase):

    def __init__(self, name, pvstring, pvvalue, delayAfterOpening=0.5):
        self.name = name
        self.inputNames = [name]
        self.outputFormat = ['%d']
        self.level = 7
        self.delayAfterOpening = delayAfterOpening
        self.pv = CAClient(pvstring)
        self.pv.configure()
        self.pvval = pvvalue
        self.firstpoint = False

    def collectData(self):
        self.open()
        
    def isBusy(self):
        return 0

    def readout(self):
        return self.getPosition()

    def getPosition(self):
        return int(float(self.pv.caget()))

    def getCollectionTime(self):
        return 0

    def asynchronousMoveTo(self, rawposition):
        self.open()

    def createsOwnFiles(self):
        return False;

    def atScanStart(self):
        self.firstpoint = True

    def open(self, report=False):
        #print "Opening fs"
        self.pv.caput(self.pvval)
        sleep(self.delayAfterOpening)
        if self.firstpoint:
            print "Opening fast shutter for each point"
            self.firstpoint = False
        if report:
            print "Opened fast shutter"
                
class FastShutterCloseClass(DetectorBase):

    def __init__(self, name, pvstring, pvvalue, delayAfterClosing=0):
        self.name = name
        self.inputNames = [name]
        self.outputFormat = ['%d']
        self.level = 9
        self.delayAfterClosing = delayAfterClosing
        self.pv = CAClient(pvstring)
        self.pv.configure()
        self.pvval = pvvalue
        self.firstpoint = False

    def collectData(self):
        #self.close()
        return

    def isBusy(self):
        return 0

    def readout(self):
        self.close()
        return self.getPosition()

    def getPosition(self):
        return int(float(self.pv.caget()))

    def getCollectionTime(self):
        return 0

    def asynchronousMoveTo(self, rawposition):
        self.close()

    def createsOwnFiles(self):
        return False;
    
    def close(self, report=False):
        self.pv.caput(self.pvval)
        sleep(self.delayAfterClosing)
        if self.firstpoint:
            print "Closing fast shutter for each point"
            self.firstpoint = False
        if report:
            print "Closed fast shutter"

    def atScanStart(self):
        self.firstpoint = True
                    
    def atScanEnd(self):
        #print "Scan end"
        self.close(report = True)
    
    def stop(self):
        #print "Stop"
        self.close(report = True)

    def atCommandFailure(self):
        #print "Fail"
        self.close(report = True)
        
fs1 = FastShutterOpenClass('fs1', "BL07I-EA-SHTR-01:CON", 1, 0.5);
fs2 = FastShutterCloseClass('fs2', "BL07I-EA-SHTR-01:CON", 0, 0);
waitTimer.setLevel(6)
