import warnings
warnings.warn("the try_continuous_energy module is deprecated. All objects in this module are already imported into GDA.", 
              DeprecationWarning,
              stacklevel=2)

from scannable.waveform_channel.BinpointWaveformChannelController import BinpointWaveformChannelController
from scannable.waveform_channel.McsWaveformChannelController import McsWaveformChannelController
from scannable.waveform_channel.WaveformChannelScannable import WaveformChannelScannable
from gda.device.detector.hardwaretriggerable import DummyHardwareTriggerableDetector
from gdascripts.scan import trajscans
from gdascripts.scan.scanListener import ScanListener
from scannable.continuous.deprecated import ContinuousPgmEnergyMoveController.ContinuousPgmEnergyMoveController
from scannable.continuous.deprecated import ContinuousMoveScannable.ContinuousMoveScannable
from scannable.continuous.ContinuousPgmGratingEnergyMoveController import ContinuousPgmGratingEnergyMoveController
from scannable.continuous.deprecated import ContinuousMovePgmEnergyBinpointScannable.ContinuousMovePgmEnergyBinpointScannable
#from scannable.continuous.ContinuousMovePgmEnergyIdJawPhaseBinpointScannable import ContinuousMovePgmEnergyIdJawPhaseBinpointScannable
from org.slf4j import LoggerFactory
from gdaserver import pgm_energy, pgm_grat_pitch, pgm_m2_pitch

cemc = ContinuousPgmEnergyMoveController('cemc', pgm_energy); cemc.verbose=True
egy =  ContinuousMoveScannable('egy',     cemc);               egy.verbose=True

st = DummyHardwareTriggerableDetector('st')
st.setHardwareTriggerProvider(cemc)

# I branch counter controller:                       BL10I-DI-SCLR-01:MCA01:
mcsic  = McsWaveformChannelController(     'mcsic', 'BL10I-DI-SCLR-01:MCA01:', channelAdvanceInternalNotExternal=True); mcsic.verbose=True
# RASOR counter controller:                          ME01D-EA-SCLR-01:MCA01:
mcsrc  = McsWaveformChannelController(     'mcsrc', 'ME01D-EA-SCLR-01:MCA01:', channelAdvanceInternalNotExternal=True); mcsrc.verbose=True
# J branch counter controller:                       BL10J-DI-SCLR-01:MCAJ01:   NOTE: This doesn't appear to support MCA mode yet...
mcsjc  = McsWaveformChannelController(     'mcsjc', 'BL10J-DI-SCLR-01:MCAJ01:', channelAdvanceInternalNotExternal=True); mcsjc.verbose=True

# I branch scannables
mcsi16 = WaveformChannelScannable('mcsi16', mcsic, 17); mcsi16.setHardwareTriggerProvider(cemc); mcsi16.verbose=True
mcsi17 = WaveformChannelScannable('mcsi17', mcsic, 18); mcsi17.setHardwareTriggerProvider(cemc); mcsi17.verbose=True
mcsi18 = WaveformChannelScannable('mcsi18', mcsic, 19); mcsi18.setHardwareTriggerProvider(cemc); mcsi18.verbose=True
mcsi19 = WaveformChannelScannable('mcsi19', mcsic, 20); mcsi19.setHardwareTriggerProvider(cemc); mcsi19.verbose=True
# RASOR scannables
mcsr16 = WaveformChannelScannable('mcsr16', mcsrc, 17); mcsr16.setHardwareTriggerProvider(cemc); mcsr16.verbose=True
mcsr17 = WaveformChannelScannable('mcsr17', mcsrc, 18); mcsr17.setHardwareTriggerProvider(cemc); mcsr17.verbose=True
mcsr18 = WaveformChannelScannable('mcsr18', mcsrc, 19); mcsr18.setHardwareTriggerProvider(cemc); mcsr18.verbose=True
mcsr19 = WaveformChannelScannable('mcsr19', mcsrc, 20); mcsr19.setHardwareTriggerProvider(cemc); mcsr19.verbose=True
# J branch scannables
mcsj16 = WaveformChannelScannable('mcsj16', mcsjc, 17); mcsj16.setHardwareTriggerProvider(cemc); mcsj16.verbose=True
mcsj17 = WaveformChannelScannable('mcsj17', mcsjc, 18); mcsj17.setHardwareTriggerProvider(cemc); mcsj17.verbose=True
mcsj18 = WaveformChannelScannable('mcsj18', mcsjc, 19); mcsj18.setHardwareTriggerProvider(cemc); mcsj18.verbose=True
mcsj19 = WaveformChannelScannable('mcsj19', mcsjc, 20); mcsj19.setHardwareTriggerProvider(cemc); mcsj19.verbose=True

# Sometimes the RASOR struck scaler returns 1 fewer points than requested, this causes the binpoints to fail and the whole scan to fail.
# Adding the shortest possible time to the total count time seems to ensure that all of the required points are acquired.   
mcsrc.exposure_time_offset=0.001
# This may be needed on the other scalers too.
#mcsic.exposure_time_offset=0.001
#mcsjc.exposure_time_offset=0.001

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
# cd /dls_sw/prod/R3.14.12.3/ioc/BL10I/BL10I-CS-IOC-02/0-2/data; ./test_BinPoints_GUI.sh
# Custom1 and 2 are both currently set to return the current MCA channel number, so should always be equal to the binpount 

cemc_g = ContinuousPgmGratingEnergyMoveController(                   'cemc_g',  pgm_grat_pitch, pgm_m2_pitch, 'BL10I-OP-PGM-01:');                                       cemc_g.verbose=True

mcsr16_g              = WaveformChannelScannable('mcsr16_g',              mcsrc,     17);                            mcsr16_g.setHardwareTriggerProvider(cemc_g);              mcsr16_g.verbose=True
mcsr17_g              = WaveformChannelScannable('mcsr17_g',              mcsrc,     18);                            mcsr17_g.setHardwareTriggerProvider(cemc_g);              mcsr17_g.verbose=True
mcsr18_g              = WaveformChannelScannable('mcsr18_g',              mcsrc,     19);                            mcsr18_g.setHardwareTriggerProvider(cemc_g);              mcsr18_g.verbose=True
mcsr19_g              = WaveformChannelScannable('mcsr19_g',              mcsrc,     20);                            mcsr19_g.setHardwareTriggerProvider(cemc_g);              mcsr19_g.verbose=True
binpointGrtPitch_g    = WaveformChannelScannable('binpointGrtPitch_g',    binpointc, 'GRT:PITCH:');        binpointGrtPitch_g.setHardwareTriggerProvider(cemc_g);    binpointGrtPitch_g.verbose=True
binpointMirPitch_g    = WaveformChannelScannable('binpointMirPitch_g',    binpointc, 'MIR:PITCH:');        binpointMirPitch_g.setHardwareTriggerProvider(cemc_g);    binpointMirPitch_g.verbose=True
binpointPgmEnergy_g   = WaveformChannelScannable('binpointPgmEnergy_g',   binpointc, 'PGM:ENERGY:');      binpointPgmEnergy_g.setHardwareTriggerProvider(cemc_g);   binpointPgmEnergy_g.verbose=True
binpointId1JawPhase_g = WaveformChannelScannable('binpointId1JawPhase_g', binpointc, 'ID1:JAWPHASE:');  binpointId1JawPhase_g.setHardwareTriggerProvider(cemc_g); binpointId1JawPhase_g.verbose=True
binpointId2JawPhase_g = WaveformChannelScannable('binpointId2JawPhase_g', binpointc, 'ID2:JAWPHASE:');  binpointId2JawPhase_g.setHardwareTriggerProvider(cemc_g); binpointId2JawPhase_g.verbose=True
binpointMcaTime_g     = WaveformChannelScannable('binpointMcaTime_g',     binpointc, 'MCA:ELAPSEDTIME:');   binpointMcaTime_g.setHardwareTriggerProvider(cemc_g);     binpointMcaTime_g.verbose=True
binpointCustom1_g     = WaveformChannelScannable('binpointCustom1_g',     binpointc, 'CUSTOM1:');           binpointCustom1_g.setHardwareTriggerProvider(cemc_g);     binpointCustom1_g.verbose=True

egy_g =  ContinuousMovePgmEnergyBinpointScannable('egy_g',            cemc_g,    binpointGrtPitch_g, binpointMirPitch_g, binpointPgmEnergy_g);                            egy_g.verbose=True

# cvscan egy   695 705 1 mcsr17 2 binpointGrtPitch   binpointMirPitch   binpointPgmEnergy   binpointId1JawPhase   binpointId2JawPhase   binpointMcaTime 
# cvscan egy_g 695 705 1 mcsr17 2 binpointGrtPitch_g binpointMirPitch_g binpointPgmEnergy_g binpointId1JawPhase_g binpointId2JawPhase_g binpointMcaTime_g 

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