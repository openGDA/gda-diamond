
from i06shared.scalers.Scaler8512Device import Scaler8512ChannelEpicsDeviceClass;
from i06shared.scalers.scaler_configuration import is_use_scaler_channel_as_detector
from i06shared.scalers.Scaler8512Detector import Scaler8512ChannelDetector

print("-"*100)
print("Set up the 8512 scaler card")
print("Create scalar objects: 'ca11s','ca12s','ca13s','ca14s','ca21s','ca22s','ca23s','ca24s','ca31s','ca32s','ca33s','ca34s','ca41s','ca42s','ca43s','ca44s'")
print("Create RAW scalar objects: 'ca11sr','ca12sr','ca13sr','ca14sr','ca21sr','ca22sr','ca23sr','ca24sr','ca31sr','ca32sr','ca33sr','ca34sr','ca41sr','ca42sr','ca43sr','ca44sr'")

pvScalerTP='BL06I-DI-8512-01:PRESET';
pvScalerCNT='BL06I-DI-8512-01:STARTCOUNT';

pvCA11C = 'BL06I-DI-IAMP-01:I1C';
pvCA12C = 'BL06I-DI-IAMP-01:I2C';
pvCA13C = 'BL06I-DI-IAMP-01:I3C';
pvCA14C = 'BL06I-DI-IAMP-01:I4C';

pvCA21C = 'BL06I-DI-IAMP-02:I1C';
pvCA22C = 'BL06I-DI-IAMP-02:I2C';
pvCA23C = 'BL06I-DI-IAMP-02:I3C';
pvCA24C = 'BL06I-DI-IAMP-02:I4C';

pvCA31C = 'BL06I-DI-IAMP-03:I1C';
pvCA32C = 'BL06I-DI-IAMP-03:I2C';
pvCA33C = 'BL06I-DI-IAMP-03:I3C';
pvCA34C = 'BL06I-DI-IAMP-03:I4C';

pvCA41C = 'BL06I-DI-IAMP-04:I1C';
pvCA42C = 'BL06I-DI-IAMP-04:I2C';
pvCA43C = 'BL06I-DI-IAMP-04:I3C';
pvCA44C = 'BL06I-DI-IAMP-04:I4C';

#Use the scaler "scaled" count
if is_use_scaler_channel_as_detector():
    ca11s = Scaler8512ChannelDetector('ca11s',pvScalerTP, pvScalerCNT, pvCA11C); ca11s.configure()
    ca12s = Scaler8512ChannelDetector('ca12s',pvScalerTP, pvScalerCNT, pvCA12C); ca12s.configure()
    ca13s = Scaler8512ChannelDetector('ca13s',pvScalerTP, pvScalerCNT, pvCA13C); ca13s.configure()
    ca14s = Scaler8512ChannelDetector('ca14s',pvScalerTP, pvScalerCNT, pvCA14C); ca14s.configure()
    
    ca21s = Scaler8512ChannelDetector('ca21s',pvScalerTP, pvScalerCNT, pvCA21C); ca21s.configure()
    ca22s = Scaler8512ChannelDetector('ca22s',pvScalerTP, pvScalerCNT, pvCA22C); ca22s.configure()
    ca23s = Scaler8512ChannelDetector('ca23s',pvScalerTP, pvScalerCNT, pvCA23C); ca23s.configure()
    ca24s = Scaler8512ChannelDetector('ca24s',pvScalerTP, pvScalerCNT, pvCA24C); ca24s.configure()
    
    ca31s = Scaler8512ChannelDetector('ca31s',pvScalerTP, pvScalerCNT, pvCA31C); ca31s.configure()
    ca32s = Scaler8512ChannelDetector('ca32s',pvScalerTP, pvScalerCNT, pvCA32C); ca32s.configure()
    ca33s = Scaler8512ChannelDetector('ca33s',pvScalerTP, pvScalerCNT, pvCA33C); ca33s.configure()
    ca34s = Scaler8512ChannelDetector('ca34s',pvScalerTP, pvScalerCNT, pvCA34C); ca34s.configure()
    
    ca41s = Scaler8512ChannelDetector('ca41s',pvScalerTP, pvScalerCNT, pvCA41C); ca41s.configure()
    ca42s = Scaler8512ChannelDetector('ca42s',pvScalerTP, pvScalerCNT, pvCA42C); ca42s.configure()
    ca43s = Scaler8512ChannelDetector('ca43s',pvScalerTP, pvScalerCNT, pvCA43C); ca43s.configure()
    ca44s = Scaler8512ChannelDetector('ca44s',pvScalerTP, pvScalerCNT, pvCA44C); ca44s.configure()
else:
    ca11s = Scaler8512ChannelEpicsDeviceClass('ca11s',pvScalerTP, pvScalerCNT, pvCA11C);
    ca12s = Scaler8512ChannelEpicsDeviceClass('ca12s',pvScalerTP, pvScalerCNT, pvCA12C);
    ca13s = Scaler8512ChannelEpicsDeviceClass('ca13s',pvScalerTP, pvScalerCNT, pvCA13C);
    ca14s = Scaler8512ChannelEpicsDeviceClass('ca14s',pvScalerTP, pvScalerCNT, pvCA14C);
    
    ca21s = Scaler8512ChannelEpicsDeviceClass('ca21s',pvScalerTP, pvScalerCNT, pvCA21C);
    ca22s = Scaler8512ChannelEpicsDeviceClass('ca22s',pvScalerTP, pvScalerCNT, pvCA22C);
    ca23s = Scaler8512ChannelEpicsDeviceClass('ca23s',pvScalerTP, pvScalerCNT, pvCA23C);
    ca24s = Scaler8512ChannelEpicsDeviceClass('ca24s',pvScalerTP, pvScalerCNT, pvCA24C);
    
    ca31s = Scaler8512ChannelEpicsDeviceClass('ca31s',pvScalerTP, pvScalerCNT, pvCA31C);
    ca32s = Scaler8512ChannelEpicsDeviceClass('ca32s',pvScalerTP, pvScalerCNT, pvCA32C);
    ca33s = Scaler8512ChannelEpicsDeviceClass('ca33s',pvScalerTP, pvScalerCNT, pvCA33C);
    ca34s = Scaler8512ChannelEpicsDeviceClass('ca34s',pvScalerTP, pvScalerCNT, pvCA34C);
    
    ca41s = Scaler8512ChannelEpicsDeviceClass('ca41s',pvScalerTP, pvScalerCNT, pvCA41C);
    ca42s = Scaler8512ChannelEpicsDeviceClass('ca42s',pvScalerTP, pvScalerCNT, pvCA42C);
    ca43s = Scaler8512ChannelEpicsDeviceClass('ca43s',pvScalerTP, pvScalerCNT, pvCA43C);
    ca44s = Scaler8512ChannelEpicsDeviceClass('ca44s',pvScalerTP, pvScalerCNT, pvCA44C);

scaler1=[ca11s,ca12s,ca13s,ca14s,ca21s,ca22s,ca23s,ca24s,ca31s,ca32s,ca33s,ca34s,ca41s,ca42s,ca43s,ca44s]

#Use the scaler Raw count
pvCA11CRAW = 'BL06I-DI-IAMP-01:I1C-RAW';
pvCA12CRAW = 'BL06I-DI-IAMP-01:I2C-RAW';
pvCA13CRAW = 'BL06I-DI-IAMP-01:I3C-RAW';
pvCA14CRAW = 'BL06I-DI-IAMP-01:I4C-RAW';

pvCA21CRAW = 'BL06I-DI-IAMP-02:I1C-RAW';
pvCA22CRAW = 'BL06I-DI-IAMP-02:I2C-RAW';
pvCA23CRAW = 'BL06I-DI-IAMP-02:I3C-RAW';
pvCA24CRAW = 'BL06I-DI-IAMP-02:I4C-RAW';

pvCA31CRAW = 'BL06I-DI-IAMP-03:I1C-RAW';
pvCA32CRAW = 'BL06I-DI-IAMP-03:I2C-RAW';
pvCA33CRAW = 'BL06I-DI-IAMP-03:I3C-RAW';
pvCA34CRAW = 'BL06I-DI-IAMP-03:I4C-RAW';

pvCA41CRAW = 'BL06I-DI-IAMP-04:I1C-RAW';
pvCA42CRAW = 'BL06I-DI-IAMP-04:I2C-RAW';
pvCA43CRAW = 'BL06I-DI-IAMP-04:I3C-RAW';
pvCA44CRAW = 'BL06I-DI-IAMP-04:I4C-RAW';

if is_use_scaler_channel_as_detector():
    ca11sr = Scaler8512ChannelDetector('ca11sr',pvScalerTP, pvScalerCNT, pvCA11CRAW); ca11sr.configure()
    ca12sr = Scaler8512ChannelDetector('ca12sr',pvScalerTP, pvScalerCNT, pvCA12CRAW); ca12sr.configure()
    ca13sr = Scaler8512ChannelDetector('ca13sr',pvScalerTP, pvScalerCNT, pvCA13CRAW); ca13sr.configure()
    ca14sr = Scaler8512ChannelDetector('ca14sr',pvScalerTP, pvScalerCNT, pvCA14CRAW); ca14sr.configure()
    
    ca21sr = Scaler8512ChannelDetector('ca21sr',pvScalerTP, pvScalerCNT, pvCA21CRAW); ca21sr.configure()
    ca22sr = Scaler8512ChannelDetector('ca22sr',pvScalerTP, pvScalerCNT, pvCA22CRAW); ca22sr.configure()
    ca23sr = Scaler8512ChannelDetector('ca23sr',pvScalerTP, pvScalerCNT, pvCA23CRAW); ca23sr.configure()
    ca24sr = Scaler8512ChannelDetector('ca24sr',pvScalerTP, pvScalerCNT, pvCA24CRAW); ca24sr.configure()
    
    ca31sr = Scaler8512ChannelDetector('ca31sr',pvScalerTP, pvScalerCNT, pvCA31CRAW); ca31sr.configure()
    ca32sr = Scaler8512ChannelDetector('ca32sr',pvScalerTP, pvScalerCNT, pvCA32CRAW); ca32sr.configure()
    ca33sr = Scaler8512ChannelDetector('ca33sr',pvScalerTP, pvScalerCNT, pvCA33CRAW); ca33sr.configure()
    ca34sr = Scaler8512ChannelDetector('ca34sr',pvScalerTP, pvScalerCNT, pvCA34CRAW); ca34sr.configure()
    
    ca41sr = Scaler8512ChannelDetector('ca41sr',pvScalerTP, pvScalerCNT, pvCA41CRAW); ca41sr.configure()
    ca42sr = Scaler8512ChannelDetector('ca42sr',pvScalerTP, pvScalerCNT, pvCA42CRAW); ca42sr.configure()
    ca43sr = Scaler8512ChannelDetector('ca43sr',pvScalerTP, pvScalerCNT, pvCA43CRAW); ca43sr.configure()
    ca44sr = Scaler8512ChannelDetector('ca44sr',pvScalerTP, pvScalerCNT, pvCA44CRAW); ca44sr.configure()
else:
    ca11sr = Scaler8512ChannelEpicsDeviceClass('ca11sr',pvScalerTP, pvScalerCNT, pvCA11CRAW);
    ca12sr = Scaler8512ChannelEpicsDeviceClass('ca12sr',pvScalerTP, pvScalerCNT, pvCA12CRAW);
    ca13sr = Scaler8512ChannelEpicsDeviceClass('ca13sr',pvScalerTP, pvScalerCNT, pvCA13CRAW);
    ca14sr = Scaler8512ChannelEpicsDeviceClass('ca14sr',pvScalerTP, pvScalerCNT, pvCA14CRAW);
    
    ca21sr = Scaler8512ChannelEpicsDeviceClass('ca21sr',pvScalerTP, pvScalerCNT, pvCA21CRAW);
    ca22sr = Scaler8512ChannelEpicsDeviceClass('ca22sr',pvScalerTP, pvScalerCNT, pvCA22CRAW);
    ca23sr = Scaler8512ChannelEpicsDeviceClass('ca23sr',pvScalerTP, pvScalerCNT, pvCA23CRAW);
    ca24sr = Scaler8512ChannelEpicsDeviceClass('ca24sr',pvScalerTP, pvScalerCNT, pvCA24CRAW);
    
    ca31sr = Scaler8512ChannelEpicsDeviceClass('ca31sr',pvScalerTP, pvScalerCNT, pvCA31CRAW);
    ca32sr = Scaler8512ChannelEpicsDeviceClass('ca32sr',pvScalerTP, pvScalerCNT, pvCA32CRAW);
    ca33sr = Scaler8512ChannelEpicsDeviceClass('ca33sr',pvScalerTP, pvScalerCNT, pvCA33CRAW);
    ca34sr = Scaler8512ChannelEpicsDeviceClass('ca34sr',pvScalerTP, pvScalerCNT, pvCA34CRAW);
    
    ca41sr = Scaler8512ChannelEpicsDeviceClass('ca41sr',pvScalerTP, pvScalerCNT, pvCA41CRAW);
    ca42sr = Scaler8512ChannelEpicsDeviceClass('ca42sr',pvScalerTP, pvScalerCNT, pvCA42CRAW);
    ca43sr = Scaler8512ChannelEpicsDeviceClass('ca43sr',pvScalerTP, pvScalerCNT, pvCA43CRAW);
    ca44sr = Scaler8512ChannelEpicsDeviceClass('ca44sr',pvScalerTP, pvScalerCNT, pvCA44CRAW);

scalar1raw=[ca11sr,ca12sr,ca13sr,ca14sr,ca21sr,ca22sr,ca23sr,ca24sr,ca31sr,ca32sr,ca33sr,ca34sr,ca41sr,ca42sr,ca43sr,ca44sr]


