'''
Created on 21 Apr 2017

@author: fy65
'''

from i06shared.scannables.sourceModes import SourceMode
from i06shared.scannables.polarisation import Polarisation
from i06shared.scannables.energy import CombinedEnergy
from i06shared.scannables.linearArbitraryAngle import LinearArbitraryAngle
from i06shared.scannables.offsetHarmonic import HarmonicOffset
import __main__  # @UnresolvedImport
from i06shared import installation
import math
from gda.configuration.properties import LocalProperties
from i06shared.scannables.dummyListScannable import DummyListScannable
from gda.device.scannable import DummyScannable

GAP_LIMIT=99.0
RAW_PHASE_MOTOR_TOLERANCE=1.0
ENERGY_VALUE_TOLERANCE=10.0
idd,idu,dpu,dmu,unknown=SourceMode.SOURCE_MODES
pc,nc,lh,lv,la,unknown=Polarisation.POLARISATIONS

def initialisation():
    if float(__main__.iddgap.getPosition()) < GAP_LIMIT and float(__main__.idugap.getPosition()) < GAP_LIMIT:
        if math.fabs(float(__main__.iddrpenergy.getPosition()) - float(__main__.idurpenergy.getPosition())) <= ENERGY_VALUE_TOLERANCE:
            __main__.smode.mode=SourceMode.SOURCE_MODES[2]
            if math.fabs(float(__main__.iddtrp.getPosition()) - 0.0) <= RAW_PHASE_MOTOR_TOLERANCE and math.fabs(float(__main__.idutrp.getPosition()) - 0.0) <= RAW_PHASE_MOTOR_TOLERANCE:
                __main__.pol.polarisation=Polarisation.POLARISATIONS[2]
            elif math.fabs(float(__main__.iddtrp.getPosition()) - 32.0) <= RAW_PHASE_MOTOR_TOLERANCE and math.fabs(float(__main__.idutrp.getPosition()) - 32.0) <= RAW_PHASE_MOTOR_TOLERANCE:
                __main__.pol.polarisation=Polarisation.POLARISATIONS[3]
            elif math.fabs(float(__main__.iddtrp.getPosition()) - 22.0) <= RAW_PHASE_MOTOR_TOLERANCE and math.fabs(float(__main__.idutrp.getPosition()) - 22.0) <= RAW_PHASE_MOTOR_TOLERANCE:
                __main__.pol.polarisation=Polarisation.POLARISATIONS[0]
            elif math.fabs(float(__main__.iddtrp.getPosition()) + 22.0) <= RAW_PHASE_MOTOR_TOLERANCE and math.fabs(float(__main__.idutrp.getPosition()) + 22.0) <= RAW_PHASE_MOTOR_TOLERANCE:
                __main__.pol.polarisation=Polarisation.POLARISATIONS[1]
            elif math.fabs(float(__main__.iddtrp.getPosition()) - float(__main__.iddbrp.getPosition())*(-1.0)) <= RAW_PHASE_MOTOR_TOLERANCE and math.fabs(float(__main__.idutrp.getPosition()) - float(__main__.idubrp.getPosition())*(-1.0)) <= RAW_PHASE_MOTOR_TOLERANCE:
                __main__.pol.polarisation=Polarisation.POLARISATIONS[4]
            else:
                __main__.pol.polarisation=Polarisation.POLARISATIONS[5]
        else:
            __main__.smode.mode=SourceMode.SOURCE_MODES[3]
            if math.fabs(float(__main__.iddtrp.getPosition()) - 0.0) <= RAW_PHASE_MOTOR_TOLERANCE:
                if math.fabs(float(__main__.iddrpenergy.getPosition()) - (float(__main__.pgmenergy.getPosition())+float(__main__.offhar.getPosition()))) <= ENERGY_VALUE_TOLERANCE:
                    __main__.pol.polarisation=Polarisation.POLARISATIONS[2]
                elif math.fabs(float(__main__.idurpenergy.getPosition()) - (float(__main__.pgmenergy.getPosition())+float(__main__.offhar.getPosition()))) <= ENERGY_VALUE_TOLERANCE:
                    __main__.pol.polarisation=Polarisation.POLARISATIONS[3]
                else:
                    __main__.pol.polarisation=Polarisation.POLARISATIONS[5]  
            elif math.fabs(float(__main__.iddtrp.getPosition()) - 22.0) <= RAW_PHASE_MOTOR_TOLERANCE:
                if math.fabs(float(__main__.iddrpenergy.getPosition()) - (float(__main__.pgmenergy.getPosition())+float(__main__.offhar.getPosition()))) <= ENERGY_VALUE_TOLERANCE:
                    __main__.pol.polarisation=Polarisation.POLARISATIONS[0]
                elif math.fabs(float(__main__.idurpenergy.getPosition()) - (float(__main__.pgmenergy.getPosition())+float(__main__.offhar.getPosition()))) <= ENERGY_VALUE_TOLERANCE:
                    __main__.pol.polarisation=Polarisation.POLARISATIONS[1]
                else:
                    __main__.pol.polarisation=Polarisation.POLARISATIONS[5]   
            else:
                __main__.pol.polarisation=Polarisation.POLARISATIONS[5]  
            
    elif float(__main__.iddgap.getPosition()) > GAP_LIMIT and float(__main__.idugap.getPosition()) < GAP_LIMIT:
        __main__.smode.mode=SourceMode.SOURCE_MODES[1]
        if math.fabs(float(__main__.idutrp.getPosition()) - 0.0) <= RAW_PHASE_MOTOR_TOLERANCE:
            __main__.pol.polarisation=Polarisation.POLARISATIONS[2]
        elif math.fabs(float(__main__.idutrp.getPosition()) - 32.0) <= RAW_PHASE_MOTOR_TOLERANCE:
            __main__.pol.polarisation=Polarisation.POLARISATIONS[3]
        elif math.fabs(float(__main__.idutrp.getPosition()) - 22.0) <= RAW_PHASE_MOTOR_TOLERANCE:
            __main__.pol.polarisation=Polarisation.POLARISATIONS[0]
        elif math.fabs(float(__main__.idutrp.getPosition()) + 22.0) <= RAW_PHASE_MOTOR_TOLERANCE:
            __main__.pol.polarisation=Polarisation.POLARISATIONS[1]
        elif math.fabs(float(__main__.idutrp.getPosition()) - float(__main__.idubrp.getPosition())*(-1.0)) <= RAW_PHASE_MOTOR_TOLERANCE:
            __main__.pol.polarisation=Polarisation.POLARISATIONS[4]
        else:
            __main__.pol.polarisation=Polarisation.POLARISATIONS[5]
    elif float(__main__.iddgap.getPosition()) < GAP_LIMIT and float(__main__.idugap.getPosition()) > GAP_LIMIT:
        __main__.smode.mode=SourceMode.SOURCE_MODES[0]
        if math.fabs(float(__main__.iddtrp.getPosition()) - 0.0) <= RAW_PHASE_MOTOR_TOLERANCE:
            __main__.pol.polarisation=Polarisation.POLARISATIONS[2]
        elif math.fabs(float(__main__.iddtrp.getPosition()) - 32.0) <= RAW_PHASE_MOTOR_TOLERANCE:
            __main__.pol.polarisation=Polarisation.POLARISATIONS[3]
        elif math.fabs(float(__main__.iddtrp.getPosition()) - 22.0) <= RAW_PHASE_MOTOR_TOLERANCE:
            __main__.pol.polarisation=Polarisation.POLARISATIONS[0]
        elif math.fabs(float(__main__.iddtrp.getPosition()) + 22.0) <= RAW_PHASE_MOTOR_TOLERANCE:
            __main__.pol.polarisation=Polarisation.POLARISATIONS[1]
        elif math.fabs(float(__main__.iddtrp.getPosition()) - float(__main__.iddbrp.getPosition())*(-1.0)) <= RAW_PHASE_MOTOR_TOLERANCE:
            __main__.pol.polarisation=Polarisation.POLARISATIONS[4]
        else:
            __main__.pol.polarisation=Polarisation.POLARISATIONS[5]
    else:
        __main__.smode.mode=SourceMode.SOURCE_MODES[4]

beamline = LocalProperties.get(LocalProperties.GDA_BEAMLINE_NAME)

if installation.isLive() and beamline != "lab44":
    __main__.smode=SourceMode('smode', defaultmode=SourceMode.SOURCE_MODES[4])
    __main__.offhar=HarmonicOffset('offhar', __main__.smode, __main__.iddpol, __main__.idupol,__main__.iddrpenergy,__main__.idurpenergy, __main__.pgmenergy, offhar=0.0)
    __main__.pol=Polarisation('pol', __main__.iddpol, __main__.iddrpenergy, __main__.iddgap, __main__.idupol, __main__.idurpenergy, __main__.idugap, __main__.pgmenergy, __main__.smode,__main__.offhar, detune=100.0, opengap=100.0,defaultPolarisation=Polarisation.POLARISATIONS[5])
    initialisation()
    __main__.energy=CombinedEnergy('energy', __main__.iddgap, __main__.idugap, __main__.iddrpenergy, __main__.idurpenergy, __main__.pgmenergy, __main__.smode, __main__.pol,__main__.offhar, detune=100.0, opengap=100.0)
    __main__.laa=LinearArbitraryAngle('laa', __main__.iddlaangle, __main__.idulaangle, __main__.smode, __main__.pol)
    __main__.offhar.setPolScannable(__main__.pol)
else:
    __main__.smode = DummyListScannable('smode', list_values=SourceMode.SOURCE_MODES[:-1])
    __main__.offhar = DummyScannable('offhar')
    __main__.pol = DummyListScannable('pol', list_values=Polarisation.POLARISATIONS[:-1])
    __main__.energy=__main__.pgmenergy
    __main__.laa=LinearArbitraryAngle('laa', __main__.iddlaangle, __main__.idulaangle, __main__.smode, __main__.pol)
    
