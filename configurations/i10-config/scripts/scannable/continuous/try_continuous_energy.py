# run 'scannable/continuous/try_continuous_energy.py'

from mtscripts.scannable.waveform_channel.BinpointWaveformChannelController import \
                                          BinpointWaveformChannelController
from mtscripts.scannable.waveform_channel.McsWaveformChannelController import \
                                          McsWaveformChannelController
from mtscripts.scannable.waveform_channel.WaveformChannelScannable import \
                                          WaveformChannelScannable
from gda.device.detector.hardwaretriggerable import \
                    DummyHardwareTriggerableDetector
from gdascripts.scan import trajscans
from gdascripts.scan.scanListener import ScanListener
from scannable.continuous.ContinuousPgmEnergyMoveController import \
                          ContinuousPgmEnergyMoveController
from scannable.continuous.ContinuousMoveScannable import \
                          ContinuousMoveScannable
from scannable.continuous.ContinuousPgmGratingEnergyMoveController import \
                          ContinuousPgmGratingEnergyMoveController
from org.slf4j import LoggerFactory

global pgm_energy
global pgm_grat_pitch, pgm_m2_pitch

cemc = ContinuousPgmEnergyMoveController('cemc', pgm_energy); cemc.verbose=True
egy =  ContinuousMoveScannable('egy',     cemc);               egy.verbose=True

st = DummyHardwareTriggerableDetector('st')
st.setHardwareTriggerProvider(cemc)

# I branch counter:                                  BL10I-DI-SCLR-01:MCA01:
mcsic  = McsWaveformChannelController(     'mcsic', 'BL10I-DI-SCLR-01:MCA01:', channelAdvanceInternalNotExternal=True); mcsic.verbose=True
mcsi16 = WaveformChannelScannable('mcsi16', mcsic, 17);            mcsi16.setHardwareTriggerProvider(cemc);             mcsi16.verbose=True
mcsi17 = WaveformChannelScannable('mcsi17', mcsic, 18);            mcsi17.setHardwareTriggerProvider(cemc);             mcsi17.verbose=True
mcsi18 = WaveformChannelScannable('mcsi18', mcsic, 19);            mcsi18.setHardwareTriggerProvider(cemc);             mcsi18.verbose=True
mcsi19 = WaveformChannelScannable('mcsi19', mcsic, 20);            mcsi19.setHardwareTriggerProvider(cemc);             mcsi19.verbose=True

# RASOR counter:                                     ME01D-EA-SCLR-01:MCA01:
mcsrc  = McsWaveformChannelController(     'mcsrc', 'ME01D-EA-SCLR-01:MCA01:', channelAdvanceInternalNotExternal=True); mcsrc.verbose=True
mcsr16 = WaveformChannelScannable('mcsr16', mcsrc, 17);            mcsr16.setHardwareTriggerProvider(cemc);             mcsr16.verbose=True
mcsr17 = WaveformChannelScannable('mcsr17', mcsrc, 18);            mcsr17.setHardwareTriggerProvider(cemc);             mcsr17.verbose=True
mcsr18 = WaveformChannelScannable('mcsr18', mcsrc, 19);            mcsr18.setHardwareTriggerProvider(cemc);             mcsr18.verbose=True
mcsr19 = WaveformChannelScannable('mcsr19', mcsrc, 20);            mcsr19.setHardwareTriggerProvider(cemc);             mcsr19.verbose=True

# This doesn't appear to support MCA mode yet...
# J branch counter:                                  BL10J-DI-SCLR-01:MCAJ01:
mcsjc  = McsWaveformChannelController(     'mcsjc', 'BL10J-DI-SCLR-01:MCAJ01:', channelAdvanceInternalNotExternal=True); mcsjc.verbose=True
mcsj16 = WaveformChannelScannable('mcsj16', mcsjc, 17);            mcsj16.setHardwareTriggerProvider(cemc);              mcsj16.verbose=True
mcsj17 = WaveformChannelScannable('mcsj17', mcsjc, 18);            mcsj17.setHardwareTriggerProvider(cemc);              mcsj17.verbose=True
mcsj18 = WaveformChannelScannable('mcsj18', mcsjc, 19);            mcsj18.setHardwareTriggerProvider(cemc);              mcsj18.verbose=True
mcsj19 = WaveformChannelScannable('mcsj19', mcsjc, 20);            mcsj19.setHardwareTriggerProvider(cemc);              mcsj19.verbose=True

# Binpoint is slaved from (triggered by) RASOR scaler (mcsrc)                        'BL10I-CS-CSCAN-01:'
binpointc           = BinpointWaveformChannelController(             'binpointc', 'BL10I-CS-CSCAN-01:', 'IDPGM:BINPOINTALL:');                                        binpointc.verbose=True
binpointGrtPitch    = WaveformChannelScannable('binpointGrtPitch',    binpointc, 'GRT:PITCH:');          binpointGrtPitch.setHardwareTriggerProvider(cemc);    binpointGrtPitch.verbose=True
binpointMirPitch    = WaveformChannelScannable('binpointMirPitch',    binpointc, 'MIR:PITCH:');          binpointMirPitch.setHardwareTriggerProvider(cemc);    binpointMirPitch.verbose=True
binpointPgmEnergy   = WaveformChannelScannable('binpointPgmEnergy',   binpointc, 'PGM:ENERGY:');        binpointPgmEnergy.setHardwareTriggerProvider(cemc);   binpointPgmEnergy.verbose=True
binpointId1JawPhase = WaveformChannelScannable('binpointId1JawPhase', binpointc, 'ID1:JAWPHASE:');    binpointId1JawPhase.setHardwareTriggerProvider(cemc); binpointId1JawPhase.verbose=True
binpointId2JawPhase = WaveformChannelScannable('binpointId2JawPhase', binpointc, 'ID2:JAWPHASE:');    binpointId2JawPhase.setHardwareTriggerProvider(cemc); binpointId2JawPhase.verbose=True
binpointMcaTime     = WaveformChannelScannable('binpointMcaTime',     binpointc, 'MCA:ELAPSEDTIME:');     binpointMcaTime.setHardwareTriggerProvider(cemc);     binpointMcaTime.verbose=True
binpointCustom1     = WaveformChannelScannable('binpointCustom1',     binpointc, 'CUSTOM1:');             binpointCustom1.setHardwareTriggerProvider(cemc);     binpointCustom1.verbose=True
binpointCustom2     = WaveformChannelScannable('binpointCustom2',     binpointc, 'CUSTOM2:');             binpointCustom2.setHardwareTriggerProvider(cemc);     binpointCustom2.verbose=True

cemc_g = ContinuousPgmGratingEnergyMoveController(                   'cemc_g',  pgm_grat_pitch, pgm_m2_pitch);                                                           cemc_g.verbose=True
egy_g =  ContinuousMoveScannable('egy_g',                             cemc_g);                                                                                            egy_g.verbose=True

mcsr17_g            = WaveformChannelScannable('mcsr17_g', mcsrc, 18);                                           mcsr17_g.setHardwareTriggerProvider(cemc_g);            mcsr17_g.verbose=True
binpointPgmEnergy_g = WaveformChannelScannable('binpointPgmEnergy_g', binpointc, 'PGM:ENERGY:');      binpointPgmEnergy_g.setHardwareTriggerProvider(cemc_g); binpointPgmEnergy_g.verbose=True

# cvscan egy 695 705 1 mcs1 mcs17 mcs16 2 binpointGrtPitch binpointMirPitch binpointPgmEnergy binpointId1JawPhase binpointId2JawPhase binpointMcaTime 

class TrajectoryControllerHelper(ScanListener):
    def __init__(self): # motors, maybe also detector to set the delay time
        self.logger = LoggerFactory.getLogger("TrajectoryControllerHelper")

    def prepareForScan(self):
        self.logger.info("prepareForScan()")

    def update(self, scanObject):
        self.logger.info("update(%r)" % scanObject)


trajscans.DEFAULT_SCANNABLES_FOR_TRAJSCANS = [meta] # @UndefinedVariable

trajectory_controller_helper = TrajectoryControllerHelper()

print "Creating gda cvscan commands:"
# These will need more classes added to /uk.ac.gda.core/scripts/gdascripts/scan/trajscans.py
#trajcscan=trajscans.TrajCscan([scan_processor, trajectory_controller_helper]) #@UndefinedVariable
#trajrscan=trajscans.TrajRscan([scan_processor, trajectory_controller_helper]) #@UndefinedVariable
cvscan=trajscans.CvScan([scan_processor, trajectory_controller_helper]) #@UndefinedVariable
alias('cvscan') #@UndefinedVariable

# E.g. cvscan egy 695 705 1 mcs1 mcs17 mcs16 2

""" Tests:
    10ev at 2 seconds per 1ev 'step & 10ev at .2 seconds per .1ev 'step:

    scan pgm_energy 695 705 1 macr1 macr16 macr17 2       11 points, 28 seconds (18:32:36 to 18:33:24)
    scan pgm_energy 695 705 .1 macr1 macr16 macr17 .2    101 points, 3 minutes 15 seconds (18:35:57 to 18:39:12
    
    cvscan egy 695 705 1 mcs1 mcs16 mcs17 2                11 points, 34 seconds (18:41:48 to 18:42:22)
    cvscan egy 695 705 .1 mcs1 mcs16 mcs17 .2            101? points, 36 seconds (18:45:09 to 18:45:45)
"""