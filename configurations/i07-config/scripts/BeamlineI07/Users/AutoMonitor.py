from gda.device.detector import DetectorBase

#
# Class for creating monitors that automatically set their integration times
# to that of the detector
#

class AutoMonitor(DetectorBase):

    def __init__(self, name, monitor, detector):
        self.setName(name)
        self.detector = detector
        self.monitor = monitor

    def collectData(self):
        self.setCollectionTime(0)
        self.monitor.collectData()

    def getStatus(self):
        return self.monitor.getStatus()

    def readout(self):
        return self.monitor.readout()

    def setCollectionTime(self, time):
        self.monitor.setCollectionTime(self.detector.getCollectionTime())
#        print "Collection time set to " + str(self.monitor.getCollectionTime())

    def getCollectionTime(self):
        return self.detector.getCollectionTime()

    def getPosition(self):
        return self.monitor.getPosition()        

    def asynchronousMoveTo(self, time):
        self.monitor.asynchronousMoveTo(time)

    def createsOwnFiles(self):
        return False;

    def toString(self):
        return self.getName() + ": Integration=" + str(self.getCollectionTime()) +" (follows '"+ self.detector.getName() + "'), Count=" + str(self.getPosition());

class CountNormaliser(ScannableMotionBase):
    def __init__(self, name, numerator, denominator, constant=1):
        self.setName(name)
        self.setInputNames([name])
        self.numerator = numerator
        self.denominator = denominator
        self.constant = constant

    def getPosition(self):
        return float(self.constant)*self.numerator.getPosition()/self.denominator.getPosition()

    def asynchronousMoveTo(self, time):
        while self.isBusy():
            sleep(0.2)

    def createsOwnFiles(self):
        return False;

    def isBusy(self):
        if self.numerator.isBusy() or self.denominator.isBusy():
            return 1
        else:
            return 0

    def toString(self):
        return self.getName() + ": " +str(self.constant)+"*"+ self.numerator.getName() +"/"+ self.denominator.getName() + "=Count=" + str(self.getPosition());

class CountNormaliserPil(ScannableMotionBase):
    def __init__(self, name, numerator, index, denominator, constant=1, denom_offset=0):
        self.setName(name)
        self.setInputNames([name])
        self.numerator = numerator
        self.index = index
        self.denominator = denominator
        self.constant = constant
        self.denom_offset = denom_offset

    def getPosition(self):
        p = self.numerator.getPosition()
        i = self.denominator.getCollectionTime()
        return float(self.constant)*p[self.index]/(self.denominator.getPosition() + self.denom_offset*i)

    def asynchronousMoveTo(self, time):
        while self.isBusy():
            sleep(0.2)

    def createsOwnFiles(self):
        return False;

    def isBusy(self):
        if self.numerator.isBusy() or self.denominator.isBusy():
            return 1
        else:
            return 0

    def toString(self):
        return self.getName() + ": " +str(self.constant)+"*"+ self.numerator.getName() + "[" + str(self.index) + "]" +"/"+ self.denominator.getName() + "=Count=" + str(self.getPosition());
