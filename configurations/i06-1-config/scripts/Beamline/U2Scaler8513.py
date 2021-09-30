
from Diamond.PseudoDevices.Scaler8512Device import Scaler8512ChannelEpicsDeviceClass;
from i06shared import installation
from gdascripts.pd.dummy_pds import DummyEpicsReadWritePVClass
print "-"*100
print "Set up the Patch Panel U2 scaler card"
print "Create RAW scalar objects: 'ca61sr','ca62sr','ca63sr','ca64sr','ca65sr','ca66sr','ca67sr','ca68sr'"

if installation.isLive():
    #Patch Panel U2 use the same scaler preset/trigger signal from the same scaler card
    pvPatchPanelScalerTP='BL06I-DI-8512-02:PRESET';
    pvPatchPanelScalerCNT='BL06I-DI-8512-02:STARTCOUNT';
    
    #For Patch Panel U2
    #Use the scaler Raw count
    pvCA61CRAW = 'BL06J-EA-USER-01:SC1-RAW';
    pvCA62CRAW = 'BL06J-EA-USER-01:SC2-RAW';
    pvCA63CRAW = 'BL06J-EA-USER-01:SC3-RAW';
    pvCA64CRAW = 'BL06J-EA-USER-01:SC4-RAW';
    pvCA65CRAW = 'BL06J-EA-USER-01:SC5-RAW';
    pvCA66CRAW = 'BL06J-EA-USER-01:SC6-RAW';
    pvCA67CRAW = 'BL06J-EA-USER-01:SC7-RAW';
    pvCA68CRAW = 'BL06J-EA-USER-01:SC8-RAW';
    
    ca61sr = Scaler8512ChannelEpicsDeviceClass('ca61sr',pvPatchPanelScalerTP, pvPatchPanelScalerCNT, pvCA61CRAW);
    ca62sr = Scaler8512ChannelEpicsDeviceClass('ca62sr',pvPatchPanelScalerTP, pvPatchPanelScalerCNT, pvCA62CRAW);
    ca63sr = Scaler8512ChannelEpicsDeviceClass('ca63sr',pvPatchPanelScalerTP, pvPatchPanelScalerCNT, pvCA63CRAW);
    ca64sr = Scaler8512ChannelEpicsDeviceClass('ca64sr',pvPatchPanelScalerTP, pvPatchPanelScalerCNT, pvCA64CRAW);
    ca65sr = Scaler8512ChannelEpicsDeviceClass('ca65sr',pvPatchPanelScalerTP, pvPatchPanelScalerCNT, pvCA65CRAW);
    ca66sr = Scaler8512ChannelEpicsDeviceClass('ca66sr',pvPatchPanelScalerTP, pvPatchPanelScalerCNT, pvCA66CRAW);
    ca67sr = Scaler8512ChannelEpicsDeviceClass('ca67sr',pvPatchPanelScalerTP, pvPatchPanelScalerCNT, pvCA67CRAW);
    ca68sr = Scaler8512ChannelEpicsDeviceClass('ca68sr',pvPatchPanelScalerTP, pvPatchPanelScalerCNT, pvCA68CRAW);
else:
    ca61sr = DummyEpicsReadWritePVClass('ca61sr', 0.0, 5000.0, '', '%.0f');
    ca62sr = DummyEpicsReadWritePVClass('ca62sr', 0.0, 5000.0, '', '%.0f');
    ca63sr = DummyEpicsReadWritePVClass('ca63sr', 0.0, 5000.0, '', '%.0f');
    ca64sr = DummyEpicsReadWritePVClass('ca64sr', 0.0, 5000.0, '', '%.0f');
    ca65sr = DummyEpicsReadWritePVClass('ca65sr', 0.0, 5000.0, '', '%.0f');
    ca66sr = DummyEpicsReadWritePVClass('ca66sr', 0.0, 5000.0, '', '%.0f');
    ca67sr = DummyEpicsReadWritePVClass('ca67sr', 0.0, 5000.0, '', '%.0f');
    ca68sr = DummyEpicsReadWritePVClass('ca68sr', 0.0, 5000.0, '', '%.0f');
    
scaler2=[ca61sr,ca62sr,ca63sr,ca64sr,ca65sr,ca66sr,ca67sr,ca68sr]

#acqtime = DetectorIntegrationsDevice('acqtime', [ca61sr]);
#acqtime.addDetectors([ca11sr]);
