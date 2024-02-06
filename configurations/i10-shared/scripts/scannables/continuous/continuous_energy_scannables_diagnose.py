'''
Extracted from i10-config/scripts/scannable/continuous/try_continuous_energy.py in GDA 9.8
Created on 13 Apr 2018

@author: fy65
'''
from scannables.waveform_channel.BinpointWaveformChannelController import BinpointWaveformChannelController
from scannables.waveform_channel.McsWaveformChannelController import McsWaveformChannelController
from scannables.waveform_channel.WaveformChannelScannable import WaveformChannelScannable
from scannables.continuous.ContinuousMovePgmEnergyIDGapBinpointScannable import ContinuousMovePgmEnergyIDGapBinpointScannable
from scannables.continuous.energy_move_controller import energy_controller

print("-"*100)
print("Creating scannables for continuous energy scanning using cvscan in RASOR end station.")
print("  These Objects deliver constant velocity motion in PGM grating pitch motor and ID gap simultaneously:")
print("   'energy' - energy scannable used in 'cvscan' to control beam energy via PGM Grating pitch, PGM mirror pitch and ID gap")
print("            - this scannable can also be used in step 'scan' command, in which it delegates energy move to 'energy_s' scannable.")
print("   'mcs16', 'mcs17', 'mcs18', 'mcs19', 'mcs20', 'mcs21', 'mcs11', 'mcs23'- RASOR scannables used in 'cvscan' to collect data from MCS channel 17, 18, 19, 20, 21, 22, 23, 24, respectively")

# Diagnose counter controller - reading collected data from multi-channel scaler
mcs_diagnose_controller = McsWaveformChannelController('mcs_diagnose_controller', 'BL10I-DI-SCLR-02:MCA02:', channelAdvanceInternalNotExternal = True); mcs_diagnose_controller.verbose = True
# Sometimes the RASOR struck scaler returns 1 fewer points than requested, this causes the binpoints to fail and the whole scan to fail.
# Adding the shortest possible time to the total count time seems to ensure that all of the required points are acquired.
mcs_diagnose_controller.exposure_time_offset = 0.001
# Binpoint is slaved from (triggered by) Diagnose scaler (mcs_diagnose_controller) - reading collected motor position data from BINPOINT  'BL10I-CS-CSCAN-01:'
binpoint_diagnose_controller = BinpointWaveformChannelController('binpoint_diagnose_controller', 'BL10I-DI-CSCAN-02:', 'IDPGM:BINPOINTALL:'); binpoint_diagnose_controller.verbose = True

# scannables to capture count data from scaler channels
mcsd16 = WaveformChannelScannable('mcsd16', mcs_diagnose_controller, 17); mcsd16.setHardwareTriggerProvider(energy_controller); mcsd16.verbose = True
mcsd17 = WaveformChannelScannable('mcsd17', mcs_diagnose_controller, 18); mcsd17.setHardwareTriggerProvider(energy_controller); mcsd17.verbose = True
mcsd18 = WaveformChannelScannable('mcsd18', mcs_diagnose_controller, 19); mcsd18.setHardwareTriggerProvider(energy_controller); mcsd18.verbose = True
mcsd19 = WaveformChannelScannable('mcsd19', mcs_diagnose_controller, 20); mcsd19.setHardwareTriggerProvider(energy_controller); mcsd19.verbose = True
mcsd20 = WaveformChannelScannable('mcsd20', mcs_diagnose_controller, 21); mcsd20.setHardwareTriggerProvider(energy_controller); mcsd20.verbose = True
mcsd21 = WaveformChannelScannable('mcsd21', mcs_diagnose_controller, 22); mcsd21.setHardwareTriggerProvider(energy_controller); mcsd21.verbose = True
mcsd22 = WaveformChannelScannable('mcsd22', mcs_diagnose_controller, 23); mcsd22.setHardwareTriggerProvider(energy_controller); mcsd22.verbose = True
mcsd23 = WaveformChannelScannable('mcsd23', mcs_diagnose_controller, 24); mcsd23.setHardwareTriggerProvider(energy_controller); mcsd23.verbose = True
# scannables to capture motor position data from BINPOINT
binpoint_diagnose_GrtPitch = WaveformChannelScannable('binpoint_diagnose_GrtPitch', binpoint_diagnose_controller, 'GRT:PITCH:');       binpoint_diagnose_GrtPitch.setHardwareTriggerProvider(energy_controller);  binpoint_diagnose_GrtPitch.verbose = True
binpoint_diagnose_MirPitch = WaveformChannelScannable('binpoint_diagnose_MirPitch', binpoint_diagnose_controller, 'MIR:PITCH:');       binpoint_diagnose_MirPitch.setHardwareTriggerProvider(energy_controller);  binpoint_diagnose_MirPitch.verbose = True
binpoint_diagnose_PgmEnergy = WaveformChannelScannable('binpoint_diagnose_PgmEnergy', binpoint_diagnose_controller, 'PGM:ENERGY:');      binpoint_diagnose_PgmEnergy.setHardwareTriggerProvider(energy_controller); binpoint_diagnose_PgmEnergy.verbose = True
binpoint_diagnose_ID1Jawphase = WaveformChannelScannable('binpoint_diagnose_ID1Jawphase', binpoint_diagnose_controller, 'ID1:JAWPHASE:');      binpoint_diagnose_ID1Jawphase.setHardwareTriggerProvider(energy_controller); binpoint_diagnose_ID1Jawphase.verbose = True
binpoint_diagnose_ID2Jawphase = WaveformChannelScannable('binpoint_diagnose_ID2Jawphase', binpoint_diagnose_controller, 'ID2:JAWPHASE:');      binpoint_diagnose_ID2Jawphase.setHardwareTriggerProvider(energy_controller); binpoint_diagnose_ID2Jawphase.verbose = True
binpoin_diagnoset_McaTime = WaveformChannelScannable('binpoin_diagnoset_McaTime', binpoint_diagnose_controller, 'MCA:ELAPSEDTIME:'); binpoin_diagnoset_McaTime.setHardwareTriggerProvider(energy_controller);   binpoin_diagnoset_McaTime.verbose = True
# binpoint_Custom1   = WaveformChannelScannable('binpoint_Custom1',   binpoint_controller, 'CUSTOM1:');         binpoint_Custom1.setHardwareTriggerProvider(energy_controller);   binpoint_Custom1.verbose=True

# energy scannable used to parse input data and delegate motions to controllers above
energyd = ContinuousMovePgmEnergyIDGapBinpointScannable('energyd', energy_controller, binpoint_diagnose_GrtPitch, binpoint_diagnose_MirPitch, binpoint_diagnose_PgmEnergy); energyd.verbose = True

# cvscan energyd 695 705 1 mcs17 2

