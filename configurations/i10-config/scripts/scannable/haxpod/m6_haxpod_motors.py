'''
I10 Haxpod motors for mirror callback earlier before it reaches the target in Java EpicsMotor. These instances are created using position compare to work around the problem.

Created on 1 Aug 2019
add dummy on 19/08/2021 for nxmetadata support

@author: fy65
'''
from epics.motor.positionCompareMotorClass import PositionCompareMotorClass
from future.singleEpicsPositionerNoStatusClassDeadbandOrStop import SingleEpicsPositionerNoStatusClassDeadbandOrStop
from utils.ExceptionLogs import localStation_exception
import sys
from gda.device.scannable.scannablegroup import ScannableGroup
import installation
from gdascripts.pd.dummy_pds import DummyEpicsReadWritePVClass

if installation.isLive():
    try:
        m6_x = PositionCompareMotorClass("m6_x", "BBL10J-OP-FOCA-01:X.VAL", "BL10J-OP-FOCA-01:X.RBV", "BL10J-OP-FOCA-01:X.STOP", 0.002, "mm", "%.3f")
        m6_y = PositionCompareMotorClass("m6_y", "BL10J-OP-FOCA-01:Y.VAL", "BL10J-OP-FOCA-01:Y.RBV", "BL10J-OP-FOCA-01:Y.STOP", 0.002, "mm", "%.3f")
        m6_z = PositionCompareMotorClass("m6_z", "BL10J-OP-FOCA-01:Z.VAL", "BL10J-OP-FOCA-01:Z.RBV", "BL10J-OP-FOCA-01:Z.STOP", 0.002, "mm", "%.3f")
        m6_yaw = PositionCompareMotorClass("m6_yaw", "BL10J-OP-FOCA-01:YAW.VAL", "BL10J-OP-FOCA-01:YAW.RBV", "BL10J-OP-FOCA-01:YAW.STOP", 0.002, "urad", "%.3f")
        m6_pitch = PositionCompareMotorClass("m6_pitch", "BL10J-OP-FOCA-01:PITCH.VAL", "BL10J-OP-FOCA-01:PITCH.RBV", "BL10J-OP-FOCA-01:PITCH.STOP", 0.002, "urad", "%.3f")
        m6_roll = PositionCompareMotorClass("m6_roll", "BL10J-OP-FOCA-01:ROLL.VAL", "BL10J-OP-FOCA-01:ROLL.RBV", "BL10J-OP-FOCA-01:ROLL.STOP", 0.002, "urad", "%.3f")
        m6fpitch = SingleEpicsPositionerNoStatusClassDeadbandOrStop('m6fpitch', 'BL10J-OP-FOCA-01:FPITCH:DMD:AO', 'BL10J-OP-FOCA-01:FPITCH:RBV:AI', 'V', '%.3f', 0.1)
        M6=ScannableGroup("M6", [m6_x, m6_y, m6_z, m6_yaw, m6_pitch, m6_roll, m6fpitch])
    except:
        localStation_exception(sys.exc_info(), "initialising m6 hexapod and fpitch scannables")
else:
        # other objects are defined by Spring beans
    m6fpitch = DummyEpicsReadWritePVClass('m6fpitch', 0.0, 5.0, 'V', '%.3f')
    