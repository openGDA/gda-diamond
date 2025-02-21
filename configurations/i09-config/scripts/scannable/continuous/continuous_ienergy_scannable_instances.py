'''
create controller and scannable instances to be used in continuous energy moving scan i.e. cvscan.
'ienergy' scannables are also working with classic scan i.e.'scan' command, but the detector scannables and controllers should not be used with 'scan'
@author: fy65
@since: 22 September 2020
'''
from i09shared.scannable.continuous.continuousEnergyMoveController import ContinuousEnergyMoveController
from i09shared.scannable.waveform_channel.WaveformChannelScannable import WaveformChannelScannable
from i09shared.scannable.continuous.continuousMoveEnergyIDGapBinpointScannable import ContinuousMoveEnergyIDGapBinpointScannable
print("-"*100)
print("Creating I-branch scannables for continuous energy scanning with 'cvscan' command")
print("    1. 'ienergy' - Hard X-ray energy scannable that works with both 'cvscan' and 'scan' command")
print("    2. 'iI0'     - Hard X-ray I0 scannable used in 'cvscan' ONLY")
print("")

from scannable.ienergy_order_gap_instances import ienergy_s  # @UnusedImport
from gdaserver import igap # @UnresolvedImport
ienergy_move_controller = ContinuousEnergyMoveController('ienergy_move_controller', ienergy_s, igap, 'SR09I-MO-SERVC-01:'); ienergy_move_controller.verbose=True
from i09shared.scannable.continuous.energy_scannable_instance_setup import mcscontroller, binpointc
#hm3amp20 - Hard X-ray I0
iI0 = WaveformChannelScannable('iI0', mcscontroller, 5); iI0.setHardwareTriggerProvider(ienergy_move_controller); iI0.verbose=True
binpointDcmEnergy = WaveformChannelScannable('binpointDcmEnergy', binpointc, 'B4:'); binpointDcmEnergy.setHardwareTriggerProvider(ienergy_move_controller); binpointDcmEnergy.verbose=True
binpointIidGap    = WaveformChannelScannable('binpointIidGap',    binpointc, 'B5:'); binpointIidGap.setHardwareTriggerProvider(ienergy_move_controller);    binpointIidGap.verbose=True
ienergy = ContinuousMoveEnergyIDGapBinpointScannable('ienergy', ienergy_move_controller, binpointDcmEnergy, binpointIidGap); ienergy.verbose=True
#Test example commands
#Hard X-ray
#cvscan ienergy 2.60 2.85 0.001 iI0 0.5 sdc 0.5