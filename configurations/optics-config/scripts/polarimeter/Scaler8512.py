
from scannables.Scaler8512Device import Scaler8512ChannelEpicsDeviceClass;
print "-"*100
print "Set up scaler card"
print "Create RAW scalar objects: 'ca01sr','ca02sr','ca03sr','ca04sr','ca05sr','ca06sr','ca07sr','ca08sr'"

#Patch Panel U2 use the same scaler preset/trigger signal from the same scaler card
pvPatchPanelScalerTP='ME02P-EA-DET-01:SCALER:PRESET';
pvPatchPanelScalerCNT='ME02P-EA-DET-01:SCALER:STARTCOUNT';

#For Patch Panel U2
#Use the scaler Raw count
pvCA61CRAW = 'ME02P-EA-DET-01:SCALER:CH1-RAW';
pvCA62CRAW = 'ME02P-EA-DET-01:SCALER:CH2-RAW';
pvCA63CRAW = 'ME02P-EA-DET-01:SCALER:CH3-RAW';
pvCA64CRAW = 'ME02P-EA-DET-01:SCALER:CH4-RAW';
pvCA65CRAW = 'ME02P-EA-DET-01:SCALER:CH5-RAW';
pvCA66CRAW = 'ME02P-EA-DET-01:SCALER:CH6-RAW';
pvCA67CRAW = 'ME02P-EA-DET-01:SCALER:CH7-RAW';
pvCA68CRAW = 'ME02P-EA-DET-01:SCALER:CH8-RAW';

ca01sr = Scaler8512ChannelEpicsDeviceClass('ca01sr',pvPatchPanelScalerTP, pvPatchPanelScalerCNT, pvCA61CRAW);
ca02sr = Scaler8512ChannelEpicsDeviceClass('ca02sr',pvPatchPanelScalerTP, pvPatchPanelScalerCNT, pvCA62CRAW);
ca03sr = Scaler8512ChannelEpicsDeviceClass('ca03sr',pvPatchPanelScalerTP, pvPatchPanelScalerCNT, pvCA63CRAW);
ca04sr = Scaler8512ChannelEpicsDeviceClass('ca04sr',pvPatchPanelScalerTP, pvPatchPanelScalerCNT, pvCA64CRAW);
ca05sr = Scaler8512ChannelEpicsDeviceClass('ca05sr',pvPatchPanelScalerTP, pvPatchPanelScalerCNT, pvCA65CRAW);
ca06sr = Scaler8512ChannelEpicsDeviceClass('ca06sr',pvPatchPanelScalerTP, pvPatchPanelScalerCNT, pvCA66CRAW);
ca07sr = Scaler8512ChannelEpicsDeviceClass('ca07sr',pvPatchPanelScalerTP, pvPatchPanelScalerCNT, pvCA67CRAW);
ca08sr = Scaler8512ChannelEpicsDeviceClass('ca08sr',pvPatchPanelScalerTP, pvPatchPanelScalerCNT, pvCA68CRAW);

scaler=[ca01sr,ca02sr,ca03sr,ca04sr,ca05sr,ca06sr,ca07sr,ca08sr]

#acqtime = DetectorIntegrationsDevice('acqtime', [ca61sr]);
#acqtime.addDetectors([ca11sr]);
