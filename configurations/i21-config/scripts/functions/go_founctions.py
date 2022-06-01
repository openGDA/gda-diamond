'''
define go functions to move Insertion Device to given energy and polarisation

Created on May 6, 2022

@author: fy65
'''
from gdascripts.utils import caput
from calibration.energy_polarisation_instances import energypolarisation
from calibration.energy_polarisation_class import X_RAY_POLARISATIONS
import installation

LH,LV,CR,CL,LH3,LV3,LH5,LV5 = X_RAY_POLARISATIONS[:-2]
EPICS_FEEDBACK_PV = "BL21I-OP-MIRR-01:FBCTRL:MODE"

def goLH(en_val_std):
    ''' go to Linear Horizontal polarisation at the given energy
    '''
    go(en_val_std, LH)

def goLV(en_val_std):
    ''' go to Linear Vertical polarisation at the given energy
    '''
    go(en_val_std, LV)
    
def goCR(en_val_std):
    ''' go to Circular Right polarisation at the given energy
    '''
    go(en_val_std, CR)
    
def goCL(en_val_std):
    ''' go to Circular Left polarisation at the given energy
    '''
    go(en_val_std, CL)

def go(en_val_std, pol):
    ''' go to the given polarisation at the given energy
    '''
    from gdaserver import pgmEnergy  # @UnresolvedImport
    from time import sleep
    from utils.ScriptLogger import SinglePrint
    if not (pol in X_RAY_POLARISATIONS[:-2]):
        print("Requested polarisation %s is not supported" % pol)
        return
    if installation.isDummy():
        print("disable feedback: set %s to 0" % EPICS_FEEDBACK_PV)
    else:
        caput(EPICS_FEEDBACK_PV,0)
    while pgmEnergy.isBusy():
        SinglePrint.sprint("pgmEnergy is busy at the moment, wait for it to stop before move energy ...")
        sleep(1.0)
    print("move (energy, polarisation) to %r ..." % ([en_val_std, pol]))
    energypolarisation.moveTo([en_val_std, pol])
    if installation.isDummy():
        print("enable feedback: set %s to 4" % EPICS_FEEDBACK_PV)
    else:
        caput(EPICS_FEEDBACK_PV,4)
    print("energy is now at %f, polarisation is now at %s" % (en_val_std, pol))