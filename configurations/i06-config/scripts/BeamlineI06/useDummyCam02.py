#Usage 
from Diamond.Pilatus.DummyAreaDetector import DummyAreaDetectorClass;

from Diamond.Analysis.Analyser import AnalyserDetectorClass;
from Diamond.Analysis.Analyser import AnalyserWithRectangularROIClass;

from Diamond.Analysis.Processors import DummyTwodPorcessor, MinMaxSumMeanDeviationProcessor;

from gdascripts.analysis.datasetprocessor.twod.TwodGaussianPeak import TwodGaussianPeak
from gdascripts.analysis.datasetprocessor.twod.SumMaxPositionAndValue import SumMaxPositionAndValue

from gda.analysis.io import PilatusTiffLoader
from time import sleep;

print "-------------------------------------------------------------------"
print "Usage: use dummyCamera for a dummy 2D detector";
viewerName="PEEM Image"
dummyCamera = DummyAreaDetectorClass("dummyCamera", viewerName, '/scratch/Dev/gdaDev/gda-config/i07/scripts/Diamond/Pilatus/images100K.zip', 'tif');
dummyCamera.setFile('dummycam', 'dummyCam');
dummyCamera.setAlive(False);


print "Usage: use dcstats to find the key statistics values such as minium, maxium  with locations, sum, mean and standard deviation"
dcstats = AnalyserDetectorClass("dcstats", dummyCamera, [MinMaxSumMeanDeviationProcessor()], panelName=viewerName, iFileLoader=PilatusTiffLoader);
dcstats.setAlive(True);

print "Usage: use dcfit for peak fitting"
dcfit = AnalyserDetectorClass("dcfit", dummyCamera, [TwodGaussianPeak()], panelName=viewerName, iFileLoader=PilatusTiffLoader);
dcfit.setAlive(True);

dcroi = AnalyserWithRectangularROIClass("dcroi", dummyCamera, [MinMaxSumMeanDeviationProcessor()], panelName=viewerName, iFileLoader=PilatusTiffLoader);

dcroi.setAlive(True);
dcroi.clearRoi();

#dcroi.setRoi(0,0,100,100);
#dcroi.addRoi(100, 100, 50, 50);
#dcroi.createMask(0,5000000);
#dcroi.applyMask(pil1roi.createMask(1000,5000));

