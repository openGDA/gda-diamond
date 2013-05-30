
#from Diamond.AreaDetector.NdFilePluginDevice import NdFilePluginDeviceClass, NdFileWithStatPluginDeviceClass
#import Diamond.AreaDetector.ADDetectorDevice; reload(Diamond.AreaDetector.ADDetectorDevice)
from Diamond.AreaDetector.ADDetectorDevice import ADDetectorDeviceClass
from Diamond.AreaDetector.NdArrayPluginDevice import NdArrayPluginDeviceClass, NdArrayWithStatPluginDeviceClass


#viewerName="Area Detector"
#print "Use camd7 for the Flea camera on D7"
#camd7 = NdFileWithStatPluginDeviceClass('camd7', d7cam_ad, "Plot 1");
#camd7.setFile('D7CamImage', 'camd7');

#camd7arr = NdArrayPluginDeviceClass('camd7arr', d7cam_ad, "Plot 1");
#camd7arr.setFile('D7CamImage', 'camd7arr');

#print "Use camc2 for the GIGE1 camera C2"
#camc2 = ADDetectorDeviceClass('camc2', c2cam_ad, "Plot 2");
#camc2.setFile('CamC2Image', 'camc2');
#camc2.setStats(True);
#camc2.delay=2;


###################################################
print "---------------------------------------------------------"
print "Use flea3arr for the Array plugin of Flea camera No.3"
print "Use flea4arr for the Array plugin of Flea camera No.4"
print "Use flea5arr for the Array plugin of Flea camera No.5"
#flea3 = ADDetectorDeviceClass('flea3', fleacam3_ad, "Area Detector");
flea3arr = NdArrayPluginDeviceClass('flea3arr', fleacam3_ad, "Area Detector");
#flea3.setStats(True);
flea3arr.setSave(True);
flea3arr.setAlive(False);
flea3arr.setFile('Flea3Image', 'flea3');

flea4arr = NdArrayPluginDeviceClass('flea4arr', fleacam4_ad, "Area Detector");
#flea6.setStats(True);
flea4arr.setSave(True);
flea4arr.setAlive(False);
flea4arr.setFile('Flea4Image', 'flea4');

#flea3 = ADDetectorDeviceClass('flea3', fleacam3_ad, "Area Detector");
flea5arr = NdArrayPluginDeviceClass('flea5arr', fleacam5_ad, "Area Detector");
#flea3.setStats(True);
flea5arr.setSave(True);
flea5arr.setAlive(False);
flea5arr.setFile('Flea5Image', 'flea5');

###################################################
print "---------------------------------------------------------"
print "Use flea3stat for the Statistic plugin of Flea camera No.3"
print "Use flea4stat for the Statistic plugin of Flea camera No.4"
print "Use flea5stat for the Statistic plugin of Flea camera No.5"
flea3stat = NdArrayWithStatPluginDeviceClass('flea3stat', fleacam3_ad);
flea4stat = NdArrayWithStatPluginDeviceClass('flea4stat', fleacam4_ad);
flea5stat = NdArrayWithStatPluginDeviceClass('flea5stat', fleacam5_ad);

###################################################
from Diamond.Analysis.Processors import DummyTwodPorcessor, MinMaxSumMeanDeviationProcessor, SumProcessor;
from gda.analysis.io import JPEGLoader, TIFFImageLoader, PNGLoader

f3sum = AnalyserDetectorClass("f3sum", flea3arr, [SumProcessor()], panelName="Area Detector", iFileLoader=PNGLoader);

