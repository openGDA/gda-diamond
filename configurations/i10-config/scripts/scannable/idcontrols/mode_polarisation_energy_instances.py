'''
Created on 9 May 2018

@author: fy65
'''
from scannable.idcontrols.sourceModes import SourceMode
from gdaserver import idd_gap, idu_gap,idu_rowphase1,idu_rowphase2,idu_rowphase3, idd_rowphase1, idd_rowphase2, idd_rowphase3  # @UnresolvedImport
from scannable.idcontrols.polarisation import Polarisation
import math

print
print "-"*100
print "Creating X-ray source control and polarisation control:"
print "    1. 'smode' - a scannable to set and get current X-ray source mode, i.e. which ID is used, it disables the ID not used;"
print "    2. 'pol'   - a scannable to set and get current polarisation of the X-ray beam. GDA value only which is not applied to hardware!"
smode=SourceMode('smode',idu_gap, idd_gap, opengap=200, defaultmode=None)
pol=Polarisation('pol', smode, defaultPolarisation=None); pol.verbose=True

GAP_LIMIT=99.0
RAW_PHASE_MOTOR_TOLERANCE=1.0
ENERGY_VALUE_TOLERANCE=10.0
def initialisation():
    if float(idd_gap.getPosition()) < GAP_LIMIT and float(idu_gap.getPosition()) < GAP_LIMIT:
        #I10 does not handle this case
        smode.mode=SourceMode.SOURCE_MODES[2]
    elif float(idd_gap.getPosition()) > GAP_LIMIT and float(idu_gap.getPosition()) < GAP_LIMIT:
        #using IDU
        smode.mode=SourceMode.SOURCE_MODES[1]
        if (float(idu_rowphase1.getPosition()) > 0.0) and math.fabs(float(idu_rowphase2.getPosition())-0.0)<= RAW_PHASE_MOTOR_TOLERANCE:
            pol.asynchronousMoveTo('pc')
        elif (float(idu_rowphase1.getPosition()) < 0.0) and math.fabs(float(idu_rowphase2.getPosition()) - 0.0) <= RAW_PHASE_MOTOR_TOLERANCE:
            pol.asynchronousMoveTo('nc')
        elif math.fabs(float(idu_rowphase1.getPosition()) - 0.0) <= RAW_PHASE_MOTOR_TOLERANCE and math.fabs(float(idu_rowphase2.getPosition()) - 0.0) <= RAW_PHASE_MOTOR_TOLERANCE:
            pol.asynchronousMoveTo('lh')
        elif math.fabs(float(idu_rowphase1.getPosition()) - 24.0) <= RAW_PHASE_MOTOR_TOLERANCE and math.fabs(float(idu_rowphase2.getPosition()) - 0.0) <= RAW_PHASE_MOTOR_TOLERANCE:
            pol.asynchronousMoveTo('lv')
        elif math.fabs(float(idu_rowphase1.getPosition()) + float(idu_rowphase3.getPosition())) <= RAW_PHASE_MOTOR_TOLERANCE and math.fabs(float(idu_rowphase2.getPosition()) - 0.0) <= RAW_PHASE_MOTOR_TOLERANCE:
            pol.asynchronousMoveTo('la')
        else:
            pol.polarisation=Polarisation.POLARISATIONS[6]
    elif float(idd_gap.getPosition()) < GAP_LIMIT and float(idu_gap.getPosition()) > GAP_LIMIT:
        #using IDD
        smode.mode=SourceMode.SOURCE_MODES[0]
        if (float(idd_rowphase1.getPosition()) > 0.0) and math.fabs(float(idd_rowphase2.getPosition())-0.0)<= RAW_PHASE_MOTOR_TOLERANCE:
            pol.asynchronousMoveTo('pc')
        elif (float(idd_rowphase1.getPosition()) < 0.0) and math.fabs(float(idd_rowphase2.getPosition()) - 0.0) <= RAW_PHASE_MOTOR_TOLERANCE:
            pol.asynchronousMoveTo('nc')
        elif math.fabs(float(idd_rowphase1.getPosition()) - 0.0) <= RAW_PHASE_MOTOR_TOLERANCE and math.fabs(float(idd_rowphase2.getPosition()) - 0.0) <= RAW_PHASE_MOTOR_TOLERANCE:
            pol.asynchronousMoveTo('lh')
        elif math.fabs(float(idd_rowphase1.getPosition()) - 24.0) <= RAW_PHASE_MOTOR_TOLERANCE and math.fabs(float(idd_rowphase2.getPosition()) - 0.0) <= RAW_PHASE_MOTOR_TOLERANCE:
            pol.asynchronousMoveTo('lv')
        elif math.fabs(float(idd_rowphase1.getPosition()) + float(idd_rowphase3.getPosition())) <= RAW_PHASE_MOTOR_TOLERANCE and math.fabs(float(idd_rowphase2.getPosition()) - 0.0) <= RAW_PHASE_MOTOR_TOLERANCE :
            pol.asynchronousMoveTo('la')
        else:
            pol.polarisation=Polarisation.POLARISATIONS[6]
    else:
        smode.mode=SourceMode.SOURCE_MODES[2]