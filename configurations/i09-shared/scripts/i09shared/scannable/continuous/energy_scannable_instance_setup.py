from i09shared.scannable.waveform_channel.BinpointWaveformChannelController import BinpointWaveformChannelController
from i09shared.scannable.waveform_channel.McsWaveformChannelController import McsWaveformChannelController
# ES2 Scaler controller:  BL09L-VA-SCLR-01:MCA-01:
#mcscontroller  = McsWaveformChannelController('mcscontroller', 'BL09L-VA-SCLR-01:MCA-01:', channelAdvanceInternalNotExternal=True); mcscontroller.verbose=True
# EA1 Scaler controller: BL09I-EA-SCLR-01:MCA-01:                BL09I-EA-SCLR-01:MCA-01:mca1
mcscontroller  = McsWaveformChannelController('mcscontroller', 'BL09I-EA-SCLR-01:MCA-01:', channelAdvanceInternalNotExternal=True); mcscontroller.verbose=True
# Sometimes the MCS struck scaler returns 1 fewer points than requested, this causes the binpoints to fail and the whole scan to fail.
# Adding the shortest possible time to the total count time seems to ensure that all of the required points are acquired.
mcscontroller.exposure_time_offset=0.001
# Binpoint is slaved from (triggered by) scaler (mcscontroller)    BL09J-CS-CSCAN-01:IDPGM:BINPOINTALL:TRIGGER
binpointc = BinpointWaveformChannelController('binpointc', 'BL09J-CS-CSCAN-01:', 'IDPGM:BINPOINTALL:'); binpointc.verbose=True