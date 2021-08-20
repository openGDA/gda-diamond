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
        m1_x = PositionCompareMotorClass("m1_x", "BL10I-OP-COL-01:X.VAL", "BL10I-OP-COL-01:X.RBV", "BL10I-OP-COL-01:X.STOP", 0.002, "mm", "%.3f")
        m1_y = PositionCompareMotorClass("m1_y", "BL10I-OP-COL-01:Y.VAL", "BL10I-OP-COL-01:Y.RBV", "BL10I-OP-COL-01:Y.STOP", 0.002, "mm", "%.3f")
        m1_z = PositionCompareMotorClass("m1_z", "BL10I-OP-COL-01:Z.VAL", "BL10I-OP-COL-01:Z.RBV", "BL10I-OP-COL-01:Z.STOP", 0.002, "mm", "%.3f")
        m1_yaw = PositionCompareMotorClass("m1_yaw", "BL10I-OP-COL-01:YAW.VAL", "BL10I-OP-COL-01:YAW.RBV", "BL10I-OP-COL-01:YAW.STOP", 0.002, "urad", "%.3f")
        m1_pitch = PositionCompareMotorClass("m1_pitch", "BL10I-OP-COL-01:PITCH.VAL", "BL10I-OP-COL-01:PITCH.RBV", "BL10I-OP-COL-01:PITCH.STOP", 0.002, "urad", "%.3f")
        m1_roll = PositionCompareMotorClass("m1_roll", "BL10I-OP-COL-01:ROLL.VAL", "BL10I-OP-COL-01:ROLL.RBV", "BL10I-OP-COL-01:ROLL.STOP", 0.002, "urad", "%.3f")
        m1fpitch = SingleEpicsPositionerNoStatusClassDeadbandOrStop('m1fpitch', 'BL10I-OP-COL-01:FPITCH:DMD:AO', 'BL10I-OP-COL-01:FPITCH:RBV:AI', 'V', '%.3f', 0.001)
        M1=ScannableGroup("M1", [m1_x, m1_y, m1_z, m1_yaw, m1_pitch, m1_roll, m1fpitch])
    except:
        localStation_exception(sys.exc_info(), "initialising m1 hexapod and fpitch scannables")
else:
    # other objects are defined by Spring beans
    m1fpitch = DummyEpicsReadWritePVClass('m1fpitch', 5.0, 'V', '%.3f')
    