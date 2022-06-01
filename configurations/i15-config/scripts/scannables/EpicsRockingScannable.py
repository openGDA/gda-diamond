from gda.device.scannable import ScannableMotionBase
from gdascripts.messages.handle_messages import simpleLog
from gdascripts.utils import caget, caput

class EpicsRockingScannable(ScannableMotionBase):
    """ This scannable needs to be configured with a call to setupScan before
        being used:
        
            <scn>.setupScan(centre, rockSize, noOfRocksPerExposure)
        
        For example:
        
            pos dkphi 58-4
            dphi_rockscan.setupScan(58, 4, 2)
            pos dphi_rockscan 10
        
        will configure dphi_rockscan to make two rocks, first to 58+4 and then
        back to 58-4 at a speed such that the moves take 10 seconds.
        
        This scannable expects the underlying motor to already be at the start
        position before it is asked to move, and will leave the motor at its
        final position. Thus if noOfRocksPerExposure is even then each move
        will end up where it started, ready for the next rock, otherwise it
        will end up at it's final position, in a position which is not good
        for the start of the next move.
    """

    def __init__(self, name, scannable, check_cs_pv_base, check_cs_raw_value, check_cs_axis_value):
        self.name=name
        self.scannable=ScannableMotionBase()
        self.setName(name)
        self.scannable = scannable
        self.check_cs_pv_base=check_cs_pv_base
        self.check_cs_raw_pv = check_cs_pv_base+':CsRaw_RBV'
        self.check_cs_axis_pv = check_cs_pv_base+':CsAxis_RBV'
        self.check_cs_raw_value=check_cs_raw_value
        self.check_cs_axis_value=check_cs_axis_value
        assert len(scannable.getInputNames())==1
        assert len(scannable.getExtraNames())==0
        assert len(scannable.getOutputFormat())==1
        self.setInputNames(['t'])
        self.setExtraNames(['rock'])
        self.setOutputFormat(['%3.3f', '%d'])
        self.setLevel(5)
        self.mode_rbv=0
        self.exposureTime=-1
        self.verbose=False

    def __repr__(self):
        return "%s(name=%r, scannable=%r)" % (self.__class__.__name__, self.name, self.scannable.name)

    def setupScan(self, centre, rockSize, noOfRocksPerExposure):
        if noOfRocksPerExposure % 2 == 1:
            simpleLog("%r configured with noOfRocksPerExposure=%r so scan points will not end at their next start position!" % (self.scannable.name, noOfRocksPerExposure))
            simpleLog("For use in a scan, you should use an even number of rocks per exposure.")
            simpleLog("="*80)
        self.checkSetup()
        caput(self.scannable.getMotor().getPvName()+":ROCK:STARTPOSITION", centre-rockSize) # deg
        caput(self.scannable.getMotor().getPvName()+":ROCK:ENDPOSITION", centre+rockSize) # deg
        caput(self.scannable.getMotor().getPvName()+":ROCK:NUMROCKS", noOfRocksPerExposure)
        caput(self.scannable.getMotor().getPvName()+":ROCK:ACCELERATION", 50.0) # Degrees/s/s

    def checkSetup(self):
        ok=True
        check_cs_raw_value = caget(self.check_cs_raw_pv)
        check_cs_axis_value = caget(self.check_cs_axis_pv)
        if check_cs_raw_value <> self.check_cs_raw_value:
            simpleLog("%r failed the coordinate system check, %r returned %r rather than %r, rockscan may not work!" % (self.scannable.name, self.check_cs_raw_pv, check_cs_raw_value, self.check_cs_raw_value))
            ok = False
        if check_cs_axis_value <> self.check_cs_axis_value:
            simpleLog("%r failed the coordinate system check, %r returned %r rather than %r, rockscan may not work!" % (self.scannable.name, self.check_cs_axis_pv, check_cs_axis_value, self.check_cs_axis_value))
            ok = False
        return ok

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
        if self.verbose and mode_rbv != self.mode_rbv:
            simpleLog("mode_rbv changed from %r to %r" % (self.mode_rbv, mode_rbv))
            self.mode_rbv=mode_rbv
        return mode_rbv == 1 or mode_rbv == 2
