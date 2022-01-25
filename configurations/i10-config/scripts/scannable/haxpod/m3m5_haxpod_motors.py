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
        m3m5_x = PositionCompareMotorClass("m3m5_x", "BL10I-OP-SWTCH-01:X.VAL", "BL10I-OP-SWTCH-01:X.RBV", "BL10I-OP-SWTCH-01:X.STOP", 0.002, "mm", "%.3f")
        m3m5_y = PositionCompareMotorClass("m3m5_y", "BL10I-OP-SWTCH-01:Y.VAL", "BL10I-OP-SWTCH-01:Y.RBV", "BL10I-OP-SWTCH-01:Y.STOP", 0.002, "mm", "%.3f")
        m3m5_z = PositionCompareMotorClass("m3m5_z", "BL10I-OP-SWTCH-01:Z.VAL", "BL10I-OP-SWTCH-01:Z.RBV", "BL10I-OP-SWTCH-01:Z.STOP", 0.002, "mm", "%.3f")
        m3m5_yaw = PositionCompareMotorClass("m3m5_yaw", "BL10I-OP-SWTCH-01:YAW.VAL", "BL10I-OP-SWTCH-01:YAW.RBV", "BL10I-OP-SWTCH-01:YAW.STOP", 0.002, "urad", "%.3f")
        m3m5_pitch = PositionCompareMotorClass("m3m5_pitch", "BL10I-OP-SWTCH-01:PITCH.VAL", "BL10I-OP-SWTCH-01:PITCH.RBV", "BL10I-OP-SWTCH-01:PITCH.STOP", 0.002, "urad", "%.3f")
        m3m5_roll = PositionCompareMotorClass("m3m5_roll", "BL10I-OP-SWTCH-01:ROLL.VAL", "BL10I-OP-SWTCH-01:ROLL.RBV", "BL10I-OP-SWTCH-01:ROLL.STOP", 0.002, "urad", "%.3f")
        m3m5fpitch = SingleEpicsPositionerNoStatusClassDeadbandOrStop('m3m5fpitch', 'BL10I-OP-SWTCH-01:FPITCH:DMD:AO', 'BL10I-OP-SWTCH-01:FPITCH:RBV:AI', 'V', '%.3f', 0.1)
        M3M5=ScannableGroup("M3M5", [m3m5_x, m3m5_y, m3m5_z, m3m5_yaw, m3m5_pitch, m3m5_roll, m3m5fpitch])
    except:
        localStation_exception(sys.exc_info(), "initialising m3m5 hexapod and fpitch scannables")
else:
        # other objects are defined by Spring beans
    m3m5fpitch = DummyEpicsReadWritePVClass('m3m5fpitch', 0.0, 5.0, 'V', '%.3f')
    