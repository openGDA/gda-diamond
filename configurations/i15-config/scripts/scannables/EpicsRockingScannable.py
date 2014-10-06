from gda.device.scannable import ScannableMotionBase
from gdascripts.messages.handle_messages import simpleLog
from gdascripts.utils import caget, caput

class EpicsRockingScannable(ScannableMotionBase):

    def __init__(self, name, scannable):
        self.name=name
        self.scannable=ScannableMotionBase()
        self.setName(name)
        self.scannable = scannable
        assert len(scannable.getInputNames())==1
        assert len(scannable.getExtraNames())==0
        assert len(scannable.getOutputFormat())==1
        self.setInputNames(['t'])
        self.setExtraNames(['rock'])
        self.setOutputFormat(['%3.3f', '%d'])
        self.setLevel(5)
        self.mode_rbv=0
        self.exposureTime=-1
        self.verbose=True

    def __repr__(self):
        return "%s(name=%r, scannable=%r)" % (self.__class__.__name__, self.name, self.scannable.name)

    def setupScan(self, centre, rockSize, noOfRocksPerExposure):
        caput(self.scannable.getMotor().getPvName()+":ROCK:STARTPOSITION", centre-rockSize) # deg
        caput(self.scannable.getMotor().getPvName()+":ROCK:ENDPOSITION", centre+rockSize) # deg
        caput(self.scannable.getMotor().getPvName()+":ROCK:NUMROCKS", noOfRocksPerExposure)
        caput(self.scannable.getMotor().getPvName()+":ROCK:ACCELERATION", 50.0) # Degrees/s/s

    def atScanStart(self):
        if self.verbose:
            simpleLog("%r at position %r atScanStart" % (self.scannable.name, self.scannable.getPosition()))

    def stop(self):
        caput(self.scannable.getMotor().getPvName()+":ROCK:STOP", 1)
        simpleLog("%r stopping after stop..." % self.name)

    def atScanEnd(self):
        if self.verbose:
            simpleLog("%r at position %r atScanEnd" % (self.scannable.name, self.scannable.getPosition()))

    def atCommandFailure(self):
        caput(self.scannable.getMotor().getPvName()+":ROCK:STOP", 1)
        simpleLog("%r stopping after failure..." % self.name)

    def getPosition(self):
        return [self.exposureTime, caget(self.scannable.getMotor().getPvName()+":ROCK:CURRENTROCK_RBV")]

    def asynchronousMoveTo(self, exposureTime):
        self.exposureTime = exposureTime
        caput(self.scannable.getMotor().getPvName()+":ROCK:TIME", exposureTime) # s
        caput(self.scannable.getMotor().getPvName()+":ROCK:START", 1) # Degrees/s/s

    def isBusy(self):
        mode_rbv = caget(self.scannable.getMotor().getPvName()+":ROCK:MODE_RBV")
        if mode_rbv != self.mode_rbv:
            simpleLog("mode_rbv changed from %r to %r" % (self.mode_rbv, mode_rbv))
            self.mode_rbv=mode_rbv
        return mode_rbv == 1 or mode_rbv == 2
