'''
Extracted from i10-config/scripts/scannable/continuous/try_continuous_energy.py in GDA 9.8
Created on 13 Apr 2018

@author: fy65
'''
from scannable.waveform_channel.BinpointWaveformChannelController import BinpointWaveformChannelController
from scannable.waveform_channel.McsWaveformChannelController import McsWaveformChannelController
from scannable.waveform_channel.WaveformChannelScannable import WaveformChannelScannable
from gda.device.detector.hardwaretriggerable import DummyHardwareTriggerableDetector
from scannable.continuous.ContinuousPgmEnergyMoveController import ContinuousPgmEnergyMoveController
from scannable.continuous.ContinuousMoveScannable import ContinuousMoveScannable
from scannable.continuous.ContinuousPgmGratingEnergyMoveController import ContinuousPgmGratingEnergyMoveController
from scannable.continuous.ContinuousMovePgmEnergyBinpointScannable import ContinuousMovePgmEnergyBinpointScannable
#from scannable.continuous.ContinuousMovePgmEnergyIdJawPhaseBinpointScannable import ContinuousMovePgmEnergyIdJawPhaseBinpointScannable
from scannable.continuous.ContinuousPgmGratingIDGapEnergyMoveController import ContinuousPgmGratingIDGapEnergyMoveController

from gdaserver import pgm_energy, pgm_grat_pitch, pgm_m2_pitch
from scannable.id_energys.idu_energy_gap import idu_circ_neg_energy,\
    idu_circ_pos_energy, idu_lin_hor_energy, idu_lin_ver_energy,\
    idu_lin_hor3_energy
from scannable.id_energys.idd_energy_gap import idd_circ_neg_energy,\
    idd_circ_pos_energy, idd_lin_hor_energy, idd_lin_ver_energy
from scannable.id_energys.idd_lin_energy import idd_lin_arbitrary_energy
from scannable.id_energys.idu_lin_energy import idu_lin_arbitrary_energy

print "-"*100
print "Creating scannables for constant velocity scan"
print "    1. Objects for constant velocity in energy:"
print "        1.1 'egy'                                - energy scannable used to control pgm_energy only"
print "        1.2 'mcsr16','mcsr17','mcsr18', 'mcsr19' - RASOR scannables used with energy 'egy' scannable, mapped to MCS channel 17, 18, 19, 20 respectively"
print "        1.3 'binpointGrtPitch','binpointMirPitch','binpointPgmEnergy','binpointId1JawPhase','binpointId2JawPhase','binpointMcaTime'"
print "                                                 - position capturer waveform scannables used with energy 'egy' scannable in continuous scan"
print "    2. Objects for constant velocity in PGM grating picth motor with ID moving as follower:"
print "        2.1 'egy_g'                                      - energy scannable used to control beam energy via PGM Grating pitch, PGM mirror pitch"
print "        2.2 'mcsr16_g','mcsr17_g','mcsr18_g', 'mcsr19_g' - RASOR scannables used with energy 'egy_g' scannable, mapped to MCS channel 17, 18, 19, 20 respectively"
print "        2.3 'binpointGrtPitch_g','binpointMirPitch_g','binpointPgmEnergy_g','binpointId1JawPhase_g','binpointId2JawPhase_g','binpointMcaTime_g'"
print "                                                         - position capturer waveform scannables used with energy 'egy_g' scannable in continuous scan"
print "    3. Objects for constant velocity in both PGM grating pitch motor and ID gap motor:"
print "        3.1 'egy_g_idu_circ_neg_energy'       - used in place of 'egy_g' above but for IDU negative circular polarisation"
print "        3.2 'egy_g_idu_circ_pos_energy'       - used in place of 'egy_g' above but for IDU positive circular polarisation"
print "        3.3 'egy_g_idu_lin_hor_energy'        - used in place of 'egy_g' above but for IDU linear horizontal polarisation"
print "        3.4 'egy_g_idu_lin_ver_energy'        - used in place of 'egy_g' above but for IDU linear vertical polarisation"
print "        3.5 'egy_g_idu_lin_arbitrary_energy'  - used in place of 'egy_g' above but for IDU linear arbitrary polarisation"
print "        3.6 'egy_g_idu_lin_hor3_energy'       - used in place of 'egy_g' above but for IDU linear horizontal polarisation at 3rd harmonic"
print "        3.7 'egy_g_idd_circ_neg_energy'       - used in place of 'egy_g' above but for IDD negative circular polarisation"
print "        3.8 'egy_g_idd_circ_pos_energy'       - used in place of 'egy_g' above but for IDD positive circular polarisation"
print "        3.9 'egy_g_idd_lin_hor_energy'        - used in place of 'egy_g' above but for IDD linear horizontal polarisation"
print "        3.10 'egy_g_idd_lin_ver_energy'        - used in place of 'egy_g' above but for IDD linear vertical polarisation"
print "        3.11 'egy_g_idd_lin_arbitrary_energy'  - used in place of 'egy_g' above but for IDD linear arbitrary polarisation"

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
mcsr20_g              = WaveformChannelScannable('mcsr20_g',              mcsrc,     21);                            mcsr20_g.setHardwareTriggerProvider(cemc_g);              mcsr20_g.verbose=True
mcsr21_g              = WaveformChannelScannable('mcsr21_g',              mcsrc,     22);                            mcsr21_g.setHardwareTriggerProvider(cemc_g);              mcsr21_g.verbose=True
mcsr22_g              = WaveformChannelScannable('mcsr22_g',              mcsrc,     23);                            mcsr22_g.setHardwareTriggerProvider(cemc_g);              mcsr22_g.verbose=True
mcsr23_g              = WaveformChannelScannable('mcsr23_g',              mcsrc,     24);                            mcsr23_g.setHardwareTriggerProvider(cemc_g);              mcsr23_g.verbose=True
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

#IDU Gap
cemc_g_idu_circ_neg_energy = ContinuousPgmGratingIDGapEnergyMoveController('cemc_g_idu_circ_neg_energy', pgm_grat_pitch, pgm_m2_pitch, 'BL10I-OP-PGM-01:', idu_circ_neg_energy, 'SR10I-MO-SERVC-21:'); cemc_g_idu_circ_neg_energy.verbose=True
egy_g_idu_circ_neg_energy  = ContinuousMovePgmEnergyBinpointScannable('egy_g_idu_circ_neg_energy', cemc_g_idu_circ_neg_energy, binpointGrtPitch_g, binpointMirPitch_g, binpointPgmEnergy_g);            egy_g_idu_circ_neg_energy.verbose=True

cemc_g_idu_circ_pos_energy = ContinuousPgmGratingIDGapEnergyMoveController('cemc_g_idu_circ_pos_energy', pgm_grat_pitch, pgm_m2_pitch, 'BL10I-OP-PGM-01:', idu_circ_pos_energy, 'SR10I-MO-SERVC-21:'); cemc_g_idu_circ_pos_energy.verbose=True
egy_g_idu_circ_pos_energy  = ContinuousMovePgmEnergyBinpointScannable('egy_g_idu_circ_pos_energy', cemc_g_idu_circ_pos_energy, binpointGrtPitch_g, binpointMirPitch_g, binpointPgmEnergy_g);            egy_g_idu_circ_pos_energy.verbose=True

cemc_g_idu_lin_hor_energy  = ContinuousPgmGratingIDGapEnergyMoveController('cemc_g_idu_lin_hor_energy', pgm_grat_pitch, pgm_m2_pitch, 'BL10I-OP-PGM-01:', idu_lin_hor_energy, 'SR10I-MO-SERVC-21:');    cemc_g_idu_lin_hor_energy.verbose=True
egy_g_idu_lin_hor_energy   = ContinuousMovePgmEnergyBinpointScannable('egy_g_idu_lin_hor_energy', cemc_g_idu_lin_hor_energy, binpointGrtPitch_g, binpointMirPitch_g, binpointPgmEnergy_g);               egy_g_idu_lin_hor_energy.verbose=True

cemc_g_idu_lin_ver_energy  = ContinuousPgmGratingIDGapEnergyMoveController('cemc_g_idu_lin_ver_energy', pgm_grat_pitch, pgm_m2_pitch, 'BL10I-OP-PGM-01:', idu_lin_ver_energy, 'SR10I-MO-SERVC-21:');    cemc_g_idu_lin_ver_energy.verbose=True
egy_g_idu_lin_ver_energy   = ContinuousMovePgmEnergyBinpointScannable('egy_g_idu_lin_ver_energy', cemc_g_idu_lin_ver_energy, binpointGrtPitch_g, binpointMirPitch_g, binpointPgmEnergy_g);               egy_g_idu_lin_ver_energy.verbose=True

cemc_g_idu_lin_hor3_energy  = ContinuousPgmGratingIDGapEnergyMoveController('cemc_g_idu_lin_hor3_energy', pgm_grat_pitch, pgm_m2_pitch, 'BL10I-OP-PGM-01:', idu_lin_hor3_energy, 'SR10I-MO-SERVC-21:');cemc_g_idu_lin_hor3_energy.verbose=True
egy_g_idu_lin_hor3_energy   = ContinuousMovePgmEnergyBinpointScannable('egy_g_idu_lin_hor3_energy', cemc_g_idu_lin_hor3_energy, binpointGrtPitch_g, binpointMirPitch_g, binpointPgmEnergy_g);           egy_g_idu_lin_hor3_energy.verbose=True

cemc_g_idu_lin_arbitrary_energy  = ContinuousPgmGratingIDGapEnergyMoveController('cemc_g_idu_lin_arbitrary_energy', pgm_grat_pitch, pgm_m2_pitch, 'BL10I-OP-PGM-01:', idu_lin_arbitrary_energy, 'SR10I-MO-SERVC-21:');cemc_g_idu_lin_arbitrary_energy.verbose=True
egy_g_idu_lin_arbitrary_energy   = ContinuousMovePgmEnergyBinpointScannable('egy_g_idu_lin_arbitrary_energy', cemc_g_idu_lin_arbitrary_energy, binpointGrtPitch_g, binpointMirPitch_g, binpointPgmEnergy_g);           egy_g_idu_lin_arbitrary_energy.verbose=True

#IDD Gap
cemc_g_idd_circ_neg_energy = ContinuousPgmGratingIDGapEnergyMoveController('cemc_g_idd_circ_neg_energy', pgm_grat_pitch, pgm_m2_pitch, 'BL10I-OP-PGM-01:', idd_circ_neg_energy, 'SR10I-MO-SERVC-01:'); cemc_g_idd_circ_neg_energy.verbose=True
egy_g_idd_circ_neg_energy  = ContinuousMovePgmEnergyBinpointScannable('egy_g_idd_circ_neg_energy', cemc_g_idd_circ_neg_energy, binpointGrtPitch_g, binpointMirPitch_g, binpointPgmEnergy_g);            egy_g_idd_circ_neg_energy.verbose=True

cemc_g_idd_circ_pos_energy = ContinuousPgmGratingIDGapEnergyMoveController('cemc_g_idd_circ_pos_energy', pgm_grat_pitch, pgm_m2_pitch, 'BL10I-OP-PGM-01:', idd_circ_pos_energy, 'SR10I-MO-SERVC-01:'); cemc_g_idd_circ_pos_energy.verbose=True
egy_g_idd_circ_pos_energy  = ContinuousMovePgmEnergyBinpointScannable('egy_g_idd_circ_pos_energy', cemc_g_idd_circ_pos_energy, binpointGrtPitch_g, binpointMirPitch_g, binpointPgmEnergy_g);            egy_g_idd_circ_pos_energy.verbose=True

cemc_g_idd_lin_hor_energy  = ContinuousPgmGratingIDGapEnergyMoveController('cemc_g_idd_lin_hor_energy', pgm_grat_pitch, pgm_m2_pitch, 'BL10I-OP-PGM-01:', idd_lin_hor_energy, 'SR10I-MO-SERVC-01:');    cemc_g_idd_lin_hor_energy.verbose=True
egy_g_idd_lin_hor_energy   = ContinuousMovePgmEnergyBinpointScannable('egy_g_idd_lin_hor_energy', cemc_g_idd_lin_hor_energy, binpointGrtPitch_g, binpointMirPitch_g, binpointPgmEnergy_g);               egy_g_idd_lin_hor_energy.verbose=True

cemc_g_idd_lin_ver_energy  = ContinuousPgmGratingIDGapEnergyMoveController('cemc_g_idd_lin_ver_energy', pgm_grat_pitch, pgm_m2_pitch, 'BL10I-OP-PGM-01:', idd_lin_ver_energy, 'SR10I-MO-SERVC-01:');    cemc_g_idd_lin_ver_energy.verbose=True
egy_g_idd_lin_ver_energy   = ContinuousMovePgmEnergyBinpointScannable('egy_g_idd_lin_ver_energy', cemc_g_idd_lin_ver_energy, binpointGrtPitch_g, binpointMirPitch_g, binpointPgmEnergy_g);               egy_g_idd_lin_ver_energy.verbose=True

cemc_g_idd_lin_arbitrary_energy  = ContinuousPgmGratingIDGapEnergyMoveController('cemc_g_idd_lin_arbitrary_energy', pgm_grat_pitch, pgm_m2_pitch, 'BL10I-OP-PGM-01:', idd_lin_arbitrary_energy, 'SR10I-MO-SERVC-01:');cemc_g_idd_lin_arbitrary_energy.verbose=True
egy_g_idd_lin_arbitrary_energy   = ContinuousMovePgmEnergyBinpointScannable('egy_g_idd_lin_arbitrary_energy', cemc_g_idd_lin_arbitrary_energy, binpointGrtPitch_g, binpointMirPitch_g, binpointPgmEnergy_g);           egy_g_idd_lin_arbitrary_energy.verbose=True
