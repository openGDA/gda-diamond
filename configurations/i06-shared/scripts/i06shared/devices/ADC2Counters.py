'''
Support 'ADC2' backed by Hytec 8401 ADC with 8 channels
'''
from i06shared.scalers.Scaler8512Device import Scaler8512ChannelEpicsDeviceClass;
from i06shared.scalers.Scaler8512Detector import Scaler8512ChannelDetector
from i06shared.scalers.scaler_configuration import is_use_scaler_channel_as_detector

print("-"*100)
print("Set up the Hytec 8401 ADC 8 channel device with integration layer in EPICS")
print("Create Current reading objects: 'ca111','ca112','ca113','ca114','ca121','ca122','ca123','ca124'")
print("Create Voltage reading objects: 'ca111s','ca112s','ca113s','ca114s','ca121s','ca122s','ca123s','ca124s'")
print("Create Integrated count objects: 'ca111sr','ca112sr','ca113sr','ca114sr','ca121sr','ca122sr','ca123sr','ca124sr'")

pvIntegrationTime='BL06I-DI-ADC-02:SC:INTTIME';
pvTrigger='BL06I-DI-ADC-02:SC:STARTCOUNT';

pvCA111V = 'BL06I-AL-SLITS-04:I1';
pvCA112V = 'BL06I-AL-SLITS-04:I2';
pvCA113V = 'BL06J-AL-SLITS-01:I1';
pvCA114V = 'BL06J-AL-SLITS-01:I2';

pvCA121V = 'BL06I-OP-SWMIR-01:I:B';
pvCA122V = 'BL06J-DI-PHDGN-01:I';
pvCA123V = 'BL06J-DI-IONC-01:I';
pvCA124V = 'BL06J-DI-PHDGN-02:I';

#Use the ADC Voltage reading
if is_use_scaler_channel_as_detector():
    ca111s = Scaler8512ChannelDetector('ca111s',pvIntegrationTime, pvTrigger, pvCA111V); ca111s.configure()
    ca112s = Scaler8512ChannelDetector('ca112s',pvIntegrationTime, pvTrigger, pvCA112V); ca112s.configure()
    ca113s = Scaler8512ChannelDetector('ca113s',pvIntegrationTime, pvTrigger, pvCA113V); ca113s.configure()
    ca114s = Scaler8512ChannelDetector('ca114s',pvIntegrationTime, pvTrigger, pvCA114V); ca114s.configure()
    
    ca121s = Scaler8512ChannelDetector('ca121s',pvIntegrationTime, pvTrigger, pvCA121V); ca121s.configure()
    ca122s = Scaler8512ChannelDetector('ca122s',pvIntegrationTime, pvTrigger, pvCA122V); ca122s.configure()
    ca123s = Scaler8512ChannelDetector('ca123s',pvIntegrationTime, pvTrigger, pvCA123V); ca123s.configure()
    ca124s = Scaler8512ChannelDetector('ca124s',pvIntegrationTime, pvTrigger, pvCA124V); ca124s.configure()
else:
    ca111s = Scaler8512ChannelEpicsDeviceClass('ca111s',pvIntegrationTime, pvTrigger, pvCA111V);
    ca112s = Scaler8512ChannelEpicsDeviceClass('ca112s',pvIntegrationTime, pvTrigger, pvCA112V);
    ca113s = Scaler8512ChannelEpicsDeviceClass('ca113s',pvIntegrationTime, pvTrigger, pvCA113V);
    ca114s = Scaler8512ChannelEpicsDeviceClass('ca114s',pvIntegrationTime, pvTrigger, pvCA114V);
    
    ca121s = Scaler8512ChannelEpicsDeviceClass('ca121s',pvIntegrationTime, pvTrigger, pvCA121V);
    ca122s = Scaler8512ChannelEpicsDeviceClass('ca122s',pvIntegrationTime, pvTrigger, pvCA122V);
    ca123s = Scaler8512ChannelEpicsDeviceClass('ca123s',pvIntegrationTime, pvTrigger, pvCA123V);
    ca124s = Scaler8512ChannelEpicsDeviceClass('ca124s',pvIntegrationTime, pvTrigger, pvCA124V);

adc2voltage = [ca111s,ca112s,ca113s,ca114s,ca121s,ca122s,ca123s,ca124s]

#Use the ADC Current reading
pvCA111C = 'BL06I-AL-SLITS-04:I1:UA';
pvCA112C = 'BL06I-AL-SLITS-04:I2:UA';
pvCA113C = 'BL06J-AL-SLITS-01:I1:UA';
pvCA114C = 'BL06J-AL-SLITS-01:I2:UA';

pvCA121C = 'BL06I-OP-SWMIR-01:I:B:UA';
pvCA122C = 'BL06J-DI-PHDGN-01:I:UA';
pvCA123C = 'BL06J-DI-IONC-01:I:UA';
pvCA124C = 'BL06J-DI-PHDGN-02:I:UA';

#Use the ADC Current reading
if is_use_scaler_channel_as_detector():
    ca111 = Scaler8512ChannelDetector('ca111',pvIntegrationTime, pvTrigger, pvCA111C); ca111.configure()
    ca112 = Scaler8512ChannelDetector('ca112',pvIntegrationTime, pvTrigger, pvCA112C); ca112.configure()
    ca113 = Scaler8512ChannelDetector('ca113',pvIntegrationTime, pvTrigger, pvCA113C); ca113.configure()
    ca114 = Scaler8512ChannelDetector('ca114',pvIntegrationTime, pvTrigger, pvCA114C); ca114.configure()
    
    ca121 = Scaler8512ChannelDetector('ca121',pvIntegrationTime, pvTrigger, pvCA121C); ca121.configure()
    ca122 = Scaler8512ChannelDetector('ca122',pvIntegrationTime, pvTrigger, pvCA122C); ca122.configure()
    ca123 = Scaler8512ChannelDetector('ca123',pvIntegrationTime, pvTrigger, pvCA123C); ca123.configure()
    ca124 = Scaler8512ChannelDetector('ca124',pvIntegrationTime, pvTrigger, pvCA124C); ca124.configure()
else:
    ca111 = Scaler8512ChannelEpicsDeviceClass('ca111',pvIntegrationTime, pvTrigger, pvCA111C);
    ca112 = Scaler8512ChannelEpicsDeviceClass('ca112',pvIntegrationTime, pvTrigger, pvCA112C);
    ca113 = Scaler8512ChannelEpicsDeviceClass('ca113',pvIntegrationTime, pvTrigger, pvCA113C);
    ca114 = Scaler8512ChannelEpicsDeviceClass('ca114',pvIntegrationTime, pvTrigger, pvCA114C);
    
    ca121 = Scaler8512ChannelEpicsDeviceClass('ca121',pvIntegrationTime, pvTrigger, pvCA121C);
    ca122 = Scaler8512ChannelEpicsDeviceClass('ca122',pvIntegrationTime, pvTrigger, pvCA122C);
    ca123 = Scaler8512ChannelEpicsDeviceClass('ca123',pvIntegrationTime, pvTrigger, pvCA123C);
    ca124 = Scaler8512ChannelEpicsDeviceClass('ca124',pvIntegrationTime, pvTrigger, pvCA124C);

adc2current=[ca111,ca112,ca113,ca114,ca121,ca122,ca123,ca124]

#Use the ADC integrated count
pvCA111Count = 'BL06I-DI-ADC-02:CH1:SUM';
pvCA112Count = 'BL06I-DI-ADC-02:CH2:SUM';
pvCA113Count = 'BL06I-DI-ADC-02:CH3:SUM';
pvCA114Count = 'BL06I-DI-ADC-02:CH4:SUM';

pvCA121Count = 'BL06I-DI-ADC-02:CH5:SUM';
pvCA122Count = 'BL06I-DI-ADC-02:CH6:SUM';
pvCA123Count = 'BL06I-DI-ADC-02:CH7:SUM';
pvCA124Count = 'BL06I-DI-ADC-02:CH8:SUM';

if is_use_scaler_channel_as_detector():
    ca111sr = Scaler8512ChannelEpicsDeviceClass('ca111sr',pvIntegrationTime, pvTrigger, pvCA111Count); ca111sr.configure()
    ca112sr = Scaler8512ChannelEpicsDeviceClass('ca112sr',pvIntegrationTime, pvTrigger, pvCA112Count); ca112sr.configure()
    ca113sr = Scaler8512ChannelEpicsDeviceClass('ca113sr',pvIntegrationTime, pvTrigger, pvCA113Count); ca113sr.configure()
    ca114sr = Scaler8512ChannelEpicsDeviceClass('ca114sr',pvIntegrationTime, pvTrigger, pvCA114Count); ca114sr.configure()
    
    ca121sr = Scaler8512ChannelEpicsDeviceClass('ca121sr',pvIntegrationTime, pvTrigger, pvCA121Count); ca121sr.configure()
    ca122sr = Scaler8512ChannelEpicsDeviceClass('ca122sr',pvIntegrationTime, pvTrigger, pvCA122Count); ca122sr.configure()
    ca123sr = Scaler8512ChannelEpicsDeviceClass('ca123sr',pvIntegrationTime, pvTrigger, pvCA123Count); ca123sr.configure()
    ca124sr = Scaler8512ChannelEpicsDeviceClass('ca124sr',pvIntegrationTime, pvTrigger, pvCA124Count); ca124sr.configure()
else:
    ca111sr = Scaler8512ChannelEpicsDeviceClass('ca111sr',pvIntegrationTime, pvTrigger, pvCA111Count);
    ca112sr = Scaler8512ChannelEpicsDeviceClass('ca112sr',pvIntegrationTime, pvTrigger, pvCA112Count);
    ca113sr = Scaler8512ChannelEpicsDeviceClass('ca113sr',pvIntegrationTime, pvTrigger, pvCA113Count);
    ca114sr = Scaler8512ChannelEpicsDeviceClass('ca114sr',pvIntegrationTime, pvTrigger, pvCA114Count);
    
    ca121sr = Scaler8512ChannelEpicsDeviceClass('ca121sr',pvIntegrationTime, pvTrigger, pvCA121Count);
    ca122sr = Scaler8512ChannelEpicsDeviceClass('ca122sr',pvIntegrationTime, pvTrigger, pvCA122Count);
    ca123sr = Scaler8512ChannelEpicsDeviceClass('ca123sr',pvIntegrationTime, pvTrigger, pvCA123Count);
    ca124sr = Scaler8512ChannelEpicsDeviceClass('ca124sr',pvIntegrationTime, pvTrigger, pvCA124Count);

adc2count=[ca111sr,ca112sr,ca113sr,ca114sr,ca121sr,ca122sr,ca123sr,ca124sr]


