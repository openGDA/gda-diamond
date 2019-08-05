'''
Created on 1 Aug 2019

@author: fy65
'''
from epics.motor.positionCompareMotorClass import PositionCompareMotorClass
from future.singleEpicsPositionerNoStatusClassDeadbandOrStop import SingleEpicsPositionerNoStatusClassDeadbandOrStop
from utils.ExceptionLogs import localStation_exception
import sys
from gda.device.scannable.scannablegroup import ScannableGroup

try:
    m4_x = PositionCompareMotorClass("m4_x", "BL10I-OP-FOCS-01:X.VAL", "BL10I-OP-FOCS-01:X.RBV", "BL10I-OP-FOCS-01:X.STOP", 0.002, "mm", "%.3f")
    m4_y = PositionCompareMotorClass("m4_y", "BL10I-OP-FOCS-01:Y.VAL", "BL10I-OP-FOCS-01:Y.RBV", "BL10I-OP-FOCS-01:Y.STOP", 0.002, "mm", "%.3f")
    m4_z = PositionCompareMotorClass("m4_z", "BL10I-OP-FOCS-01:Z.VAL", "BL10I-OP-FOCS-01:Z.RBV", "BL10I-OP-FOCS-01:Z.STOP", 0.002, "mm", "%.3f")
    m4_yaw = PositionCompareMotorClass("m4_yaw", "BL10I-OP-FOCS-01:YAW.VAL", "BL10I-OP-FOCS-01:YAW.RBV", "BL10I-OP-FOCS-01:YAW.STOP", 0.002, "urad", "%.3f")
    m4_pitch = PositionCompareMotorClass("m4_pitch", "BL10I-OP-FOCS-01:PITCH.VAL", "BL10I-OP-FOCS-01:PITCH.RBV", "BL10I-OP-FOCS-01:PITCH.STOP", 0.002, "urad", "%.3f")
    m4_roll = PositionCompareMotorClass("m4_roll", "BL10I-OP-FOCS-01:ROLL.VAL", "BL10I-OP-FOCS-01:ROLL.RBV", "BL10I-OP-FOCS-01:ROLL.STOP", 0.002, "urad", "%.3f")
    m4fpitch = SingleEpicsPositionerNoStatusClassDeadbandOrStop('m4fpitch', 'BL10I-OP-FOCS-01:FPITCH:DMD:AO', 'BL10I-OP-FOCS-01:FPITCH:RBV:AI', 'V', '%.3f', 0.001)
    m4=ScannableGroup("m4", [m4_x, m4_y, m4_z, m4_yaw, m4_pitch, m4_roll, m4fpitch])
except:
    localStation_exception(sys.exc_info(), "initialising m4 hexapod and fpitch scannables")