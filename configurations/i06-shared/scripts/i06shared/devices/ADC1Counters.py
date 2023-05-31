'''
Support 'ADC1' backed by Hytec 8401 ADC with 8 channels
'''
from i06shared.scalers.Scaler8512Device import Scaler8512ChannelEpicsDeviceClass;
from i06shared.scalers.scaler_configuration import is_use_scaler_channel_as_detector
from i06shared.scalers.Scaler8512Detector import Scaler8512ChannelDetector

print("-"*100)
print("Set up the Hytec 8401 ADC 8 channel device with integration layer in EPICS")
print("Create Current reading objects: 'ca91','ca92','ca93','ca94','ca121','ca122','ca123','ca124'")
print("Create Voltage reading objects: 'ca91s','ca92s','ca93s','ca94s','ca121s','ca122s','ca123s','ca124s'")
print("Create Integrated count objects: 'ca91sr','ca92sr','ca93sr','ca94sr','ca121sr','ca122sr','ca123sr','ca124sr'")

pvIntegrationTime = 'BL06I-DI-ADC-01:SC:INTTIME';
pvTrigger = 'BL06I-DI-ADC-01:SC:STARTCOUNT';

pvCA91V = 'BL06I-DI-LDGN-01:I';
pvCA92V = 'BL06I-DI-LDGN-02:I';
pvCA93V = 'BL06I-OP-SM-01:I';
pvCA94V = 'BL06I-OP-SM-02:I';

pvCA101V = 'BL06I-DI-PHDGN-02:I:B';
pvCA102V = 'BL06I-OP-FCMIR-01:I:B';
pvCA103V = 'BL06I-DI-PHDGN-03:I:B';
pvCA104V = 'BL06I-DI-IONC-01:I:B';

#Use the ADC Voltage reading
if is_use_scaler_channel_as_detector():
    ca91s = Scaler8512ChannelDetector('ca91s', pvIntegrationTime, pvTrigger, pvCA91V); ca91s.configure()
    ca92s = Scaler8512ChannelDetector('ca92s', pvIntegrationTime, pvTrigger, pvCA92V); ca92s.configure()
    ca93s = Scaler8512ChannelDetector('ca93s', pvIntegrationTime, pvTrigger, pvCA93V); ca93s.configure()
    ca94s = Scaler8512ChannelDetector('ca94s', pvIntegrationTime, pvTrigger, pvCA94V); ca94s.configure()
    
    ca101s = Scaler8512ChannelDetector('ca101s', pvIntegrationTime, pvTrigger, pvCA101V); ca101s.configure()
    ca102s = Scaler8512ChannelDetector('ca102s', pvIntegrationTime, pvTrigger, pvCA102V); ca102s.configure()
    ca103s = Scaler8512ChannelDetector('ca103s', pvIntegrationTime, pvTrigger, pvCA103V); ca103s.configure()
    ca104s = Scaler8512ChannelDetector('ca104s', pvIntegrationTime, pvTrigger, pvCA104V); ca104s.configure()
else:
    ca91s = Scaler8512ChannelEpicsDeviceClass('ca91s', pvIntegrationTime, pvTrigger, pvCA91V);
    ca92s = Scaler8512ChannelEpicsDeviceClass('ca92s', pvIntegrationTime, pvTrigger, pvCA92V);
    ca93s = Scaler8512ChannelEpicsDeviceClass('ca93s', pvIntegrationTime, pvTrigger, pvCA93V);
    ca94s = Scaler8512ChannelEpicsDeviceClass('ca94s', pvIntegrationTime, pvTrigger, pvCA94V);
    
    ca101s = Scaler8512ChannelEpicsDeviceClass('ca101s', pvIntegrationTime, pvTrigger, pvCA101V);
    ca102s = Scaler8512ChannelEpicsDeviceClass('ca102s', pvIntegrationTime, pvTrigger, pvCA102V);
    ca103s = Scaler8512ChannelEpicsDeviceClass('ca103s', pvIntegrationTime, pvTrigger, pvCA103V);
    ca104s = Scaler8512ChannelEpicsDeviceClass('ca104s', pvIntegrationTime, pvTrigger, pvCA104V);

adc1voltage=[ca91s,ca92s,ca93s,ca94s,ca101s,ca102s,ca103s,ca104s]

# ADC Current reading
pvCA91C = 'BL06I-DI-LDGN-01:I:UA';
pvCA92C = 'BL06I-DI-LDGN-02:I:UA';
pvCA93C = 'BL06I-OP-SM-01:I:UA';
pvCA94C = 'BL06I-OP-SM-02:I:UA';

pvCA101C = 'BL06I-DI-PHDGN-02:I:B:UA';
pvCA102C = 'BL06I-OP-FCMIR-01:I:B:UA';
pvCA103C = 'BL06I-DI-PHDGN-03:I:B:UA';
pvCA104C = 'BL06I-DI-IONC-01:I:B:UA';

#Use the ADC Current reading
if is_use_scaler_channel_as_detector():
    ca91 = Scaler8512ChannelDetector('ca91', pvIntegrationTime, pvTrigger, pvCA91C); ca91.configure()
    ca92 = Scaler8512ChannelDetector('ca92', pvIntegrationTime, pvTrigger, pvCA92C); ca92.configure()
    ca93 = Scaler8512ChannelDetector('ca93', pvIntegrationTime, pvTrigger, pvCA93C); ca93.configure()
    ca94 = Scaler8512ChannelDetector('ca94', pvIntegrationTime, pvTrigger, pvCA94C); ca94.configure()
    
    ca101 = Scaler8512ChannelDetector('ca101', pvIntegrationTime, pvTrigger, pvCA101C); ca101.configure()
    ca102 = Scaler8512ChannelDetector('ca102', pvIntegrationTime, pvTrigger, pvCA102C); ca102.configure()
    ca103 = Scaler8512ChannelDetector('ca103', pvIntegrationTime, pvTrigger, pvCA103C); ca103.configure()
    ca104 = Scaler8512ChannelDetector('ca104', pvIntegrationTime, pvTrigger, pvCA104C); ca104.configure()
else:
    ca91 = Scaler8512ChannelEpicsDeviceClass('ca91', pvIntegrationTime, pvTrigger, pvCA91C);
    ca92 = Scaler8512ChannelEpicsDeviceClass('ca92', pvIntegrationTime, pvTrigger, pvCA92C);
    ca93 = Scaler8512ChannelEpicsDeviceClass('ca93', pvIntegrationTime, pvTrigger, pvCA93C);
    ca94 = Scaler8512ChannelEpicsDeviceClass('ca94', pvIntegrationTime, pvTrigger, pvCA94C);
    
    ca101 = Scaler8512ChannelEpicsDeviceClass('ca101', pvIntegrationTime, pvTrigger, pvCA101C);
    ca102 = Scaler8512ChannelEpicsDeviceClass('ca102', pvIntegrationTime, pvTrigger, pvCA102C);
    ca103 = Scaler8512ChannelEpicsDeviceClass('ca103', pvIntegrationTime, pvTrigger, pvCA103C);
    ca104 = Scaler8512ChannelEpicsDeviceClass('ca104', pvIntegrationTime, pvTrigger, pvCA104C);

adc1current = [ca91, ca92, ca93, ca94, ca101,ca102,ca103,ca104]

#Use the ADC integrated count
pvCA91Count = 'BL06I-DI-ADC-01:CH1:SUM';
pvCA92Count = 'BL06I-DI-ADC-01:CH2:SUM';
pvCA93Count = 'BL06I-DI-ADC-01:CH3:SUM';
pvCA94Count = 'BL06I-DI-ADC-01:CH4:SUM';

pvCA101Count = 'BL06I-DI-ADC-01:CH5:SUM';
pvCA102Count = 'BL06I-DI-ADC-01:CH6:SUM';
pvCA103Count = 'BL06I-DI-ADC-01:CH7:SUM';
pvCA104Count = 'BL06I-DI-ADC-01:CH8:SUM';

if is_use_scaler_channel_as_detector():
    ca91sr = Scaler8512ChannelDetector('ca91sr',pvIntegrationTime, pvTrigger, pvCA91Count); ca91sr.configure()
    ca92sr = Scaler8512ChannelDetector('ca92sr',pvIntegrationTime, pvTrigger, pvCA92Count); ca92sr.configure()
    ca93sr = Scaler8512ChannelDetector('ca93sr',pvIntegrationTime, pvTrigger, pvCA93Count); ca93sr.configure()
    ca94sr = Scaler8512ChannelDetector('ca94sr',pvIntegrationTime, pvTrigger, pvCA94Count); ca94sr.configure()
    
    ca101sr = Scaler8512ChannelDetector('ca101sr',pvIntegrationTime, pvTrigger, pvCA101Count); ca101sr.configure()
    ca102sr = Scaler8512ChannelDetector('ca102sr',pvIntegrationTime, pvTrigger, pvCA102Count); ca102sr.configure()
    ca103sr = Scaler8512ChannelDetector('ca103sr',pvIntegrationTime, pvTrigger, pvCA103Count); ca103sr.configure()
    ca104sr = Scaler8512ChannelDetector('ca104sr',pvIntegrationTime, pvTrigger, pvCA104Count); ca104sr.configure()
else:
    ca91sr = Scaler8512ChannelEpicsDeviceClass('ca91sr',pvIntegrationTime, pvTrigger, pvCA91Count);
    ca92sr = Scaler8512ChannelEpicsDeviceClass('ca92sr',pvIntegrationTime, pvTrigger, pvCA92Count);
    ca93sr = Scaler8512ChannelEpicsDeviceClass('ca93sr',pvIntegrationTime, pvTrigger, pvCA93Count);
    ca94sr = Scaler8512ChannelEpicsDeviceClass('ca94sr',pvIntegrationTime, pvTrigger, pvCA94Count);
    
    ca101sr = Scaler8512ChannelEpicsDeviceClass('ca101sr',pvIntegrationTime, pvTrigger, pvCA101Count);
    ca102sr = Scaler8512ChannelEpicsDeviceClass('ca102sr',pvIntegrationTime, pvTrigger, pvCA102Count);
    ca103sr = Scaler8512ChannelEpicsDeviceClass('ca103sr',pvIntegrationTime, pvTrigger, pvCA103Count);
    ca104sr = Scaler8512ChannelEpicsDeviceClass('ca104sr',pvIntegrationTime, pvTrigger, pvCA104Count);

adc1count=[ca91sr,ca92sr,ca93sr,ca94sr,ca101sr,ca102sr,ca103sr,ca104sr]


