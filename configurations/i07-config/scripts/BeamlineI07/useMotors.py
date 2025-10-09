
from Diamond.PseudoDevices.EpicsMotors import EpicsMotorOffsetClass;

from gdaserver import MotorDELTA_DIFF1, MotorGAMMA_DIFF1, MotorOMEGA_DIFF1, MotorTHETA_DIFF1, MotorCHI_DIFF1, hex1rx

if isLive():
    diff1vdeltaoffset = EpicsMotorOffsetClass('diff1vdeltaoffset', MotorDELTA_DIFF1.getPvName(), '%.6f');

    diff1vgammaoffset = EpicsMotorOffsetClass('diff1vgammaoffset', MotorGAMMA_DIFF1.getPvName(), '%.6f');

    diff1vomegaoffset = EpicsMotorOffsetClass('diff1vomegaoffset', MotorOMEGA_DIFF1.getPvName(), '%.6f');

    diff1homegaoffset = EpicsMotorOffsetClass('diff1homegaoffset', MotorTHETA_DIFF1.getPvName(), '%.6f');

    diff1chioffset = EpicsMotorOffsetClass('diff1chioffset', MotorCHI_DIFF1.getPvName(), '%.6f');

from gda.device.scannable import ScannableBase


class ScaledVirtualMotor(ScannableBase):
    """
    Wrapper for ScannableMotor which scales the value by a fixed (settable) amount.
    """

    def __init__(self, name, gda_motor):
        self.setName(name)
        self.setRealMotor(gda_motor)
        self.scale_factor = 1.0

    def rawAsynchronousMoveTo(self, posn):
        self.real_motor.rawAsynchronousMoveTo(posn / self.scale_factor)

    def setRealMotor(self, motor):
        self.real_motor = motor

    def setScaleFactor(self, scale):
        self.scale_factor = float(scale)

    def getScaleFactor(self):
        return self.scale_factor

    def getPosition(self):
        return self.real_motor.getPosition() * self.scale_factor

    def isBusy(self):
        return self.real_motor.isBusy()

    def waitWhileBusy(self):
        self.real_motor.waitWhileBusy()

    def stop(self):
        self.real_motor.stop()

thv = ScaledVirtualMotor("thv", hex1rx)