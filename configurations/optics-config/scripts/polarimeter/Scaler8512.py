
from scannables.Scaler8512Device import Scaler8512ChannelEpicsDeviceClass;
print "-"*100
print "Set up scaler card"
print "Create RAW scalar objects: 'ca1sr','ca2sr','ca3sr','ca4sr','ca5sr','ca6sr','ca7sr','ca8sr'"

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

ca1sr = Scaler8512ChannelEpicsDeviceClass('ca1sr',pvPatchPanelScalerTP, pvPatchPanelScalerCNT, pvCA61CRAW);
ca2sr = Scaler8512ChannelEpicsDeviceClass('ca2sr',pvPatchPanelScalerTP, pvPatchPanelScalerCNT, pvCA62CRAW);
ca3sr = Scaler8512ChannelEpicsDeviceClass('ca3sr',pvPatchPanelScalerTP, pvPatchPanelScalerCNT, pvCA63CRAW);
ca4sr = Scaler8512ChannelEpicsDeviceClass('ca4sr',pvPatchPanelScalerTP, pvPatchPanelScalerCNT, pvCA64CRAW);
ca5sr = Scaler8512ChannelEpicsDeviceClass('ca5sr',pvPatchPanelScalerTP, pvPatchPanelScalerCNT, pvCA65CRAW);
ca6sr = Scaler8512ChannelEpicsDeviceClass('ca6sr',pvPatchPanelScalerTP, pvPatchPanelScalerCNT, pvCA66CRAW);
ca7sr = Scaler8512ChannelEpicsDeviceClass('ca7sr',pvPatchPanelScalerTP, pvPatchPanelScalerCNT, pvCA67CRAW);
ca8sr = Scaler8512ChannelEpicsDeviceClass('ca8sr',pvPatchPanelScalerTP, pvPatchPanelScalerCNT, pvCA68CRAW);

scaler=[ca1sr,ca2sr,ca3sr,ca4sr,ca5sr,ca6sr,ca7sr,ca8sr]

#acqtime = DetectorIntegrationsDevice('acqtime', [ca61sr]);
#acqtime.addDetectors([ca11sr]);
