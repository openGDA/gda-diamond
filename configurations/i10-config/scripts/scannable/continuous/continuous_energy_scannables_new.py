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
print("  These Objects deliver constant velocity motion in PGM grating pitch motor and ID gap at the same time:")
print("   'energy' - energy scannable used in 'cvscan' to control beam energy via PGM Grating pitch, PGM mirror pitch and ID gap")
print("            - this scannable can also be used in step 'scan' command, in which it delegates energy move to 'energy_s scannable.")
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

print("-"*100)
print("Creating scannables for continuous energy scanning using cvscan")
print("  These Objects deliver constant velocity motion in PGM grating pitch motor and ID gap at the same time:")
print("   'energye' - energy scannable used in 'cvscan' to control beam energy via PGM Grating pitch, PGM mirror pitch and ID gap")
print("            - this scannable can also be used in step 'scan' command, in which it delegates energy move to 'energy_s scannable.")
print("   'mcse16', 'mcse17', 'mcse18', 'mcse19', 'mcse20', 'mcse21', 'mcse11', 'mcse23'- EM scannables used in 'cvscan' to collect data from MCS channel 17, 18, 19, 20, 21, 22, 23, 24 on SCALAR 3, respectively")

# Electron Magnet counter controller - reading collected data from multi-channel scaler:    BL10J-EA-SCLR-02:MCAJ03:
mcs_em_controller = McsWaveformChannelController('mcs_em_controller', 'BL10J-EA-SCLR-02:MCAJ03:', channelAdvanceInternalNotExternal=True); mcs_em_controller.verbose=True
# Sometimes the struck scaler returns 1 fewer points than requested, this causes the binpoints to fail and the whole scan to fail.
# Adding the shortest possible time to the total count time seems to ensure that all of the required points are acquired.   
mcs_em_controller.exposure_time_offset = 0.001
# Binpoint is slaved from (triggered by) EM scaler (mcs_em_controller) - reading collected motor position data from BINPOINT  'BL10J-EA-CSCAN-02:'
binpoint_em_controller = BinpointWaveformChannelController('binpoint_em_controller', 'BL10J-EA-CSCAN-02:', 'IDPGM:BINPOINTALL:'); binpoint_em_controller.verbose=True

# scannables to capture count data from scaler 3 channels 
mcse16 = WaveformChannelScannable('mcse16', mcs_em_controller, 17); mcse16.setHardwareTriggerProvider(energy_controller); mcse16.verbose=True
mcse17 = WaveformChannelScannable('mcse17', mcs_em_controller, 18); mcse17.setHardwareTriggerProvider(energy_controller); mcse17.verbose=True
mcse18 = WaveformChannelScannable('mcse18', mcs_em_controller, 19); mcse18.setHardwareTriggerProvider(energy_controller); mcse18.verbose=True
mcse19 = WaveformChannelScannable('mcse19', mcs_em_controller, 20); mcse19.setHardwareTriggerProvider(energy_controller); mcse19.verbose=True
mcse20 = WaveformChannelScannable('mcse20', mcs_em_controller, 21); mcse20.setHardwareTriggerProvider(energy_controller); mcse20.verbose=True
mcse21 = WaveformChannelScannable('mcse21', mcs_em_controller, 22); mcse21.setHardwareTriggerProvider(energy_controller); mcse21.verbose=True
mcse22 = WaveformChannelScannable('mcse22', mcs_em_controller, 23); mcse22.setHardwareTriggerProvider(energy_controller); mcse22.verbose=True
mcse23 = WaveformChannelScannable('mcse23', mcs_em_controller, 24); mcse23.setHardwareTriggerProvider(energy_controller); mcse23.verbose=True
# scannables to capture motor position data from BINPOINT 
binpoint_em_GrtPitch  = WaveformChannelScannable('binpoint_em_GrtPitch',  binpoint_em_controller, 'GRT:PITCH:');       binpoint_em_GrtPitch.setHardwareTriggerProvider(energy_controller);  binpoint_em_GrtPitch.verbose=True
binpoint_em_MirPitch  = WaveformChannelScannable('binpoint_em_MirPitch',  binpoint_em_controller, 'MIR:PITCH:');       binpoint_em_MirPitch.setHardwareTriggerProvider(energy_controller);  binpoint_em_MirPitch.verbose=True
binpoint_em_PgmEnergy = WaveformChannelScannable('binpoint_em_PgmEnergy', binpoint_em_controller, 'PGM:ENERGY:');      binpoint_em_PgmEnergy.setHardwareTriggerProvider(energy_controller); binpoint_em_PgmEnergy.verbose=True
binpoint_em_ID1Jawphase = WaveformChannelScannable('binpoint_em_ID1Jawphase', binpoint_em_controller, 'ID1:JAWPHASE:');      binpoint_em_ID1Jawphase.setHardwareTriggerProvider(energy_controller); binpoint_em_ID1Jawphase.verbose=True
binpoint_em_ID2Jawphase = WaveformChannelScannable('binpoint_em_ID2Jawphase', binpoint_em_controller, 'ID2:JAWPHASE:');      binpoint_em_ID2Jawphase.setHardwareTriggerProvider(energy_controller); binpoint_em_ID2Jawphase.verbose=True
binpoint_em_McaTime   = WaveformChannelScannable('binpoint_em_McaTime',   binpoint_em_controller, 'MCA:ELAPSEDTIME:'); binpoint_em_McaTime.setHardwareTriggerProvider(energy_controller);   binpoint_em_McaTime.verbose=True

#energy scannable used to parse input data and delegate motions to controllers above
energye = ContinuousMovePgmEnergyIDGapBinpointScannable('energye', energy_controller, binpoint_em_GrtPitch, binpoint_em_MirPitch, binpoint_em_PgmEnergy); energye.verbose=True

