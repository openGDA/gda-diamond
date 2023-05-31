from i06shared.scalers.Scaler8512Device import Scaler8512ChannelEpicsDeviceClass;
from i06shared.scalers.Scaler8512Detector import Scaler8512ChannelDetector
from i06shared.scalers.scaler_configuration import is_use_scaler_channel_as_detector

#Both Patch Panel U1 and U2 use the same scaler preset/trigger signal from the same scaler card
pvPatchPanelScalerTP = 'BL06I-EA-USER-03:SCALER:PRESET';
pvPatchPanelScalerCNT = 'BL06I-EA-USER-03:SCALER:STARTCOUNT';

#For Mobilerack Scaler card
#Use the scaler Raw count
pvCA71CRAW = 'BL06I-EA-USER-03:SC1-RAW';
pvCA72CRAW = 'BL06I-EA-USER-03:SC2-RAW';
pvCA73CRAW = 'BL06I-EA-USER-03:SC3-RAW';
pvCA74CRAW = 'BL06I-EA-USER-03:SC4-RAW';

if is_use_scaler_channel_as_detector():
    ca71sr = Scaler8512ChannelDetector('ca71sr',pvPatchPanelScalerTP, pvPatchPanelScalerCNT, pvCA71CRAW); ca71sr.configure()
    ca72sr = Scaler8512ChannelDetector('ca72sr',pvPatchPanelScalerTP, pvPatchPanelScalerCNT, pvCA72CRAW); ca72sr.configure()
    ca73sr = Scaler8512ChannelDetector('ca73sr',pvPatchPanelScalerTP, pvPatchPanelScalerCNT, pvCA73CRAW); ca73sr.configure()
    ca74sr = Scaler8512ChannelDetector('ca74sr',pvPatchPanelScalerTP, pvPatchPanelScalerCNT, pvCA74CRAW); ca74sr.configure()
else:
    ca71sr = Scaler8512ChannelEpicsDeviceClass('ca71sr',pvPatchPanelScalerTP, pvPatchPanelScalerCNT, pvCA71CRAW);
    ca72sr = Scaler8512ChannelEpicsDeviceClass('ca72sr',pvPatchPanelScalerTP, pvPatchPanelScalerCNT, pvCA72CRAW);
    ca73sr = Scaler8512ChannelEpicsDeviceClass('ca73sr',pvPatchPanelScalerTP, pvPatchPanelScalerCNT, pvCA73CRAW);
    ca74sr = Scaler8512ChannelEpicsDeviceClass('ca74sr',pvPatchPanelScalerTP, pvPatchPanelScalerCNT, pvCA74CRAW);
