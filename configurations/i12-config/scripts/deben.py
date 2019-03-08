from epics_scripts.pv_scannable_utils import caput
from i13positionCompareMotorClass import PositionCompareMotorClass
from epics_scripts.pv_scannable_utils import createPVScannable

#def __init__(self, name, pvinstring, pvoutstring, pvstopstring, tolerance, unitstring, formatstring):

print "adding deben objects and methods"

dbn_pv_prefix = "BL12I-EA-DOF-01:RIG:"	# beamline specific

dbn_rot = PositionCompareMotorClass(    "dbn_rot",\
                                        dbn_pv_prefix+"BOT:MOTOR.VAL", dbn_pv_prefix+"BOT:MOTOR.RBV", dbn_pv_prefix+"BOT:MOTOR.STOP",\
                                        tolerance=0.002, unitstring="deg", formatstring="%.3f", wait_sec=1)
dbn_rott = PositionCompareMotorClass(   "dbn_rott",\
                                        dbn_pv_prefix+"TOP:MOTOR.VAL", dbn_pv_prefix+"TOP:MOTOR.RBV", dbn_pv_prefix+"TOP:MOTOR.STOP",\
                                        tolerance=0.002, unitstring="deg", formatstring="%.3f", wait_sec=1)
dbn_rotb = PositionCompareMotorClass(   "dbn_rotb",\
                                        dbn_pv_prefix+"BOT:MOTOR.VAL", dbn_pv_prefix+"BOT:MOTOR.RBV", dbn_pv_prefix+"BOT:MOTOR.STOP",\
                                        tolerance=0.002, unitstring="deg", formatstring="%.3f", wait_sec=1)
dbn_y = PositionCompareMotorClass(      "dbn_y",\
                                        dbn_pv_prefix+"LIN:MOTOR.VAL", dbn_pv_prefix+"LIN:MOTOR.RBV", dbn_pv_prefix+"LIN:MOTOR.STOP",\
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

from time import sleep
def deben_hysteresis_test(n, frm, step, wait_sec=1):
    fname = deben_hysteresis_test.__name__
    stage = dbn_rotb
    pos_lst = [frm + i*step for i in range(n)]
    print("len(pos_lst) = %d" %(len(pos_lst)))
    for i,p in enumerate(pos_lst):
        print("pt i = %d" %(i))
        stage.moveTo(p)
        sleep(wait_sec)
    
    print("Reverse walk...")
    for i,p in enumerate(reversed(pos_lst)):
        print("pt i = %d" %(i))
        stage.moveTo(p)
        sleep(wait_sec)
        
    print("Finished %s!" %(fname))



