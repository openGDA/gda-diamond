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
print "    Objects for constant velocity in PGM grating picth motor with ID moving as follower:"
print "    1. 'cenergy'   - energy scannable used to perform continuous energy scan via PGM energy and ID gap"
print "    2. 'mcs2','mcs3','mcs4', 'mcs5' - scannables used with 'cenergy' scannable, mapped to MCS channel 2, 3, 4, 5 respectively"
print "    3. 'binpointPgmEnergy','binpointIdGap','binpointMcaTime' - position capturer waveform scannables used with 'cenergy' scannable in continuous scan"

# ES2 Scaler controller:  BL09L-VA-SCLR-01:MCA-01:
#mcscontroller  = McsWaveformChannelController('mcscontroller', 'BL09L-VA-SCLR-01:MCA-01:', channelAdvanceInternalNotExternal=True); mcscontroller.verbose=True
# EA1 Scaler controller: BL09I-EA-SCLR-01:MCA-01:                BL09I-EA-SCLR-01:MCA-01:mca1
mcscontroller  = McsWaveformChannelController('mcscontroller', 'BL09I-EA-SCLR-01:MCA-01:', channelAdvanceInternalNotExternal=True); mcscontroller.verbose=True

# Sometimes the MCS struck scaler returns 1 fewer points than requested, this causes the binpoints to fail and the whole scan to fail.
# Adding the shortest possible time to the total count time seems to ensure that all of the required points are acquired.   
mcscontroller.exposure_time_offset=0.001

# Binpoint is slaved from (triggered by) scaler (mcscontroller)    BL09J-CS-CSCAN-01:IDPGM:BINPOINTALL:TRIGGER
binpointc = BinpointWaveformChannelController('binpointc', 'BL09J-CS-CSCAN-01:', 'IDPGM:BINPOINTALL:'); binpointc.verbose=True

from pseudodevices.detuneIDGap import jdetune
energy_move_controller = ContinuousPgmEnergyIDGapMoveController('energy_move_controller', __main__.jenergy, 'SR09J-MO-SERVC-01:', detune=jdetune); energy_move_controller.verbose=True
#hm3amp20
mcs2 = WaveformChannelScannable('mcs2', mcscontroller, 2); mcs2.setHardwareTriggerProvider(energy_move_controller); mcs2.verbose=True
#sm5amp8
mcs3 = WaveformChannelScannable('mcs3', mcscontroller, 3); mcs3.setHardwareTriggerProvider(energy_move_controller); mcs3.verbose=True
#smpmamp39
mcs4 = WaveformChannelScannable('mcs4', mcscontroller, 4); mcs4.setHardwareTriggerProvider(energy_move_controller); mcs4.verbose=True
#rfdamp10
mcs5 = WaveformChannelScannable('mcs5', mcscontroller, 5); mcs5.setHardwareTriggerProvider(energy_move_controller); mcs5.verbose=True

binpointPgmEnergy = WaveformChannelScannable('binpointPgmEnergy', binpointc, 'B1:'); binpointPgmEnergy.setHardwareTriggerProvider(energy_move_controller); binpointPgmEnergy.verbose=True
binpointIdGap     = WaveformChannelScannable('binpointIdGap',     binpointc, 'B2:'); binpointIdGap.setHardwareTriggerProvider(energy_move_controller);     binpointIdGap.verbose=True
binpointMcaTime   = WaveformChannelScannable('binpointMcaTime',   binpointc, 'B3:'); binpointMcaTime.setHardwareTriggerProvider(energy_move_controller);   binpointMcaTime.verbose=True
binpointCustom    = WaveformChannelScannable('binpointCustom',    binpointc, 'B4:'); binpointCustom.setHardwareTriggerProvider(energy_move_controller);    binpointCustom.verbose=True

cenergy = ContinuousMovePgmEnergyIDGapBinpointScannable('cenergy', energy_move_controller, binpointPgmEnergy, binpointIdGap); cenergy.verbose=True

# cvscan cenergy 695 705 1 mcs2 2 mcs3 2 mcs4 2 mcs5 2  binpointPgmEnergy binpointIdGap binpointMcaTime 
