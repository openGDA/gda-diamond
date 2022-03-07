'''
Extracted from i10-config/scripts/scannable/continuous/try_continuous_energy.py in GDA 9.8
Created on 13 Apr 2018

@author: fy65
'''
from scannable.waveform_channel.BinpointWaveformChannelController import BinpointWaveformChannelController
from scannable.waveform_channel.McsWaveformChannelController import McsWaveformChannelController
from scannable.waveform_channel.WaveformChannelScannable import WaveformChannelScannable
from scannable.continuous.ContinuousMovePgmEnergyIDGapBinpointScannable import ContinuousMovePgmEnergyIDGapBinpointScannable
from scannable.continuous.energy_move_controller import energy_controller

print("-"*100)
print("Creating scannables for continuous energyh scanning using cvscan in HFM end station.")
print("  These Objects deliver constant velocity motion in PGM grating pitch motor and ID gap at the same time:")
print("   'energyh' - energyh scannable used in 'cvscan' to control beam energyh via PGM Grating pitch, PGM mirror pitch and ID gap")
print("            - this scannable can also be used in step 'scan' command, in which it delegates energyh move to 'energy_s' scannable.")
print("   'mcsh16', 'mcsh17', 'mcsh18', 'mcsh19', 'mcsh20', 'mcsh21', 'mcsh22', 'mcsh23'- HFM scannables used in 'cvscan' to collect data from MCS channel 17, 18, 19, 20, 21, 22, 23, 24 on SCALAR 3, respectively")

# Electron Magnet counter controller - reading collected data from multi-channel scaler:    BL10J-EA-SCLR-01:MCAJ02:
mcs_hfm_controller = McsWaveformChannelController('mcs_hfm_controller', 'BL10J-EA-SCLR-01:MCAJ02:', channelAdvanceInternalNotExternal=True); mcs_hfm_controller.verbose=True
# Sometimes the struck scaler returns 1 fewer points than requested, this causes the binpoints to fail and the whole scan to fail.
# Adding the shortest possible time to the total count time seems to ensure that all of the required points are acquired.   
mcs_hfm_controller.exposure_time_offset = 0.001
# Binpoint is slaved from (triggered by) EM scaler (mcs_hfm_controller) - reading collected motor position data from BINPOINT  'BL10J-EA-CSCAN-01:'
binpoint_hfm_controller = BinpointWaveformChannelController('binpoint_hfm_controller', 'BL10J-EA-CSCAN-01:', 'IDPGM:BINPOINTALL:'); binpoint_hfm_controller.verbose=True

# scannables to capture count data from scaler 3 channels 
mcsh16 = WaveformChannelScannable('mcsh16', mcs_hfm_controller, 17); mcsh16.setHardwareTriggerProvider(energy_controller); mcsh16.verbose=True
mcsh17 = WaveformChannelScannable('mcsh17', mcs_hfm_controller, 18); mcsh17.setHardwareTriggerProvider(energy_controller); mcsh17.verbose=True
mcsh18 = WaveformChannelScannable('mcsh18', mcs_hfm_controller, 19); mcsh18.setHardwareTriggerProvider(energy_controller); mcsh18.verbose=True
mcsh19 = WaveformChannelScannable('mcsh19', mcs_hfm_controller, 20); mcsh19.setHardwareTriggerProvider(energy_controller); mcsh19.verbose=True
mcsh20 = WaveformChannelScannable('mcsh20', mcs_hfm_controller, 21); mcsh20.setHardwareTriggerProvider(energy_controller); mcsh20.verbose=True
mcsh21 = WaveformChannelScannable('mcsh21', mcs_hfm_controller, 22); mcsh21.setHardwareTriggerProvider(energy_controller); mcsh21.verbose=True
mcsh22 = WaveformChannelScannable('mcsh22', mcs_hfm_controller, 23); mcsh22.setHardwareTriggerProvider(energy_controller); mcsh22.verbose=True
mcsh23 = WaveformChannelScannable('mcsh23', mcs_hfm_controller, 24); mcsh23.setHardwareTriggerProvider(energy_controller); mcsh23.verbose=True
# scannables to capture motor position data from BINPOINT 
binpoint_hfm_GrtPitch  = WaveformChannelScannable('binpoint_hfm_GrtPitch',  binpoint_hfm_controller, 'GRT:PITCH:');       binpoint_hfm_GrtPitch.setHardwareTriggerProvider(energy_controller);  binpoint_hfm_GrtPitch.verbose=True
binpoint_hfm_MirPitch  = WaveformChannelScannable('binpoint_hfm_MirPitch',  binpoint_hfm_controller, 'MIR:PITCH:');       binpoint_hfm_MirPitch.setHardwareTriggerProvider(energy_controller);  binpoint_hfm_MirPitch.verbose=True
binpoint_hfm_PgmEnergy = WaveformChannelScannable('binpoint_hfm_PgmEnergy', binpoint_hfm_controller, 'PGM:ENERGY:');      binpoint_hfm_PgmEnergy.setHardwareTriggerProvider(energy_controller); binpoint_hfm_PgmEnergy.verbose=True
binpoint_hfm_ID1Jawphase = WaveformChannelScannable('binpoint_hfm_ID1Jawphase', binpoint_hfm_controller, 'ID1:JAWPHASE:');      binpoint_hfm_ID1Jawphase.setHardwareTriggerProvider(energy_controller); binpoint_hfm_ID1Jawphase.verbose=True
binpoint_hfm_ID2Jawphase = WaveformChannelScannable('binpoint_hfm_ID2Jawphase', binpoint_hfm_controller, 'ID2:JAWPHASE:');      binpoint_hfm_ID2Jawphase.setHardwareTriggerProvider(energy_controller); binpoint_hfm_ID2Jawphase.verbose=True
binpoint_hfm_McaTime   = WaveformChannelScannable('binpoint_hfm_McaTime',   binpoint_hfm_controller, 'MCA:ELAPSEDTIME:'); binpoint_hfm_McaTime.setHardwareTriggerProvider(energy_controller);   binpoint_hfm_McaTime.verbose=True

#energyh scannable used to parse input data and delegate motions to controllers above
energyh = ContinuousMovePgmEnergyIDGapBinpointScannable('energyh', energy_controller, binpoint_hfm_GrtPitch, binpoint_hfm_MirPitch, binpoint_hfm_PgmEnergy); energyh.verbose=True


# cvscan energyh 695 705 1 mcsh17 2 