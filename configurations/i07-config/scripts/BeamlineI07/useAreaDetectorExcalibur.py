from Diamond.Excalibur.ExcaliburWrapper import ExcaliburOdinI07

from Diamond.Analysis.Analyser import AnalyserDetectorClass;
from Diamond.Analysis.Analyser import AnalyserWithRectangularROIClass;

from Diamond.Analysis.Processors import DummyTwodPorcessor, MinMaxSumMeanDeviationProcessor, SumProcessor;

from gdascripts.analysis.datasetprocessor.twod.TwodGaussianPeak import TwodGaussianPeak
from gdascripts.analysis.datasetprocessor.twod.SumMaxPositionAndValue import SumMaxPositionAndValue

from gda.analysis.io import PilatusTiffLoader

print "Create exc as the base detector for Excalibur 1M"
print "WARNING This script is deprecated"
print "Old scanning Excalibur scans now use objects implemented in Java and configured in Spring"

exc = ExcaliburOdinI07("exc", "Area Detector", "excalibur");
exc.setAlive(False);
exc.addShutter('fs')
exc.setFile("exc/");
#print "             Use pil1.setFile('path/','prefix') to set the image directory and name"
#print "             Current image directory: ", pil1.getFilePath();
#print "             Current image prefix: ",    pil1.getFilePrefix();

print "Usage: use excstats to find the key statistics values such as minimum, maximum  with locations, sum, mean and standard deviation"
excstats = AnalyserDetectorClass("excstats", exc, [MinMaxSumMeanDeviationProcessor()], panelName="Area Detector", iFileLoader=PilatusTiffLoader);
excstats.setAlive(True);
excstats.readoutNexus = True


print "Usage: use excroi for Region Of Interest operations"
print "For example: excroi.setRoi(starX, starY, width, height) to set up the ROI"
print "             excroi.getRoi(starX, starY, width, height) to get current ROI"
print "             excroi.createMask(low, high) to mask out pixels out of low/high region"
print "             excroi.setAlive(True) to enable the data display on GUI panel"
print "             excroi.setAlive(False) to stop data update on GUI panel"
excroi = AnalyserWithRectangularROIClass("excroi", exc, [MinMaxSumMeanDeviationProcessor()], panelName="Area Detector", iFileLoader=PilatusTiffLoader);
excroi.setAlive(True);
excroi.readoutNexus = True

#excroi.clearRoi();
#excroi.setRoi(0,0,100,100);
#excroi.addRoi(100, 100, 50, 50);
#excroi.createMask(0,5000000);
#excroi.applyMask(excroi.createMask(1000,5000));

print "Use pilatusHeader as all Pilatus detector metadata holder"


#exc.setMetadataDevice(pilatusHeader);

i07.registerForPathUpdate(exc)


