#Usage 
from Diamond.Pilatus.DummyAreaDetector import DummyAreaDetectorClass


from Diamond.Analysis.Analyser import AnalyserDetectorClass;
from Diamond.Analysis.Analyser import AnalyserWithRectangularROIClass;


#from Diamond.Analysis.DetectorAnalyserROI import DetectorAnalyserWithRectangularROIClass;
#from Diamond.Analysis.DetectorAnalyser import DetectorAnalyserClass;

from Diamond.Analysis.Processors import DummyTwodPorcessor, MinMaxSumMeanDeviationProcessor, SumProcessor;

from gdascripts.analysis.datasetprocessor.twod.TwodGaussianPeak import TwodGaussianPeak

from gda.analysis.io import PilatusTiffLoader
from time import sleep;

print "-------------------------------------------------------------------"
print "Usage: use dummyCamera for a dummy 2D detector";
viewerName="Plot 1"
dummyCamera = DummyAreaDetectorClass("dummyCamera", viewerName, '/dls_sw/i07/software/gda/config/scripts/Diamond/Pilatus/images100K.zip', 'tif');
dummyCamera.setFile('dummycam', 'dummyCam');
dummyCamera.setAlive(False);


print "Usage: use dcsum to find the integration of pixels from the dummy camera"
dcsum = AnalyserDetectorClass("dcsum", dummyCamera, [SumProcessor()], panelName=viewerName, iFileLoader=PilatusTiffLoader);
dcsum.setAlive(True);

print "Usage: use dcstats to find the key statistics values such as minium, maxium  with locations, sum, mean and standard deviation"
dcstats = AnalyserDetectorClass("dcstats", dummyCamera, [MinMaxSumMeanDeviationProcessor()], panelName=viewerName, iFileLoader=PilatusTiffLoader);
dcstats.setAlive(True);

print "Usage: use dcfit for peak fitting"
dcfit = AnalyserDetectorClass("dcfit", dummyCamera, [TwodGaussianPeak()], panelName=viewerName, iFileLoader=PilatusTiffLoader);
dcfit.setAlive(True);

dcroi = AnalyserWithRectangularROIClass("dcroi", dummyCamera, [MinMaxSumMeanDeviationProcessor()], panelName=viewerName, iFileLoader=PilatusTiffLoader);

dcroi.setAlive(True);
#dcroi.setPassive(False);
#dcroi.clearRoi();

#dcroi.setRoi(0,0,100,100);
#dcroi.addRoi(100, 100, 50, 50);
#dcroi.createMask(0,5000000);
#dcroi.applyMask(pil1roi.createMask(1000,5000));


from Diamond.PseudoDevices.MetadataHeaderDevice import MetadataHeaderDeviceClass
dcHeader = MetadataHeaderDeviceClass("dcHeader");
dcHeader.add([testMotor1, testMotor2, testMotor3]);

from Diamond.PseudoDevices.DummyShutter import DummyShutterClass
dummyCameraShutter = DummyShutterClass('dummyCameraShutter', delayAfterOpening=0.5, delayAfterClosing=0);

dummyCamera.setMetadataDevice(dcHeader);
dummyCamera.addShutter(dummyCameraShutter);
