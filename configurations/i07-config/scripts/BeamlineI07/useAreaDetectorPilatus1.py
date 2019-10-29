
from Diamond.Pilatus.PilatusInfo import PilatusInfo;

from Diamond.Pilatus.ADPilatusPseudoDevice import ADPilatusPseudoDeviceClass

from Diamond.Analysis.Analyser import AnalyserDetectorClass;
from Diamond.Analysis.Analyser import AnalyserWithRectangularROIClass;

from Diamond.Analysis.Processors import DummyTwodPorcessor, MinMaxSumMeanDeviationProcessor, SumProcessor;

from gdascripts.analysis.datasetprocessor.twod.TwodGaussianPeak import TwodGaussianPeak
from gdascripts.analysis.datasetprocessor.twod.SumMaxPositionAndValue import SumMaxPositionAndValue

from gda.analysis.io import PilatusTiffLoader

print "To create pil1 as the base detector for Pilatus 100K in EH1"

pil1 = ADPilatusPseudoDeviceClass("pil1", "Area Detector", "pilatus1");
pil1.setAlive(False);
pil1.addShutter('fs')
pil1.setFile("pilatus1/","p100kImage");
#print "             Use pil1.setFile('path/','prefix') to set the image directory and name"
#print "             Current image directory: ", pil1.getFilePath();
#print "             Current image prefix: ",    pil1.getFilePrefix();


print "Usage: use pilXsum to find the integration"
pil1sum = AnalyserDetectorClass("pil1sum", pil1, [SumProcessor()], panelName="Area Detector", iFileLoader=PilatusTiffLoader);
pil1sum.setAlive(True);
pil1sum.readoutNexus = True

print "Usage: use pilXstats to find the key statistics values such as minium, maxium  with locations, sum, mean and standard deviation"
pil1stats = AnalyserDetectorClass("pil1stats", pil1, [MinMaxSumMeanDeviationProcessor()], panelName="Area Detector", iFileLoader=PilatusTiffLoader);
pil1stats.setAlive(True);
pil1stats.readoutNexus = True

print "Usage: use pilXfit for peak fitting"
pil1fit = AnalyserDetectorClass("pil1fit", pil1, [TwodGaussianPeak()], panelName="Area Detector", iFileLoader=PilatusTiffLoader);
pil1fit.setAlive(True);
pil1fit.readoutNexus = True

print "Usage: use pilXroi for Region Of Interest operations"
print "For example: pil1roi.setRoi(starX, starY, width, height) to set up the ROI"
print "             pil1roi.getRoi(starX, starY, width, height) to get current ROI"
print "             pil1roi.createMask(low, high) to mask out pixels out of low/high region"
print "             pil1roi.setAlive(True) to enable the data display on GUI panel"
print "             pil1roi.setAlive(False) to stop data update on GUI panel"
pil1roi = AnalyserWithRectangularROIClass("pil1roi", pil1, [MinMaxSumMeanDeviationProcessor()], panelName="Area Detector", iFileLoader=PilatusTiffLoader);
pil1roi.setAlive(True);
pil1roi.readoutNexus = True
#pil1roi.clearRoi();
#pil1roi.setRoi(0,0,100,100);
#pil1roi.addRoi(100, 100, 50, 50);
#pil1roi.createMask(0,5000000);
#pil1roi.applyMask(pil1roi.createMask(1000,5000));

pil1roisum = AnalyserWithRectangularROIClass("pil1roisum", pil1, [SumProcessor()], panelName="Area Detector", iFileLoader=PilatusTiffLoader);
pil1roisum.setAlive(True);
pil1roisum.readoutNexus = True


print "Use pilatusHeader as all Pilatus detector metadata holder"
pil1.setMetadataDevice(pilatusHeader);

i07.registerForPathUpdate(pil1)

