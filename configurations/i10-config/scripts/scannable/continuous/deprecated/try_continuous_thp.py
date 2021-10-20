# run 'scannable/continuous/try_continuous_thp.py'
#
# Requires:
#
# run 'scannable/continuous/try_continuous_energy.py'

from mtscripts.scannable.waveform_channel.WaveformChannelScannable import \
                                          WaveformChannelScannable
from scannable.continuous.deprecated import ContinuousThpMoveController.ContinuousThpMoveController
from scannable.continuous.deprecated import ContinuousMoveThpBinpointScannable.ContinuousMoveThpBinpointScannable

from gdascripts.utils import caput_wait

global mcsrc, binpointc, TrajectoryControllerHelper, thp

ctmc = ContinuousThpMoveController('ctmc',  thp); ctmc.verbose=True

mcsr16_t              = WaveformChannelScannable('mcsr16_t',              mcsrc,     17);                            mcsr16_t.setHardwareTriggerProvider(ctmc);              mcsr16_t.verbose=True
mcsr17_t              = WaveformChannelScannable('mcsr17_t',              mcsrc,     18);                            mcsr17_t.setHardwareTriggerProvider(ctmc);              mcsr17_t.verbose=True
mcsr18_t              = WaveformChannelScannable('mcsr18_t',              mcsrc,     19);                            mcsr18_t.setHardwareTriggerProvider(ctmc);              mcsr18_t.verbose=True
mcsr19_t              = WaveformChannelScannable('mcsr19_t',              mcsrc,     20);                            mcsr19_t.setHardwareTriggerProvider(ctmc);              mcsr19_t.verbose=True
binpointCustom2_t     = WaveformChannelScannable('binpointCustom2_t',     binpointc, 'CUSTOM2:');           binpointCustom2_t.setHardwareTriggerProvider(ctmc);     binpointCustom2_t.verbose=True

thp_t =  ContinuousMoveThpBinpointScannable('thp_t', ctmc, binpointCustom2_t); thp_t.verbose=True

print "Configuring Custom2 binpoint for thp:"

caput_wait("BL10I-CS-CSCAN-01:CUSTOM2:BINPOINT:DESCRIPTION", "Custom2 - Thp", 2)
# Supported method
caput_wait("BL10I-CS-CSCAN-01:CUSTOM2:BINPOINT:NEWDATALINK.BB", "ME01D-MO-POLAN-01:THETA.RBV", 2)
caput_wait("BL10I-CS-CSCAN-01:CUSTOM2:BINPOINT:NEWDATALINK.PROC", 1, 2)

print "Creating gda cvdscan commands:"

"""
from gdascripts.scan.gdascans import Scan
from gdascripts.scan.specscans import Dscan
from gdascripts.scan.trajscans import CvMixin

class CvDScan(Dscan, CvMixin):

    def __init__(self, scanListeners = None):
        Dscan.__init__(self, scanListeners)
        self.__doc__ = Scan.__doc__.replace('scan', 'cvdscan') #@UndefinedVariable

    def _createScan(self, args):
        return self.createTrajAndPossiblyConcurrentScan(args)

cvdscan=CvDScan([scan_processor, trajectory_controller_helper]) #@UndefinedVariable
alias('cvdscan') #@UndefinedVariable
"""