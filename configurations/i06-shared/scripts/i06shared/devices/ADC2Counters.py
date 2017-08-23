'''
Support 'ADC2' backed by Hytec 8401 ADC with 8 channels
'''
from Diamond.PseudoDevices.Scaler8512Device import Scaler8512ChannelEpicsDeviceClass;

print "-"*100
print "Set up the Hytec 8401 ADC 8 channel device with integration layer in EPICS"
print "Create Integrated count objects: 'ca101','ca102','ca103','ca104','ca111','ca112','ca113','ca114'"
print "Create Current reading objects: 'ca101sr','ca102sr','ca103sr','ca104sr','ca111sr','ca112sr','ca113sr','ca114sr'"

pvIntegrationTime='BL06I-DI-ADC-02:SC:INTTIME';
pvTrigger='BL06I-DI-ADC-02:SC:STARTCOUNT';

pvCA101C = 'BL06I-AL-SLITS-04:I1';
pvCA102C = 'BL06I-AL-SLITS-04:I2';
pvCA103C = 'BL06J-AL-SLITS-01:I1';
pvCA104C = 'BL06J-AL-SLITS-01:I2';

pvCA111C = 'BL06I-OP-SWMIR-01:I:B';
pvCA112C = 'BL06J-DI-PHDGN-01:I';
pvCA113C = 'BL06J-DI-IONC-01:I';
pvCA114C = 'BL06J-DI-PHDGN-02:I';

#Use the ADC Current reading
ca101 = Scaler8512ChannelEpicsDeviceClass('ca101',pvIntegrationTime, pvTrigger, pvCA101C);
ca102 = Scaler8512ChannelEpicsDeviceClass('ca102',pvIntegrationTime, pvTrigger, pvCA102C);
ca103 = Scaler8512ChannelEpicsDeviceClass('ca103',pvIntegrationTime, pvTrigger, pvCA103C);
ca104 = Scaler8512ChannelEpicsDeviceClass('ca104',pvIntegrationTime, pvTrigger, pvCA104C);

ca111 = Scaler8512ChannelEpicsDeviceClass('ca111',pvIntegrationTime, pvTrigger, pvCA111C);
ca112 = Scaler8512ChannelEpicsDeviceClass('ca112',pvIntegrationTime, pvTrigger, pvCA112C);
ca113 = Scaler8512ChannelEpicsDeviceClass('ca113',pvIntegrationTime, pvTrigger, pvCA113C);
ca114 = Scaler8512ChannelEpicsDeviceClass('ca114',pvIntegrationTime, pvTrigger, pvCA114C);


adc2current=[ca101,ca102,ca103,ca104,ca111,ca112,ca113,ca114]

#Use the ADC integrated count
pvCA101Count = 'BL06I-DI-ADC-02:CH1:SUM';
pvCA102Count = 'BL06I-DI-ADC-02:CH2:SUM';
pvCA103Count = 'BL06I-DI-ADC-02:CH3:SUM';
pvCA104Count = 'BL06I-DI-ADC-02:CH4:SUM';

pvCA111Count = 'BL06I-DI-ADC-02:CH5:SUM';
pvCA112Count = 'BL06I-DI-ADC-02:CH6:SUM';
pvCA113Count = 'BL06I-DI-ADC-02:CH7:SUM';
pvCA114Count = 'BL06I-DI-ADC-02:CH8:SUM';

ca101sr = Scaler8512ChannelEpicsDeviceClass('ca101sr',pvIntegrationTime, pvTrigger, pvCA101Count);
ca102sr = Scaler8512ChannelEpicsDeviceClass('ca102sr',pvIntegrationTime, pvTrigger, pvCA102Count);
ca103sr = Scaler8512ChannelEpicsDeviceClass('ca103sr',pvIntegrationTime, pvTrigger, pvCA103Count);
ca104sr = Scaler8512ChannelEpicsDeviceClass('ca104sr',pvIntegrationTime, pvTrigger, pvCA104Count);

ca111sr = Scaler8512ChannelEpicsDeviceClass('ca111sr',pvIntegrationTime, pvTrigger, pvCA111Count);
ca112sr = Scaler8512ChannelEpicsDeviceClass('ca112sr',pvIntegrationTime, pvTrigger, pvCA112Count);
ca113sr = Scaler8512ChannelEpicsDeviceClass('ca113sr',pvIntegrationTime, pvTrigger, pvCA113Count);
ca114sr = Scaler8512ChannelEpicsDeviceClass('ca114sr',pvIntegrationTime, pvTrigger, pvCA114Count);

adc2count=[ca101sr,ca102sr,ca103sr,ca104sr,ca111sr,ca112sr,ca113sr,ca114sr]
#del ca11s

