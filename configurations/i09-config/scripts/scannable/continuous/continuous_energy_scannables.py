'''
create controller and scannable instances to be used in continuous energy moving scan i.e. cvscan.
'ienergy' and 'jenergy' scannables are also working with classic scan i.e.'scan' command, but the detector scannables and controllers should not be used with 'scan'

@author: fy65
@since: 22 September 2020
'''
from scannable.waveform_channel.BinpointWaveformChannelController import BinpointWaveformChannelController
from scannable.waveform_channel.McsWaveformChannelController import McsWaveformChannelController
from scannable.continuous.continuousEnergyMoveController import ContinuousEnergyMoveController
from scannable.waveform_channel.WaveformChannelScannable import WaveformChannelScannable
from scannable.continuous.continuousMoveEnergyIDGapBinpointScannable import ContinuousMoveEnergyIDGapBinpointScannable
import __main__  # @UnresolvedImport

print ("-"*100)
print ("Creating scannables for continuous energy scanning with 'cvscan' command")
print ("    Objects for constant velocity in PGM grating pitch motor with ID moving as follower:")
print ("    1. 'jenergy' - soft X-ray energy scannable that works with both 'cvscan' and 'scan' command")
print ("    2. 'jI0'     - soft X-ray I0 scannable used in 'cvscan' ONLY")
print ("    3. 'sdc'     - sample drain current scannable used in 'cvscan' ONLY")
print ("    4. 'ienergy' - Hard X-ray energy scannable that works with both 'cvscan' and 'scan' command")
print ("    5. 'iI0'     - Hard X-ray I0 scannable used in 'cvscan' ONLY")
print("")

# ES2 Scaler controller:  BL09L-VA-SCLR-01:MCA-01:
#mcscontroller  = McsWaveformChannelController('mcscontroller', 'BL09L-VA-SCLR-01:MCA-01:', channelAdvanceInternalNotExternal=True); mcscontroller.verbose=True
# EA1 Scaler controller: BL09I-EA-SCLR-01:MCA-01:                BL09I-EA-SCLR-01:MCA-01:mca1
mcscontroller  = McsWaveformChannelController('mcscontroller', 'BL09I-EA-SCLR-01:MCA-01:', channelAdvanceInternalNotExternal=True); mcscontroller.verbose=True

# Sometimes the MCS struck scaler returns 1 fewer points than requested, this causes the binpoints to fail and the whole scan to fail.
# Adding the shortest possible time to the total count time seems to ensure that all of the required points are acquired.   
mcscontroller.exposure_time_offset=0.001

# Binpoint is slaved from (triggered by) scaler (mcscontroller)    BL09J-CS-CSCAN-01:IDPGM:BINPOINTALL:TRIGGER
binpointc = BinpointWaveformChannelController('binpointc', 'BL09J-CS-CSCAN-01:', 'IDPGM:BINPOINTALL:'); binpointc.verbose=True

jenergy_move_controller = ContinuousEnergyMoveController('jenergy_move_controller', __main__.jenergy_s, __main__.jgap, 'SR09J-MO-SERVC-01:'); jenergy_move_controller.verbose=True
ienergy_move_controller = ContinuousEnergyMoveController('ienergy_move_controller', __main__.ienergy_s, __main__.igap, 'SR09I-MO-SERVC-01:'); ienergy_move_controller.verbose=True

#sm5amp8 - soft X-ray I0
jI0 = WaveformChannelScannable('jI0', mcscontroller, 3); jI0.setHardwareTriggerProvider(jenergy_move_controller); jI0.verbose=True
#smpmamp39 - Sample Drain Current - hardware trigger provider set here will be override dynamically in cvscan command as it is used for both hard and soft X-ray energy scan  
sdc = WaveformChannelScannable('sdc', mcscontroller, 4); sdc.setHardwareTriggerProvider(jenergy_move_controller); sdc.verbose=True
#hm3amp20 - Hard X-ray I0
iI0 = WaveformChannelScannable('iI0', mcscontroller, 5); iI0.setHardwareTriggerProvider(ienergy_move_controller); iI0.verbose=True

binpointPgmEnergy = WaveformChannelScannable('binpointPgmEnergy', binpointc, 'B1:'); binpointPgmEnergy.setHardwareTriggerProvider(jenergy_move_controller); binpointPgmEnergy.verbose=True
binpointJidGap    = WaveformChannelScannable('binpointJidGap',    binpointc, 'B2:'); binpointJidGap.setHardwareTriggerProvider(jenergy_move_controller);    binpointJidGap.verbose=True
binpointMcaTime   = WaveformChannelScannable('binpointMcaTime',   binpointc, 'B3:'); binpointMcaTime.setHardwareTriggerProvider(jenergy_move_controller);   binpointMcaTime.verbose=True
binpointDcmEnergy = WaveformChannelScannable('binpointDcmEnergy', binpointc, 'B4:'); binpointDcmEnergy.setHardwareTriggerProvider(ienergy_move_controller); binpointDcmEnergy.verbose=True
binpointIidGap    = WaveformChannelScannable('binpointIidGap',    binpointc, 'B5:'); binpointIidGap.setHardwareTriggerProvider(ienergy_move_controller);    binpointIidGap.verbose=True

jenergy = ContinuousMoveEnergyIDGapBinpointScannable('jenergy', jenergy_move_controller, binpointPgmEnergy, binpointJidGap); jenergy.verbose=True
ienergy = ContinuousMoveEnergyIDGapBinpointScannable('ienergy', ienergy_move_controller, binpointDcmEnergy, binpointIidGap); ienergy.verbose=True

#Test example commands
#Hard X-ray 
#cvscan ienergy 2.60 2.85 0.001 iI0 0.5 sdc 0.5
#Soft X-ray
#cvscan jenergy 0.2 0.45 0.001 jI0 0.5 sdc 0.5
