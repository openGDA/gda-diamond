'''
Support 'ADC3' backed by Hytec 8401 ADC with 8 channels
'''
from Diamond.PseudoDevices.Scaler8512Device import Scaler8512ChannelEpicsDeviceClass;

print "-"*100
print "Set up the Hytec 8401 ADC 8 channel device with integration layer in EPICS"
print "Create Integrated count objects: 'ca131','ca132','ca133','ca134','ca141','ca142','ca143','ca144'"
print "Create Current reading objects: 'ca131sr','ca132sr','ca133sr','ca134sr','ca141sr','ca142sr','ca143sr','ca144sr'"

pvIntegrationTime='BL06I-DI-ADC-03:SC:INTTIME';
pvTrigger='BL06I-DI-ADC-03:SC:STARTCOUNT';

pvCA131C = 'BL06I-DI-ADC-03:CH1:I';
pvCA132C = 'BL06I-DI-ADC-03:CH2:I';
pvCA133C = 'BL06I-DI-ADC-03:CH3:I';
pvCA134C = 'BL06I-DI-ADC-03:CH4:I';

pvCA141C = 'BL06I-DI-ADC-03:CH5:I';
pvCA142C = 'BL06I-DI-ADC-03:CH6:I';
pvCA143C = 'BL06I-DI-ADC-03:CH7:I';
pvCA144C = 'BL06I-DI-ADC-03:CH8:I';

#Use the ADC Current reading
ca131 = Scaler8512ChannelEpicsDeviceClass('ca131',pvIntegrationTime, pvTrigger, pvCA131C);
ca132 = Scaler8512ChannelEpicsDeviceClass('ca132',pvIntegrationTime, pvTrigger, pvCA132C);
ca133 = Scaler8512ChannelEpicsDeviceClass('ca133',pvIntegrationTime, pvTrigger, pvCA133C);
ca134 = Scaler8512ChannelEpicsDeviceClass('ca134',pvIntegrationTime, pvTrigger, pvCA134C);

ca141 = Scaler8512ChannelEpicsDeviceClass('ca141',pvIntegrationTime, pvTrigger, pvCA141C);
ca142 = Scaler8512ChannelEpicsDeviceClass('ca142',pvIntegrationTime, pvTrigger, pvCA142C);
ca143 = Scaler8512ChannelEpicsDeviceClass('ca143',pvIntegrationTime, pvTrigger, pvCA143C);
ca144 = Scaler8512ChannelEpicsDeviceClass('ca144',pvIntegrationTime, pvTrigger, pvCA144C);


adc3current=[ca131,ca132,ca133,ca134,ca141,ca142,ca143,ca144]

#Use the ADC integrated count
pvCA131Count = 'BL06I-DI-ADC-03:CH1:SUM';
pvCA132Count = 'BL06I-DI-ADC-03:CH2:SUM';
pvCA133Count = 'BL06I-DI-ADC-03:CH3:SUM';
pvCA134Count = 'BL06I-DI-ADC-03:CH4:SUM';

pvCA141Count = 'BL06I-DI-ADC-03:CH5:SUM';
pvCA142Count = 'BL06I-DI-ADC-03:CH6:SUM';
pvCA143Count = 'BL06I-DI-ADC-03:CH7:SUM';
pvCA144Count = 'BL06I-DI-ADC-03:CH8:SUM';

ca131sr = Scaler8512ChannelEpicsDeviceClass('ca131sr',pvIntegrationTime, pvTrigger, pvCA131Count);
ca132sr = Scaler8512ChannelEpicsDeviceClass('ca132sr',pvIntegrationTime, pvTrigger, pvCA132Count);
ca133sr = Scaler8512ChannelEpicsDeviceClass('ca133sr',pvIntegrationTime, pvTrigger, pvCA133Count);
ca134sr = Scaler8512ChannelEpicsDeviceClass('ca134sr',pvIntegrationTime, pvTrigger, pvCA134Count);

ca141sr = Scaler8512ChannelEpicsDeviceClass('ca141sr',pvIntegrationTime, pvTrigger, pvCA141Count);
ca142sr = Scaler8512ChannelEpicsDeviceClass('ca142sr',pvIntegrationTime, pvTrigger, pvCA142Count);
ca143sr = Scaler8512ChannelEpicsDeviceClass('ca143sr',pvIntegrationTime, pvTrigger, pvCA143Count);
ca144sr = Scaler8512ChannelEpicsDeviceClass('ca144sr',pvIntegrationTime, pvTrigger, pvCA144Count);

adc3count=[ca131sr,ca132sr,ca133sr,ca134sr,ca141sr,ca142sr,ca143sr,ca144sr]
#del ca11s

