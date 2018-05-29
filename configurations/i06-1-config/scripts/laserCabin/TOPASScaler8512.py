
from Diamond.PseudoDevices.Scaler8512Device import Scaler8512ChannelEpicsDeviceClass;
print "-"*100
print "Set up the Patch Panel TOPAS scaler card"
print "Create RAW scalar objects: 'ca81sr','ca82sr','ca83sr','ca84sr','ca85sr','ca86sr','ca87sr','ca88sr'"

#Patch Panel TOPAS use the same scaler preset/trigger signal from the same scaler card
pvPatchPanelScalerTP='BL06I-EA-8512-01:PRESET';
pvPatchPanelScalerCNT='BL06I-EA-8512-01:STARTCOUNT';

#For Patch Panel TOPAS
#Use the scaler Raw count
pvCA81CRAW = 'BL06I-EA-HIRES-01:SC1-RAW';
pvCA82CRAW = 'BL06I-EA-HIRES-01:SC2-RAW';
pvCA83CRAW = 'BL06I-EA-HIRES-01:SC3-RAW';
pvCA84CRAW = 'BL06I-EA-HIRES-01:SC4-RAW';
pvCA85CRAW = 'BL06I-EA-HIRES-01:SC5-RAW';
pvCA86CRAW = 'BL06I-EA-HIRES-01:SC6-RAW';
pvCA87CRAW = 'BL06I-EA-HIRES-01:SC7-RAW';
pvCA88CRAW = 'BL06I-EA-HIRES-01:SC8-RAW';

ca81sr = Scaler8512ChannelEpicsDeviceClass('ca81sr',pvPatchPanelScalerTP, pvPatchPanelScalerCNT, pvCA81CRAW);
ca82sr = Scaler8512ChannelEpicsDeviceClass('ca82sr',pvPatchPanelScalerTP, pvPatchPanelScalerCNT, pvCA82CRAW);
ca83sr = Scaler8512ChannelEpicsDeviceClass('ca83sr',pvPatchPanelScalerTP, pvPatchPanelScalerCNT, pvCA83CRAW);
ca84sr = Scaler8512ChannelEpicsDeviceClass('ca84sr',pvPatchPanelScalerTP, pvPatchPanelScalerCNT, pvCA84CRAW);
ca85sr = Scaler8512ChannelEpicsDeviceClass('ca85sr',pvPatchPanelScalerTP, pvPatchPanelScalerCNT, pvCA85CRAW);
ca86sr = Scaler8512ChannelEpicsDeviceClass('ca86sr',pvPatchPanelScalerTP, pvPatchPanelScalerCNT, pvCA86CRAW);
ca87sr = Scaler8512ChannelEpicsDeviceClass('ca87sr',pvPatchPanelScalerTP, pvPatchPanelScalerCNT, pvCA87CRAW);
ca88sr = Scaler8512ChannelEpicsDeviceClass('ca88sr',pvPatchPanelScalerTP, pvPatchPanelScalerCNT, pvCA88CRAW);

topas_scaler=[ca81sr,ca82sr,ca83sr,ca84sr,ca85sr,ca86sr,ca87sr,ca88sr]

#acqtime = DetectorIntegrationsDevice('acqtime', [ca81sr]);
#acqtime.addDetectors([ca81sr]);
