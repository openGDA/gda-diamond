'''
create scannables for X-ray source control, polarisation control, and energy control and 
create methods for initialisation of these scannables and control of beam harmonics order

Created on 9 May 2018

@author: fy65
'''
from calibrations.xraysource import SourceMode, X_RAY_SOURCE_MODES
from gdaserver import pgm_energy, idd_gap, idu_gap,idu_rowphase1,idu_rowphase2,idu_rowphase3,idu_rowphase4, idu_jawphase, idd_rowphase1,idd_rowphase2,idd_rowphase3,idd_rowphase4,idd_jawphase # @UnresolvedImport
from calibrations.energy_polarisation_class import BeamEnergyPolarisationClass,\
    X_RAY_POLARISATIONS
import installation
from scannable.dummyListScannable import DummyListScannable
from calibrations.linearArbitraryAngle import LinearArbitraryAngle
from Diamond.Poly import Poly
from calibrations.energy_Offset import energy_offset
    
print()
print("-"*100)
print("Creating X-ray source control, polarisation control, and energy control scannables:")
print("    1. 'smode'      - a scannable to set and get X-ray source mode, i.e. which ID is used, it disables the ID not used;")
print("    2. 'pol'        - a scannable to set and get polarisation of the X-ray beam.")
print("    3. 'energy_s'   - a scannable to set and get energy of the X-ray beam. It cannot be used for cvscan!")
print("    4. 'energy_pol' - a scannable to set and get both energy and polarisation of the X-ray beam at the same time concurrently!")

idd_controls = {"gap":idd_gap,"rowphase1":idd_rowphase1, "rowphase2":idd_rowphase2, "rowphase3":idd_rowphase3, "rowphase4":idd_rowphase4, "jawphase":idd_jawphase}
idu_controls = {"gap":idu_gap,"rowphase1":idu_rowphase1, "rowphase2":idu_rowphase2, "rowphase3":idu_rowphase3, "rowphase4":idu_rowphase4, "jawphase":idu_jawphase}
ID_ENERGY_TO_GAP_CALIBRATION_FILE = "IDEnergy2GapCalibrations.csv"
ID_ENERGY_TO_PHASE_CALIBRATION_FILE = "IDEnergy2PhaseCalibrations.csv"

GAP_LIMIT=99.0

def setBeamHarmonicsOrder(n):
    pol.setHarmonicsOrder(n)
    energy_s.setHarmonicsOrder(n)
     
def initialisation():
    if float(idd_gap.getPosition()) < GAP_LIMIT and float(idu_gap.getPosition()) < GAP_LIMIT:
        #I10 does not handle this case
        smode.mode=X_RAY_SOURCE_MODES[2]
    elif float(idd_gap.getPosition()) > GAP_LIMIT and float(idu_gap.getPosition()) < GAP_LIMIT:
        #using IDU
        smode.mode=X_RAY_SOURCE_MODES[1]
        pol.polarisation = pol.determinePhaseFromHardware(idu_controls)[0]
    elif float(idd_gap.getPosition()) < GAP_LIMIT and float(idu_gap.getPosition()) > GAP_LIMIT:
        #using IDD
        smode.mode=X_RAY_SOURCE_MODES[0]
        pol.polarisation = pol.determinePhaseFromHardware(idd_controls)[0]
    else:
        smode.mode=X_RAY_SOURCE_MODES[2]
        
if installation.isLive():
    smode=SourceMode('smode',idu_gap, idd_gap, opengap=200, defaultmode=None)
    pol=BeamEnergyPolarisationClass('pol', smode, pgm_energy, idd_controls, idu_controls, lut4gap=ID_ENERGY_TO_GAP_CALIBRATION_FILE, lut4phase=ID_ENERGY_TO_PHASE_CALIBRATION_FILE, energyConstant=True, polarisationConstant=False, maxGap=200, minGap=16, maxPhase=24)
    initialisation()
else:
    smode=DummyListScannable('smode', list_values=X_RAY_SOURCE_MODES[:-1])
    pol=DummyListScannable('pol', list_values=X_RAY_POLARISATIONS[:-1])

energy_s=BeamEnergyPolarisationClass("energy_s", smode, pgm_energy, idd_controls, idu_controls, lut4gap=ID_ENERGY_TO_GAP_CALIBRATION_FILE, lut4phase=ID_ENERGY_TO_PHASE_CALIBRATION_FILE, energyConstant=False, polarisationConstant=True, energy_offset=energy_offset, maxGap=200, minGap=16, maxPhase=24)
energy_pol=BeamEnergyPolarisationClass("energy_pol", smode, pgm_energy, idd_controls, idu_controls, lut4gap=ID_ENERGY_TO_GAP_CALIBRATION_FILE, lut4phase=ID_ENERGY_TO_PHASE_CALIBRATION_FILE, energyConstant=False, polarisationConstant=False, energy_offset=energy_offset, maxGap=200, minGap=16, maxPhase=24)
energy_pol.setInputNames(["energy","pol"])
laa = LinearArbitraryAngle("laa", idu_jawphase, idd_jawphase, smode, pol, jawphase_from_angle=Poly([-120./7.5, 1./7.5], power0first=True), angle_threshold_deg = 30.0)  # @UndefinedVariable
