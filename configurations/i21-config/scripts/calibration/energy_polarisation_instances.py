'''
defines beam energy and polarisation control scannables
Created on May 6, 2022

@author: fy65
'''
from lookup.IDLookup import IDLookup4LinearAngleMode
from calibration.energy_polarisation_class import BeamEnergyPolarisationClass
import installation
from gdaserver import idscannable,pgmEnergy,pgmGratingSelect  # @UnresolvedImport
from gda.configuration.properties import LocalProperties

lookup_file = LocalProperties.get("gda.config") + "/lookupTables/LinearAngle.csv" #theoretical table from ID group
ID_ENERGY_TO_GAP_CALIBRATION_FILE = "IDEnergy2GapCalibrations.csv"
EPICS_FEEDBACK_PV = "BL21I-OP-MIRR-01:FBCTRL:MODE"
idlamlookup = IDLookup4LinearAngleMode("idlamlookup", lut = str(lookup_file))

if installation.isLive():
    energy_s = BeamEnergyPolarisationClass("energy_s", idscannable, pgmEnergy, pgmGratingSelect, idlamlookup, lut=ID_ENERGY_TO_GAP_CALIBRATION_FILE, polarisationConstant=True,feedbackPV=EPICS_FEEDBACK_PV)  
    energy_s.configure()
    polarisation = BeamEnergyPolarisationClass("polarisation", idscannable, pgmEnergy, pgmGratingSelect, idlamlookup, lut=ID_ENERGY_TO_GAP_CALIBRATION_FILE, energyConstant=True,feedbackPV=EPICS_FEEDBACK_PV) 
    polarisation.configure()
    energypolarisation = BeamEnergyPolarisationClass("energypolarisation", idscannable, pgmEnergy, pgmGratingSelect, idlamlookup, lut=ID_ENERGY_TO_GAP_CALIBRATION_FILE,feedbackPV=EPICS_FEEDBACK_PV) 
    energypolarisation.configure()
else:
    energy_s = BeamEnergyPolarisationClass("energy_s", idscannable, pgmEnergy, pgmGratingSelect, idlamlookup, lut=ID_ENERGY_TO_GAP_CALIBRATION_FILE, polarisationConstant=True)  
    energy_s.configure()
    polarisation = BeamEnergyPolarisationClass("polarisation", idscannable, pgmEnergy, pgmGratingSelect, idlamlookup, lut=ID_ENERGY_TO_GAP_CALIBRATION_FILE, energyConstant=True) 
    polarisation.configure()
    energypolarisation = BeamEnergyPolarisationClass("energypolarisation", idscannable, pgmEnergy, pgmGratingSelect, idlamlookup, lut=ID_ENERGY_TO_GAP_CALIBRATION_FILE) 
    energypolarisation.configure()

energypolarisation.setInputNames(["energy"])
energypolarisation.setExtraNames(["polarisation"])
