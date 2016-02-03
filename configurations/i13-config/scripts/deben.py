
from positionCompareMotorClass import PositionCompareMotorClass

#def __init__(self, name, pvinstring, pvoutstring, pvstopstring, tolerance, unitstring, formatstring):

print "adding deben objects and methods"

dbn_pv_prefix = "BL13I-EA-DOF-01:RIG:"

dbn_rot = PositionCompareMotorClass(    "dbn_rot",	\
                                        dbn_pv_prefix+"TOP:MOTOR.VAL", dbn_pv_prefix+"TOP:MOTOR.RBV", dbn_pv_prefix+"TOP:MOTOR.STOP", \
                                        tolerance=0.002, unitstring="deg", formatstring="%.3f", wait_sec=1)
dbn_rott = PositionCompareMotorClass(   "dbn_rott", \
                                        dbn_pv_prefix+"TOP:MOTOR.VAL", dbn_pv_prefix+"TOP:MOTOR.RBV", dbn_pv_prefix+"TOP:MOTOR.STOP", \
                                        tolerance=0.002, unitstring="deg", formatstring="%.3f", wait_sec=1)
dbn_rotb = PositionCompareMotorClass(   "dbn_rotb", \
                                        dbn_pv_prefix+"BOT:MOTOR.VAL", dbn_pv_prefix+"BOT:MOTOR.RBV", dbn_pv_prefix+"BOT:MOTOR.STOP", \
                                        tolerance=0.002, unitstring="deg", formatstring="%.3f", wait_sec=1)
dbn_y = PositionCompareMotorClass(      "dbn_y", \
                                        dbn_pv_prefix+"LIN:MOTOR.VAL", dbn_pv_prefix+"LIN:MOTOR.RBV", dbn_pv_prefix+"LIN:MOTOR.STOP", \
                                        tolerance=0.002, unitstring="mm", formatstring="%.3f", wait_sec=1)


def deben_configure():
    dbn_rot.configureAll()
    dbn_rott.configureAll()
    dbn_rotb.configureAll()
    dbn_y.configureAll()
    
def deben_clearup():
    dbn_rot.clearupAll()
    dbn_rott.clearupAll()
    dbn_rotb.clearupAll()
    dbn_y.clearupAll()
