'''
Extracted from i10-config/scripts/scannable/continuous/try_continuous_energy.py in GDA 9.8
Created on 13 Apr 2018

@author: fy65
'''
from scannable.waveform_channel.BinpointWaveformChannelController import BinpointWaveformChannelController
from scannable.waveform_channel.McsWaveformChannelController import McsWaveformChannelController
from scannable.waveform_channel.WaveformChannelScannable import WaveformChannelScannable
from scannable.continuous.ContinuousPgmGratingIDGapMoveController import ContinuousPgmGratingIDGapMoveController

from gdaserver import pgm_grat_pitch, pgm_m2_pitch  # @UnresolvedImport
from calibrations.mode_polarisation_energy_instances import energy_s
from scannable.continuous.ContinuousMovePgmEnergyIDGapBinpointScannable import ContinuousMovePgmEnergyIDGapBinpointScannable

print("-"*100)
print("Creating scannables for continuous energy scanning using cvscan")
print("  These Objects deliver constant velocity motion in PGM grating pitch motor and ID gap simultaneously:")
print("   'energy' - energy scannable used in 'cvscan' to control beam energy via PGM Grating pitch, PGM mirror pitch and ID gap")
print("            - this scannable can also be used in step 'scan' command, in which it delegates energy move to 'energy_s' scannable.")
print("   'mcs16', 'mcs17', 'mcs18', 'mcs19', 'mcs20', 'mcs21', 'mcs11', 'mcs23'- RASOR scannables used in 'cvscan' to collect data from MCS channel 17, 18, 19, 20, 21, 22, 23, 24, respectively")

# RASOR counter controller - reading collected data from multi-channel scaler:    ME01D-EA-SCLR-01:MCA01:
mcs_controller = McsWaveformChannelController('mcs_controller', 'ME01D-EA-SCLR-01:MCA01:', channelAdvanceInternalNotExternal=True); mcs_controller.verbose=True
# Sometimes the RASOR struck scaler returns 1 fewer points than requested, this causes the binpoints to fail and the whole scan to fail.
# Adding the shortest possible time to the total count time seems to ensure that all of the required points are acquired.   
mcs_controller.exposure_time_offset = 0.001
# Binpoint is slaved from (triggered by) RASOR scaler (mcs_controller) - reading collected motor position data from BINPOINT  'BL10I-CS-CSCAN-01:'
binpoint_controller = BinpointWaveformChannelController('binpoint_controller', 'BL10I-CS-CSCAN-01:', 'IDPGM:BINPOINTALL:'); binpoint_controller.verbose=True
#provide continuous motion of energy by moving ID gap and PGM Grating Pitch motor continuously
energy_controller = ContinuousPgmGratingIDGapMoveController('energy_controller', pgm_grat_pitch, pgm_m2_pitch, 'BL10I-OP-PGM-01:', energy_s, 'SR10I-MO-SERVC-21:', 'SR10I-MO-SERVC-01:'); energy_controller.verbose=True

# scannables to capture count data from scaler channels 
mcs16 = WaveformChannelScannable('mcs16', mcs_controller, 17); mcs16.setHardwareTriggerProvider(energy_controller); mcs16.verbose=True
mcs17 = WaveformChannelScannable('mcs17', mcs_controller, 18); mcs17.setHardwareTriggerProvider(energy_controller); mcs17.verbose=True
mcs18 = WaveformChannelScannable('mcs18', mcs_controller, 19); mcs18.setHardwareTriggerProvider(energy_controller); mcs18.verbose=True
mcs19 = WaveformChannelScannable('mcs19', mcs_controller, 20); mcs19.setHardwareTriggerProvider(energy_controller); mcs19.verbose=True
mcs20 = WaveformChannelScannable('mcs20', mcs_controller, 21); mcs20.setHardwareTriggerProvider(energy_controller); mcs20.verbose=True
mcs21 = WaveformChannelScannable('mcs21', mcs_controller, 22); mcs21.setHardwareTriggerProvider(energy_controller); mcs21.verbose=True
mcs22 = WaveformChannelScannable('mcs22', mcs_controller, 23); mcs22.setHardwareTriggerProvider(energy_controller); mcs22.verbose=True
mcs23 = WaveformChannelScannable('mcs23', mcs_controller, 24); mcs23.setHardwareTriggerProvider(energy_controller); mcs23.verbose=True
# scannables to capture motor position data from BINPOINT 
binpoint_GrtPitch  = WaveformChannelScannable('binpoint_GrtPitch',  binpoint_controller, 'GRT:PITCH:');       binpoint_GrtPitch.setHardwareTriggerProvider(energy_controller);  binpoint_GrtPitch.verbose=True
binpoint_MirPitch  = WaveformChannelScannable('binpoint_MirPitch',  binpoint_controller, 'MIR:PITCH:');       binpoint_MirPitch.setHardwareTriggerProvider(energy_controller);  binpoint_MirPitch.verbose=True
binpoint_PgmEnergy = WaveformChannelScannable('binpoint_PgmEnergy', binpoint_controller, 'PGM:ENERGY:');      binpoint_PgmEnergy.setHardwareTriggerProvider(energy_controller); binpoint_PgmEnergy.verbose=True
binpoint_ID1Jawphase = WaveformChannelScannable('binpoint_em_ID1Jawphase', binpoint_controller, 'ID1:JAWPHASE:');      binpoint_ID1Jawphase.setHardwareTriggerProvider(energy_controller); binpoint_ID1Jawphase.verbose=True
binpoint_ID2Jawphase = WaveformChannelScannable('binpoint_em_ID2Jawphase', binpoint_controller, 'ID2:JAWPHASE:');      binpoint_ID2Jawphase.setHardwareTriggerProvider(energy_controller); binpoint_ID2Jawphase.verbose=True
binpoint_McaTime   = WaveformChannelScannable('binpoint_McaTime',   binpoint_controller, 'MCA:ELAPSEDTIME:'); binpoint_McaTime.setHardwareTriggerProvider(energy_controller);   binpoint_McaTime.verbose=True
# binpoint_Custom1   = WaveformChannelScannable('binpoint_Custom1',   binpoint_controller, 'CUSTOM1:');         binpoint_Custom1.setHardwareTriggerProvider(energy_controller);   binpoint_Custom1.verbose=True

#energy scannable used to parse input data and delegate motions to controllers above
energy = ContinuousMovePgmEnergyIDGapBinpointScannable('energy', energy_controller, binpoint_GrtPitch, binpoint_MirPitch, binpoint_PgmEnergy); energy.verbose=True

# cvscan energy 695 705 1 mcs17 2 

