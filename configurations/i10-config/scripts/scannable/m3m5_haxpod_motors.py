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
    m3m5_x = PositionCompareMotorClass("m3m5_x", "BL10I-OP-SWTCH-01:X.VAL", "BL10I-OP-SWTCH-01:X.RBV", "BL10I-OP-SWTCH-01:X.STOP", 0.002, "mm", "%.3f")
    m3m5_y = PositionCompareMotorClass("m3m5_y", "BL10I-OP-SWTCH-01:Y.VAL", "BL10I-OP-SWTCH-01:Y.RBV", "BL10I-OP-SWTCH-01:Y.STOP", 0.002, "mm", "%.3f")
    m3m5_z = PositionCompareMotorClass("m3m5_z", "BL10I-OP-SWTCH-01:Z.VAL", "BL10I-OP-SWTCH-01:Z.RBV", "BL10I-OP-SWTCH-01:Z.STOP", 0.002, "mm", "%.3f")
    m3m5_yaw = PositionCompareMotorClass("m3m5_yaw", "BL10I-OP-SWTCH-01:YAW.VAL", "BL10I-OP-SWTCH-01:YAW.RBV", "BL10I-OP-SWTCH-01:YAW.STOP", 0.002, "urad", "%.3f")
    m3m5_pitch = PositionCompareMotorClass("m3m5_pitch", "BL10I-OP-SWTCH-01:PITCH.VAL", "BL10I-OP-SWTCH-01:PITCH.RBV", "BL10I-OP-SWTCH-01:PITCH.STOP", 0.002, "urad", "%.3f")
    m3m5_roll = PositionCompareMotorClass("m3m5_roll", "BL10I-OP-SWTCH-01:ROLL.VAL", "BL10I-OP-SWTCH-01:ROLL.RBV", "BL10I-OP-SWTCH-01:ROLL.STOP", 0.002, "urad", "%.3f")
    m3m5fpitch = SingleEpicsPositionerNoStatusClassDeadbandOrStop('m3m5fpitch', 'BL10I-OP-SWTCH-01:FPITCH:DMD:AO', 'BL10I-OP-SWTCH-01:FPITCH:RBV:AI', 'V', '%.3f', 0.001)
    m3m5=ScannableGroup("m3m5", [m3m5_x, m3m5_y, m3m5_z, m3m5_yaw, m3m5_pitch, m3m5_roll, m3m5fpitch])
except:
    localStation_exception(sys.exc_info(), "initialising m3m5 hexapod and fpitch scannables")