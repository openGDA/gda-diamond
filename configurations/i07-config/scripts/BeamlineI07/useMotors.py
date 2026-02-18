
from Diamond.PseudoDevices.EpicsMotors import EpicsMotorOffsetClass;
from gdascripts.installation import isLive # @UnresolvedImport
from gdaserver import MotorDELTA_DIFF1, MotorGAMMA_DIFF1, MotorOMEGA_DIFF1, MotorTHETA_DIFF1, MotorCHI_DIFF1, hex1rx # @UnresolvedImport
from gda.device.scannable import DummyScannable

if isLive():
    diff1vdeltaoffset = EpicsMotorOffsetClass('diff1vdeltaoffset', MotorDELTA_DIFF1.getPvName(), '%.6f');
    diff1vgammaoffset = EpicsMotorOffsetClass('diff1vgammaoffset', MotorGAMMA_DIFF1.getPvName(), '%.6f');
    diff1vomegaoffset = EpicsMotorOffsetClass('diff1vomegaoffset', MotorOMEGA_DIFF1.getPvName(), '%.6f');
    diff1homegaoffset = EpicsMotorOffsetClass('diff1homegaoffset', MotorTHETA_DIFF1.getPvName(), '%.6f');
    diff1chioffset = EpicsMotorOffsetClass('diff1chioffset', MotorCHI_DIFF1.getPvName(), '%.6f');
else :
    diff1vdeltaoffset = DummyScannable('diff1vdeltaoffset');
    diff1vgammaoffset = DummyScannable('diff1vgammaoffset');
    diff1vomegaoffset = DummyScannable('diff1vomegaoffset');
    diff1homegaoffset = DummyScannable('diff1homegaoffset');
    diff1chioffset = DummyScannable('diff1chioffset');

from gda.device.scannable import ScannableBase


class ScaledVirtualMotor(ScannableBase):
    """
    Wrapper for ScannableMotor which scales the value by a fixed (settable) amount and applies an (unscaled) offset.
    """

    def __init__(self, name, gda_motor):
        self.setName(name)
        self.setRealMotor(gda_motor)
        self.scale_factor = 1.0
        self.offset = 0.0

    def setRealMotor(self, motor):
        self.real_motor = motor

    def setScaleFactor(self, scale):
        self.scale_factor = float(scale)

    def getScaleFactor(self):
        return self.scale_factor

    def setOffset(self, new_offset):
        self.offset = new_offset

    def getOffset(self):
        return self.offset

    def zeroPosition(self):
        print("Offsetting thv so that the current position of the real motor is thv=zero.")
        self.setOffset(self.real_motor.getPosition())

    def rawAsynchronousMoveTo(self, posn):
        self.real_motor.rawAsynchronousMoveTo((posn / self.scale_factor) + self.offset)

    def getPosition(self):
        return (self.real_motor.getPosition() - self.offset) * self.scale_factor

    def isBusy(self):
        return self.real_motor.isBusy()

    def waitWhileBusy(self):
        self.real_motor.waitWhileBusy()

    def stop(self):
        self.real_motor.stop()

thv = ScaledVirtualMotor("thv", hex1rx)