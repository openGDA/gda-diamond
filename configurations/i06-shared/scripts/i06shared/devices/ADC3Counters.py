'''
Support 'ADC3' backed by Hytec 8401 ADC with 8 channels
'''
from i06shared.scalers.Scaler8512Device import Scaler8512ChannelEpicsDeviceClass;
from i06shared.scalers.scaler_configuration import is_use_scaler_channel_as_detector
from i06shared.scalers.Scaler8512Detector import Scaler8512ChannelDetector

print("-"*100)
print("Set up the Hytec 8401 ADC 8 channel device with integration layer in EPICS")
print("Create Current reading objects: 'ca131','ca132','ca133','ca134','ca141','ca142','ca143','ca144'")
print("Create Voltage reading objects: 'ca131s','ca132s','ca133s','ca134s','ca141s','ca142s','ca143s','ca144s'")
print("Create Integrated count objects: 'ca131sr','ca132sr','ca133sr','ca134sr','ca141sr','ca142sr','ca143sr','ca144sr'")

pvIntegrationTime='BL06I-DI-ADC-03:SC:INTTIME';
pvTrigger='BL06I-DI-ADC-03:SC:STARTCOUNT';

#Use the ADC Voltage reading
pvCA131V = 'BL06I-DI-ADC-03:CH1:I';
pvCA132V = 'BL06I-DI-ADC-03:CH2:I';
pvCA133V = 'BL06I-DI-ADC-03:CH3:I';
pvCA134V = 'BL06I-DI-ADC-03:CH4:I';

pvCA141V = 'BL06I-DI-ADC-03:CH5:I';
pvCA142V = 'BL06I-DI-ADC-03:CH6:I';
pvCA143V = 'BL06I-DI-ADC-03:CH7:I';
pvCA144V = 'BL06I-DI-ADC-03:CH8:I';

if is_use_scaler_channel_as_detector():
    ca131s = Scaler8512ChannelDetector('ca131s',pvIntegrationTime, pvTrigger, pvCA131V); ca131s.configure()
    ca132s = Scaler8512ChannelDetector('ca132s',pvIntegrationTime, pvTrigger, pvCA132V); ca132s.configure()
    ca133s = Scaler8512ChannelDetector('ca133s',pvIntegrationTime, pvTrigger, pvCA133V); ca133s.configure()
    ca134s = Scaler8512ChannelDetector('ca134s',pvIntegrationTime, pvTrigger, pvCA134V); ca134s.configure()
    
    ca141s = Scaler8512ChannelDetector('ca141s',pvIntegrationTime, pvTrigger, pvCA141V); ca141s.configure()
    ca142s = Scaler8512ChannelDetector('ca142s',pvIntegrationTime, pvTrigger, pvCA142V); ca142s.configure()
    ca143s = Scaler8512ChannelDetector('ca143s',pvIntegrationTime, pvTrigger, pvCA143V); ca143s.configure()
    ca144s = Scaler8512ChannelDetector('ca144s',pvIntegrationTime, pvTrigger, pvCA144V); ca144s.configure()
else:
    ca131s = Scaler8512ChannelEpicsDeviceClass('ca131s',pvIntegrationTime, pvTrigger, pvCA131V);
    ca132s = Scaler8512ChannelEpicsDeviceClass('ca132s',pvIntegrationTime, pvTrigger, pvCA132V);
    ca133s = Scaler8512ChannelEpicsDeviceClass('ca133s',pvIntegrationTime, pvTrigger, pvCA133V);
    ca134s = Scaler8512ChannelEpicsDeviceClass('ca134s',pvIntegrationTime, pvTrigger, pvCA134V);
    
    ca141s = Scaler8512ChannelEpicsDeviceClass('ca141s',pvIntegrationTime, pvTrigger, pvCA141V);
    ca142s = Scaler8512ChannelEpicsDeviceClass('ca142s',pvIntegrationTime, pvTrigger, pvCA142V);
    ca143s = Scaler8512ChannelEpicsDeviceClass('ca143s',pvIntegrationTime, pvTrigger, pvCA143V);
    ca144s = Scaler8512ChannelEpicsDeviceClass('ca144s',pvIntegrationTime, pvTrigger, pvCA144V);

adc3voltage=[ca131s,ca132s,ca133s,ca134s,ca141s,ca142s,ca143s,ca144s]

#Use the ADC Current reading
pvCA131C = 'BL06I-DI-ADC-03:CH1:I:UA';
pvCA132C = 'BL06I-DI-ADC-03:CH2:I:UA';
pvCA133C = 'BL06I-DI-ADC-03:CH3:I:UA';
pvCA134C = 'BL06I-DI-ADC-03:CH4:I:UA';

pvCA141C = 'BL06I-DI-ADC-03:CH5:I:UA';
pvCA142C = 'BL06I-DI-ADC-03:CH6:I:UA';
pvCA143C = 'BL06I-DI-ADC-03:CH7:I:UA';
pvCA144C = 'BL06I-DI-ADC-03:CH8:I:UA';

if is_use_scaler_channel_as_detector():
    ca131 = Scaler8512ChannelDetector('ca131',pvIntegrationTime, pvTrigger, pvCA131C); ca131.configure()
    ca132 = Scaler8512ChannelDetector('ca132',pvIntegrationTime, pvTrigger, pvCA132C); ca132.configure()
    ca133 = Scaler8512ChannelDetector('ca133',pvIntegrationTime, pvTrigger, pvCA133C); ca133.configure()
    ca134 = Scaler8512ChannelDetector('ca134',pvIntegrationTime, pvTrigger, pvCA134C); ca134.configure()
    
    ca141 = Scaler8512ChannelDetector('ca141',pvIntegrationTime, pvTrigger, pvCA141C); ca141.configure()
    ca142 = Scaler8512ChannelDetector('ca142',pvIntegrationTime, pvTrigger, pvCA142C); ca142.configure()
    ca143 = Scaler8512ChannelDetector('ca143',pvIntegrationTime, pvTrigger, pvCA143C); ca143.configure()
    ca144 = Scaler8512ChannelDetector('ca144',pvIntegrationTime, pvTrigger, pvCA144C); ca144.configure()
else:
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

if is_use_scaler_channel_as_detector():
    ca131sr = Scaler8512ChannelDetector('ca131sr',pvIntegrationTime, pvTrigger, pvCA131Count); ca131sr.configure()
    ca132sr = Scaler8512ChannelDetector('ca132sr',pvIntegrationTime, pvTrigger, pvCA132Count); ca132sr.configure()
    ca133sr = Scaler8512ChannelDetector('ca133sr',pvIntegrationTime, pvTrigger, pvCA133Count); ca133sr.configure()
    ca134sr = Scaler8512ChannelDetector('ca134sr',pvIntegrationTime, pvTrigger, pvCA134Count); ca134sr.configure()
    
    ca141sr = Scaler8512ChannelDetector('ca141sr',pvIntegrationTime, pvTrigger, pvCA141Count); ca141sr.configure()
    ca142sr = Scaler8512ChannelDetector('ca142sr',pvIntegrationTime, pvTrigger, pvCA142Count); ca142sr.configure()
    ca143sr = Scaler8512ChannelDetector('ca143sr',pvIntegrationTime, pvTrigger, pvCA143Count); ca143sr.configure()
    ca144sr = Scaler8512ChannelDetector('ca144sr',pvIntegrationTime, pvTrigger, pvCA144Count); ca144sr.configure()
else:
    ca131sr = Scaler8512ChannelEpicsDeviceClass('ca131sr',pvIntegrationTime, pvTrigger, pvCA131Count);
    ca132sr = Scaler8512ChannelEpicsDeviceClass('ca132sr',pvIntegrationTime, pvTrigger, pvCA132Count);
    ca133sr = Scaler8512ChannelEpicsDeviceClass('ca133sr',pvIntegrationTime, pvTrigger, pvCA133Count);
    ca134sr = Scaler8512ChannelEpicsDeviceClass('ca134sr',pvIntegrationTime, pvTrigger, pvCA134Count);
    
    ca141sr = Scaler8512ChannelEpicsDeviceClass('ca141sr',pvIntegrationTime, pvTrigger, pvCA141Count);
    ca142sr = Scaler8512ChannelEpicsDeviceClass('ca142sr',pvIntegrationTime, pvTrigger, pvCA142Count);
    ca143sr = Scaler8512ChannelEpicsDeviceClass('ca143sr',pvIntegrationTime, pvTrigger, pvCA143Count);
    ca144sr = Scaler8512ChannelEpicsDeviceClass('ca144sr',pvIntegrationTime, pvTrigger, pvCA144Count);

adc3count=[ca131sr,ca132sr,ca133sr,ca134sr,ca141sr,ca142sr,ca143sr,ca144sr]


