'''
Support 'ADC1' backed by Hytec 8401 ADC with 8 channels
'''
from Diamond.PseudoDevices.Scaler8512Device import Scaler8512ChannelEpicsDeviceClass;

print "-"*100
print "Set up the Hytec 8401 ADC 8 channel device with integration layer in EPICS"
print "Create Integrated count objects: 'ca91','ca92','ca93','ca94','ca121','ca122','ca123','ca124'"
print "Create Current reading objects: 'ca91sr','ca92sr','ca93sr','ca94sr','ca121sr','ca122sr','ca123sr','ca124sr'"

pvIntegrationTime='BL06I-DI-ADC-01:SC:INTTIME';
pvTrigger='BL06I-DI-ADC-01:SC:STARTCOUNT';

pvCA91C = 'BL06I-DI-PHDGN-02:I:B';
pvCA92C = 'BL06I-OP-FCMIR-01:I:B';
pvCA93C = 'BL06I-DI-PHDGN-03:I:B';
pvCA94C = 'BL06I-DI-IONC-01:I:B';

pvCA121C = 'BL06I-DI-LDGN-01:I';
pvCA122C = 'BL06I-DI-LDGN-02:I';
pvCA123C = 'BL06I-OP-FSM-01:Y:ERR';
pvCA124C = 'BL06I-OP-FSM-01:X:ERR';

#Use the ADC Current reading
ca91 = Scaler8512ChannelEpicsDeviceClass('ca91',pvIntegrationTime, pvTrigger, pvCA91C);
ca92 = Scaler8512ChannelEpicsDeviceClass('ca92',pvIntegrationTime, pvTrigger, pvCA92C);
ca93 = Scaler8512ChannelEpicsDeviceClass('ca93',pvIntegrationTime, pvTrigger, pvCA93C);
ca94 = Scaler8512ChannelEpicsDeviceClass('ca94',pvIntegrationTime, pvTrigger, pvCA94C);

ca121 = Scaler8512ChannelEpicsDeviceClass('ca121',pvIntegrationTime, pvTrigger, pvCA121C);
ca122 = Scaler8512ChannelEpicsDeviceClass('ca122',pvIntegrationTime, pvTrigger, pvCA122C);
ca123 = Scaler8512ChannelEpicsDeviceClass('ca123',pvIntegrationTime, pvTrigger, pvCA123C);
ca124 = Scaler8512ChannelEpicsDeviceClass('ca124',pvIntegrationTime, pvTrigger, pvCA124C);


adc1current=[ca91,ca92,ca93,ca94,ca121,ca122,ca123,ca124]

#Use the ADC integrated count
pvCA91Count = 'BL06I-DI-ADC-01:CH5:SUM';
pvCA92Count = 'BL06I-DI-ADC-01:CH6:SUM';
pvCA93Count = 'BL06I-DI-ADC-01:CH7:SUM';
pvCA94Count = 'BL06I-DI-ADC-01:CH8:SUM';

pvCA21Count = 'BL06I-DI-ADC-01:CH1:SUM';
pvCA22Count = 'BL06I-DI-ADC-01:CH2:SUM';
pvCA23Count = 'BL06I-DI-ADC-01:CH3:SUM';
pvCA24Count = 'BL06I-DI-ADC-01:CH4:SUM';

ca91sr = Scaler8512ChannelEpicsDeviceClass('ca91sr',pvIntegrationTime, pvTrigger, pvCA91Count);
ca92sr = Scaler8512ChannelEpicsDeviceClass('ca92sr',pvIntegrationTime, pvTrigger, pvCA92Count);
ca93sr = Scaler8512ChannelEpicsDeviceClass('ca93sr',pvIntegrationTime, pvTrigger, pvCA93Count);
ca94sr = Scaler8512ChannelEpicsDeviceClass('ca94sr',pvIntegrationTime, pvTrigger, pvCA94Count);

ca121sr = Scaler8512ChannelEpicsDeviceClass('ca121sr',pvIntegrationTime, pvTrigger, pvCA21Count);
ca122sr = Scaler8512ChannelEpicsDeviceClass('ca122sr',pvIntegrationTime, pvTrigger, pvCA22Count);
ca123sr = Scaler8512ChannelEpicsDeviceClass('ca123sr',pvIntegrationTime, pvTrigger, pvCA23Count);
ca124sr = Scaler8512ChannelEpicsDeviceClass('ca124sr',pvIntegrationTime, pvTrigger, pvCA24Count);

adc1count=[ca91sr,ca92sr,ca93sr,ca94sr,ca121sr,ca122sr,ca123sr,ca124sr]
#del ca11s

