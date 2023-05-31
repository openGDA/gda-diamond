
from i06shared.scalers.Scaler8512Device import Scaler8512ChannelEpicsDeviceClass;
from i06shared.scalers.Scaler8512Detector import Scaler8512ChannelDetector
from i06shared.scalers.scaler_configuration import is_use_scaler_channel_as_detector

print("-"*100)
print("Set up the Patch Panel U1 scaler card")
print("Create RAW scalar objects: 'ca51sr','ca52sr','ca53sr','ca54sr'")
#Patch Panel U1 use the same scaler preset/trigger signal from the same scaler card
pvPatchPanelScalerTP = 'BL06I-DI-8512-03:PRESET';
pvPatchPanelScalerCNT = 'BL06I-DI-8512-03:STARTCOUNT';

#For Patch Panel U1
#Use the scaler Raw count
pvCA51CRAW = 'BL06I-EA-USER-01:SC1-RAW';
pvCA52CRAW = 'BL06I-EA-USER-01:SC2-RAW';
pvCA53CRAW = 'BL06I-EA-USER-01:SC3-RAW';
pvCA54CRAW = 'BL06I-EA-USER-01:SC4-RAW';

if is_use_scaler_channel_as_detector():
    ca51sr = Scaler8512ChannelDetector('ca51sr',pvPatchPanelScalerTP, pvPatchPanelScalerCNT, pvCA51CRAW); ca51sr.configure()
    ca52sr = Scaler8512ChannelDetector('ca52sr',pvPatchPanelScalerTP, pvPatchPanelScalerCNT, pvCA52CRAW); ca52sr.configure()
    ca53sr = Scaler8512ChannelDetector('ca53sr',pvPatchPanelScalerTP, pvPatchPanelScalerCNT, pvCA53CRAW); ca53sr.configure()
    ca54sr = Scaler8512ChannelDetector('ca54sr',pvPatchPanelScalerTP, pvPatchPanelScalerCNT, pvCA54CRAW); ca54sr.configure()
else:
    ca51sr = Scaler8512ChannelEpicsDeviceClass('ca51sr',pvPatchPanelScalerTP, pvPatchPanelScalerCNT, pvCA51CRAW);
    ca52sr = Scaler8512ChannelEpicsDeviceClass('ca52sr',pvPatchPanelScalerTP, pvPatchPanelScalerCNT, pvCA52CRAW);
    ca53sr = Scaler8512ChannelEpicsDeviceClass('ca53sr',pvPatchPanelScalerTP, pvPatchPanelScalerCNT, pvCA53CRAW);
    ca54sr = Scaler8512ChannelEpicsDeviceClass('ca54sr',pvPatchPanelScalerTP, pvPatchPanelScalerCNT, pvCA54CRAW);

scalar3=[ca51sr,ca52sr,ca53sr,ca54sr]

#acqtime = DetectorIntegrationsDevice('acqtime', [ca51sr]);
#acqtime.addDetectors([ca51sr]);
