'''
create controller and scannable instances to be used in continuous energy moving scan i.e. cvscan.
'jenergy' scannables are also working with classic scan i.e.'scan' command, but the detector scannables and controllers should not be used with 'scan'
@author: fy65
@since: 22 September 2020
'''
from i09shared.scannable.continuous.continuousMoveEnergyIDGapBinpointScannable import ContinuousMoveEnergyIDGapBinpointScannable
from i09shared.scannable.continuous.continuousEnergyMoveController import ContinuousEnergyMoveController
from i09shared.scannable.waveform_channel.WaveformChannelScannable import WaveformChannelScannable

print("-"*100)
print("Creating j branch scannables for continuous energy scanning with 'cvscan' command")
print("    Objects for constant velocity in PGM grating pitch motor with ID moving as follower:")
print("    1. 'jenergy' - soft X-ray energy scannable that works with both 'cvscan' and 'scan' command")
print("    2. 'jI0'     - soft X-ray I0 scannable used in 'cvscan' ONLY")
print("    3. 'sdc'     - sample drain current scannable used in 'cvscan' ONLY")
print("")

from i09_2_shared.scannable.energy_polarisation_order_gap_instances import jenergy_s #@UnusedImport
from gdaserver import jgap # @UnresolvedImport

jenergy_move_controller = ContinuousEnergyMoveController('jenergy_move_controller', jenergy_s, jgap, 'SR09J-MO-SERVC-01:'); jenergy_move_controller.verbose=True

from i09shared.scannable.continuous.energy_scannable_instance_setup import mcscontroller, binpointc
#sm5amp8 - soft X-ray I0
jI0 = WaveformChannelScannable('jI0', mcscontroller, 3); jI0.setHardwareTriggerProvider(jenergy_move_controller); jI0.verbose=True
#smpmamp39 - Sample Drain Current - hardware trigger provider set here will be override dynamically in cvscan command as it is used for both hard and soft X-ray energy scan
sdc = WaveformChannelScannable('sdc', mcscontroller, 4); sdc.setHardwareTriggerProvider(jenergy_move_controller); sdc.verbose=True
binpointPgmEnergy = WaveformChannelScannable('binpointPgmEnergy', binpointc, 'B1:'); binpointPgmEnergy.setHardwareTriggerProvider(jenergy_move_controller); binpointPgmEnergy.verbose=True
binpointJidGap    = WaveformChannelScannable('binpointJidGap',    binpointc, 'B2:'); binpointJidGap.setHardwareTriggerProvider(jenergy_move_controller);    binpointJidGap.verbose=True
binpointMcaTime   = WaveformChannelScannable('binpointMcaTime',   binpointc, 'B3:'); binpointMcaTime.setHardwareTriggerProvider(jenergy_move_controller);   binpointMcaTime.verbose=True
jenergy = ContinuousMoveEnergyIDGapBinpointScannable('jenergy', jenergy_move_controller, binpointPgmEnergy, binpointJidGap); jenergy.verbose=True
#Test example commands
#Soft X-ray
#cvscan jenergy 0.2 0.45 0.001 jI0 0.5 sdc 0.5