'''
Object to provide continuous motion of energy by moving ID gap and PGM Grating Pitch motor continuously
Created on Mar 7, 2022

@author: fy65
'''
from scannable.continuous.ContinuousPgmGratingIDGapMoveController import ContinuousPgmGratingIDGapMoveController
from gdaserver import pgm_grat_pitch, pgm_m2_pitch  # @UnresolvedImport
from calibrations.mode_polarisation_energy_instances import energy_s

print("-"*100)
print("Creating continuous energy motion controller 'energy_controller' for cvscan.")

energy_controller = ContinuousPgmGratingIDGapMoveController('energy_controller', pgm_grat_pitch, pgm_m2_pitch, 'BL10I-OP-PGM-01:', energy_s, 'SR10I-MO-SERVC-21:', 'SR10I-MO-SERVC-01:'); energy_controller.verbose=True
