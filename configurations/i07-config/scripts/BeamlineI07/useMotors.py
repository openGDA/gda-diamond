
from Diamond.PseudoDevices.EpicsMotors import EpicsMotorOffsetClass;

from gdaserver import MotorDELTA_DIFF1
from gdaserver import MotorGAMMA_DIFF1
from gdaserver import MotorOMEGA_DIFF1
from gdaserver import MotorTHETA_DIFF1
from gdaserver import MotorCHI_DIFF1

diff1vdeltaoffset = EpicsMotorOffsetClass('diff1vdeltaoffset', MotorDELTA_DIFF1.getPvName(), '%.6f');

diff1vgammaoffset = EpicsMotorOffsetClass('diff1vgammaoffset', MotorGAMMA_DIFF1.getPvName(), '%.6f');

diff1vomegaoffset = EpicsMotorOffsetClass('diff1vomegaoffset', MotorOMEGA_DIFF1.getPvName(), '%.6f');

diff1homegaoffset = EpicsMotorOffsetClass('diff1homegaoffset', MotorTHETA_DIFF1.getPvName(), '%.6f');

diff1chioffset = EpicsMotorOffsetClass('diff1chioffset', MotorCHI_DIFF1.getPvName(), '%.6f');

