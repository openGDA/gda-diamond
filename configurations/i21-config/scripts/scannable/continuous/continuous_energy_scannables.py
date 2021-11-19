'''
create detector and scannable instances to be used for continuous energy scanning, i.e. cvscan

@author: Fajin Yuan
@organization: Diamond Light Source Ltd
@since 20 August 2020

'''

from scannable.continuous.continuousMovePgmEnergyIDGapBinpointScannable import ContinuousMovePgmEnergyIDGapBinpointScannable
from scannable.continuous.continuousPgmEnergyIDGapMoveController import ContinuousPgmEnergyIDGapMoveController
from scannable.waveform_channel.WaveformChannelScannable import WaveformChannelScannable
from scannable.waveform_channel.ADCWaveformChannelController import ADCWaveformChannelController
import __main__  # @UnresolvedImport
from scannable.waveform_channel.BinpointWaveformChannelController import BinpointWaveformChannelController
from gda.factory import Finder

print ("-"*100)
print ("Creating scannables for continuous energy scanning with ADCs")
print ("    Objects for constant velocity energy scan are:")
print ("    1. 'energy'   - energy scannable used to perform continuous energy scan by moving PGM energy and ID gap continuously at constant velocity")
print ("    2. 'draincurrent_c','diff1_c','fy2_c', 'm4c1_c' - scannables used in cvscan to collect count data")
print ("    3. 'binpointPgmEnergy','binpointIdGap' - position capturer waveform scannables used with 'cenergy' scannable in continuous scan")

#find the java objects
draincurrent_i = Finder.find("draincurrent_i")
diff1_i = Finder.find("diff1_i")
fy2_i = Finder.find("fy2_i")
m4c1 = Finder.find("m4c1")

# ADC controller maps to EPICS Group PV BL21I-EA-SMPL-01:ADC_ACQ_GRP: which controls all 3 ADCs at the same time
adc_controller  = ADCWaveformChannelController('adc_controller', 'BL21I-EA-SMPL-01:ADC_ACQ_GRP:'); adc_controller.verbose=True
# Binpoint controller is slaved from BL21I-EA-SMPL-01:ADC_ACQ_GRP:RESET. Only one set of PGM energy and ID gap caputure required
binpointc = BinpointWaveformChannelController('binpointc', 'BL21I-EA-SMPL-01:DC_S:'); binpointc.verbose=True
# Energy controller to provide continuous energy moving during constant velocity scanning.
energy_move_controller = ContinuousPgmEnergyIDGapMoveController('energy_move_controller', __main__.energy_s, __main__.idgap, 'SR21I-MO-SERVC-01:'); energy_move_controller.verbose=True

#ADC detector scannables used for 'cvscan', which use classic detector to save and restore device states before and after cvscan
draincurrent_c = WaveformChannelScannable('draincurrent_c', adc_controller, "BL21I-EA-SMPL-01:DC_S:DC_I:", draincurrent_i); draincurrent_c.setHardwareTriggerProvider(energy_move_controller); draincurrent_c.verbose=True
diff1_c = WaveformChannelScannable('diff1_c', adc_controller, "BL21I-EA-SMPL-01:DF_S:DFF_I:", diff1_i); diff1_c.setHardwareTriggerProvider(energy_move_controller); diff1_c.verbose=True
fy2_c = WaveformChannelScannable('fy2_c', adc_controller, "BL21I-EA-SMPL-01:F2_S:FYD_I:", fy2_i); fy2_c.setHardwareTriggerProvider(energy_move_controller); fy2_c.verbose=True
m4c1_c = WaveformChannelScannable('m4c1_c', adc_controller, "BL21I-MO-POD-01:C1_S:M4C1_I:", m4c1); m4c1_c.setHardwareTriggerProvider(energy_move_controller); m4c1_c.verbose=True
# Binpoint scannables used to capture PGM energy and ID gap for diagnosis purpose if and when required.
binpointIdGap     = WaveformChannelScannable('binpointIdGap',     binpointc, 'IDGAP:', None ); binpointIdGap.setHardwareTriggerProvider(energy_move_controller);   binpointIdGap.verbose=True
binpointPgmEnergy = WaveformChannelScannable('binpointPgmEnergy', binpointc, 'PGME:', None); binpointPgmEnergy.setHardwareTriggerProvider(energy_move_controller); binpointPgmEnergy.verbose=True

energy = ContinuousMovePgmEnergyIDGapBinpointScannable('energy', energy_move_controller, binpointPgmEnergy, binpointIdGap); energy.verbose=True

# cvscan energy 695 705 1 draincurrent_c 2 diff1_c 2 m4c1_c 2 
