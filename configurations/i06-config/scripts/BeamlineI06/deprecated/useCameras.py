
#from Diamond.AreaDetector.NdFilePluginDevice import NdFilePluginDeviceClass, NdFileWithStatPluginDeviceClass
#import Diamond.AreaDetector.ADDetectorDevice; reload(Diamond.AreaDetector.ADDetectorDevice)
from Diamond.AreaDetector.ADDetectorDevice import ADDetectorDeviceClass


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

print "Use camc1 for the Flea camera C1 on PEEM"
camc1 = ADDetectorDeviceClass('camc1', peemcam_ad, "Plot 1");
camc1.setStats(True);
camc1.setFile('CamC1Image', 'camc1');

