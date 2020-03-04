
from Diamond.PseudoDevices.EpicsMotors import EpicsMotorClass, EpicsCallbackMotorClass, EpicsMotorOffsetClass;

pvMotor = "BL07I-MO-DIFF-01:DELTA"
#diff1delta = EpicsMotorClass('diff1delta',pvMotor, '%.6f');
diff1vdeltaoffset = EpicsMotorOffsetClass('diff1vdeltaoffset',pvMotor, '%.6f');
#diff1hgammaoffset = EpicsMotorOffsetClass('diff1hgammaoffset',pvMotor, '%.6f');

pvMotor = "BL07I-MO-DIFF-01:GAMMA"
diff1vgammaoffset = EpicsMotorOffsetClass('diff1vgammaoffset',pvMotor, '%.6f');
#diff1hdeltaoffset = EpicsMotorOffsetClass('diff1hdeltaoffset',pvMotor, '%.6f');

pvMotor = "BL07I-MO-DIFF-01:OMEGA"
diff1vomegaoffset = EpicsMotorOffsetClass('diff1vomegaoffset',pvMotor, '%.6f');

pvMotor = "BL07I-MO-DIFF-01:ALPHA"
diff1valphaoffset = EpicsMotorOffsetClass('diff1valphaoffset',pvMotor, '%.6f');

pvMotor = "BL07I-MO-DIFF-03:THETA"
diff1homegaoffset = EpicsMotorOffsetClass('diff1homegaoffset',pvMotor, '%.6f');

pvMotor = "BL07I-MO-DIFF-01:CHI"
diff1halphaoffset = EpicsMotorOffsetClass('diff1halphaoffset',pvMotor, '%.6f');

