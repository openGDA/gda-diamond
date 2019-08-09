from epics_scripts.pv_scannable_utils import caput, caget
from positionCompareMotorClass import PositionCompareMotorClass
from epics_scripts.pv_scannable_utils import createPVScannable

#def __init__(self, name, pvinstring, pvoutstring, pvstopstring, tolerance, unitstring, formatstring):

print("\n Adding Deben objects and methods...")

dbn_pv_prefix = "BL13I-EA-DOF-01:RIG:"

dbn_rot = PositionCompareMotorClass(    "dbn_rot",	\
                                        dbn_pv_prefix+"BOT:MOTOR.VAL", dbn_pv_prefix+"BOT:MOTOR.RBV", dbn_pv_prefix+"BOT:MOTOR.STOP", \
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

def deben_after_ioc_restart():
    fname = deben_after_ioc_restart.__name__
    try:
        # bottom rot stage
        caput(dbn_pv_prefix+"BOT:MOTOR.VBAS", 0.0)
        caput(dbn_pv_prefix+"BOT:MOTOR.ERES", -0.001)
        
        # top rot stage
        caput(dbn_pv_prefix+"TOP:MOTOR.VBAS", 0.0)
        caput(dbn_pv_prefix+"TOP:MOTOR.ERES", -0.001)
    except Exception, e:
        print("Error in %s: %s" %(fname, str(e)))
    

    dbn_tension_rbv = createPVScannable("dbn_tension_rbv", dbn_pv_prefix+"TENSIONFORCE")
    dbn_torsion_rbv = createPVScannable("dbn_torsion_rbv", dbn_pv_prefix+"TORSIONFORCE")

