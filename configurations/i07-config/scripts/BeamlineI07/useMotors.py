
from Diamond.PseudoDevices.EpicsMotors import EpicsMotorClass, EpicsCallbackMotorClass, EpicsMotorOffsetClass;

from gdaserver import MotorDELTA_DIFF1
from gdaserver import MotorGAMMA_DIFF1
from gdaserver import MotorOMEGA_DIFF1
from gdaserver import MotorALPHA_DIFF1
from gdaserver import MotorTHETA_DIFF1
from gdaserver import MotorCHI_DIFF1

#diff1delta = EpicsMotorClass('diff1delta',pvMotor, '%.6f');
diff1vdeltaoffset = EpicsMotorOffsetClass('diff1vdeltaoffset', MotorDELTA_DIFF1.getPvName(), '%.6f');
#diff1hgammaoffset = EpicsMotorOffsetClass('diff1hgammaoffset',pvMotor, '%.6f');

diff1vgammaoffset = EpicsMotorOffsetClass('diff1vgammaoffset', MotorGAMMA_DIFF1.getPvName(), '%.6f');
#diff1hdeltaoffset = EpicsMotorOffsetClass('diff1hdeltaoffset',pvMotor, '%.6f');

diff1vomegaoffset = EpicsMotorOffsetClass('diff1vomegaoffset', MotorOMEGA_DIFF1.getPvName(), '%.6f');

diff1valphaoffset = EpicsMotorOffsetClass('diff1valphaoffset', MotorALPHA_DIFF1.getPvName(), '%.6f');

diff1homegaoffset = EpicsMotorOffsetClass('diff1homegaoffset', MotorTHETA_DIFF1.getPvName(), '%.6f');

diff1halphaoffset = EpicsMotorOffsetClass('diff1halphaoffset', MotorCHI_DIFF1.getPvName(), '%.6f');

