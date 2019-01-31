import installation
print "-"*100
print "Create scalar objects: 'ca01sr','ca02sr','ca03sr','ca04sr','ca05sr','ca06sr','ca07sr','ca08sr'"

if installation.isLive():
    from scannables.Scaler8512Device import Scaler8512ChannelEpicsDeviceClass;
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
else:
    from gda.device.monitor import DummyEpicsMonitorDouble
    ca01sr = DummyEpicsMonitorDouble();ca01sr.setName("ca01sr");ca01sr.setLowerLimit(0.0);ca01sr.setUpperLimit(10.0);ca01sr.setIncrement(0.15)
    ca02sr = DummyEpicsMonitorDouble();ca02sr.setName('ca02sr');ca02sr.setLowerLimit(0.0);ca02sr.setUpperLimit(10.0);ca02sr.setIncrement(0.20);
    ca03sr = DummyEpicsMonitorDouble();ca03sr.setName('ca03sr');ca03sr.setLowerLimit(0.0);ca03sr.setUpperLimit(10.0);ca03sr.setIncrement(0.12);
    ca04sr = DummyEpicsMonitorDouble();ca04sr.setName('ca04sr');ca04sr.setLowerLimit(0.0);ca04sr.setUpperLimit(10.0);ca04sr.setIncrement(0.13);
    ca05sr = DummyEpicsMonitorDouble();ca05sr.setName('ca05sr');ca05sr.setLowerLimit(0.0);ca05sr.setUpperLimit(10.0);ca05sr.setIncrement(0.14);
    ca06sr = DummyEpicsMonitorDouble();ca06sr.setName('ca06sr');ca06sr.setLowerLimit(0.0);ca06sr.setUpperLimit(10.0);ca06sr.setIncrement(0.16);
    ca07sr = DummyEpicsMonitorDouble();ca07sr.setName('ca07sr');ca07sr.setLowerLimit(0.0);ca07sr.setUpperLimit(10.0);ca07sr.setIncrement(0.17);
    ca08sr = DummyEpicsMonitorDouble();ca08sr.setName('ca08sr');ca08sr.setLowerLimit(0.0);ca08sr.setUpperLimit(10.0);ca08sr.setIncrement(0.18);

scaler=[ca01sr, ca02sr, ca03sr, ca04sr, ca05sr, ca06sr, ca07sr, ca08sr];

#acqtime = DetectorIntegrationsDevice('acqtime', [ca61sr]);
#acqtime.addDetectors([ca11sr]);
