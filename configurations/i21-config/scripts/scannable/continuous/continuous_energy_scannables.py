'''
Extracted from i10-config/scripts/scannable/continuous/try_continuous_energy.py in GDA 9.8
Created on 13 Apr 2018

@author: fy65
'''
from scannable.waveform_channel.BinpointWaveformChannelController import BinpointWaveformChannelController
from scannable.waveform_channel.McsWaveformChannelController import McsWaveformChannelController
from scannable.waveform_channel.WaveformChannelScannable import WaveformChannelScannable
from scannable.continuous.continuousMovePgmEnergyIDGapBinpointScannable import ContinuousMovePgmEnergyIDGapBinpointScannable
from scannable.continuous.continuousPgmEnergyIDGapMoveController import ContinuousPgmEnergyIDGapMoveController
import __main__  # @UnresolvedImport

print "-"*100
print "Creating scannables for continuous energy scan"
print "    Objects for constant velocity energy scan are:"
print "    1. 'cenergy'   - energy scannable used to perform continuous energy scan by moving PGM energy and ID gap continuously at constant velocity"
print "    2. 'mcs2','mcs3','mcs4', 'mcs5' - scannables used with 'cenergy' scannable, mapped to MCS channel 2, 3, 4, 5 respectively"
print "    3. 'binpointPgmEnergy','binpointIdGap','binpointMcaTime' - position capturer waveform scannables used with 'cenergy' scannable in continuous scan"

# ES2 Scaler controller:  BL09L-VA-SCLR-01:MCA-01:
mcscontroller  = McsWaveformChannelController('mcscontroller', 'BL09L-VA-SCLR-01:MCA-01:', channelAdvanceInternalNotExternal=True); mcscontroller.verbose=True

# Sometimes the MCS struck scaler returns 1 fewer points than requested, this causes the binpoints to fail and the whole scan to fail.
# Adding the shortest possible time to the total count time seems to ensure that all of the required points are acquired.   
mcscontroller.exposure_time_offset=0.001

# Binpoint is slaved from (triggered by) scaler (mcscontroller)    BL09J-CS-CSCAN-01:IDPGM:BINPOINTALL:TRIGGER
binpointc = BinpointWaveformChannelController('binpointc', 'BLTST-LPT-DEV-01:', 'JUMP:BPTS:BINPOINTALL:'); binpointc.verbose=True

energy_move_controller = ContinuousPgmEnergyIDGapMoveController('energy_move_controller', __main__.energy, 'SR21I-MO-SERVC-01:'); energy_move_controller.verbose=True
#draincurrent
draincurrent_c = WaveformChannelScannable('draincurrent_c', mcscontroller, 2); draincurrent_c.setHardwareTriggerProvider(energy_move_controller); draincurrent_c.verbose=True
#diff1
diff1_c = WaveformChannelScannable('diff1_c', mcscontroller, 3); diff1_c.setHardwareTriggerProvider(energy_move_controller); diff1_c.verbose=True

binpointPgmEnergy = WaveformChannelScannable('binpointPgmEnergy', binpointc, 'B1:'); binpointPgmEnergy.setHardwareTriggerProvider(energy_move_controller); binpointPgmEnergy.verbose=True
binpointIdGap     = WaveformChannelScannable('binpointIdGap',     binpointc, 'B2:'); binpointIdGap.setHardwareTriggerProvider(energy_move_controller);     binpointIdGap.verbose=True

energy_c = ContinuousMovePgmEnergyIDGapBinpointScannable('energy_c', energy_move_controller, binpointPgmEnergy, binpointIdGap); energy_c.verbose=True

# cvscan cenergy 695 705 1 mcs2 2 mcs3 2 mcs4 2 mcs5 2  binpointPgmEnergy binpointIdGap binpointMcaTime 
