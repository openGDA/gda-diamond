
#from Diamond.PseudoDevices.Scaler8512DirectPV import ScalerChannelEpicsPVClass;
from Diamond.PseudoDevices.Scaler8512Device import Scaler8512ChannelEpicsDeviceClass;
from Diamond.PseudoDevices.Scaler8512Device import DetectorIntegrationsDevice;

#Both Patch Panel U1 and U2 use the same scaler preset/trigger signal from the same scaler card
pvPatchPanelScalerTP='BL06I-EA-USER-03:SCALER:PRESET';
pvPatchPanelScalerCNT='BL06I-EA-USER-03:SCALER:STARTCOUNT';


#For Mobilerack Scaler card
#Use the scaler Raw count
pvCA71CRAW = 'BL06I-EA-USER-03:SC1-RAW';
pvCA72CRAW = 'BL06I-EA-USER-03:SC2-RAW';
pvCA73CRAW = 'BL06I-EA-USER-03:SC3-RAW';
pvCA74CRAW = 'BL06I-EA-USER-03:SC4-RAW';

ca71sr = Scaler8512ChannelEpicsDeviceClass('ca71sr',pvPatchPanelScalerTP, pvPatchPanelScalerCNT, pvCA71CRAW);
ca72sr = Scaler8512ChannelEpicsDeviceClass('ca72sr',pvPatchPanelScalerTP, pvPatchPanelScalerCNT, pvCA72CRAW);
ca73sr = Scaler8512ChannelEpicsDeviceClass('ca73sr',pvPatchPanelScalerTP, pvPatchPanelScalerCNT, pvCA73CRAW);
ca74sr = Scaler8512ChannelEpicsDeviceClass('ca74sr',pvPatchPanelScalerTP, pvPatchPanelScalerCNT, pvCA74CRAW);
