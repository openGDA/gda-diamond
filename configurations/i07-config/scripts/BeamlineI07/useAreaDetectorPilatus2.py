
from Diamond.Pilatus.PilatusInfo import PilatusInfo;

from Diamond.Pilatus.ADPilatusPseudoDevice import ADPilatusPseudoDeviceClass

from Diamond.Analysis.Analyser import AnalyserDetectorClass;
from Diamond.Analysis.Analyser import AnalyserWithRectangularROIClass;

from Diamond.Analysis.Processors import DummyTwodPorcessor, MinMaxSumMeanDeviationProcessor, SumProcessor;

from gdascripts.analysis.datasetprocessor.twod.TwodGaussianPeak import TwodGaussianPeak
from gdascripts.analysis.datasetprocessor.twod.SumMaxPositionAndValue import SumMaxPositionAndValue

from gda.analysis.io import PilatusTiffLoader



print "To create pil2 as the base detector for Pilatus 2M"

pil2 = ADPilatusPseudoDeviceClass("pil2", "Area Detector", "pilatus2");
pil2.setAlive(False);
pil2.addShutter('fs')
pil2.setFile("pilatus2", "p2mImage")


print "Usage: use pil2sum to find the integration"
pil2sum = AnalyserDetectorClass("pil2sum", pil2, [SumProcessor()], panelName="Area Detector", iFileLoader=PilatusTiffLoader);
pil2sum.setAlive(True);
pil2sum.readoutNexus = True

print "Usage: use pil2stats to find the key statistics values such as minium, maxium  with locations, sum, mean and standard deviation"
pil2stats = AnalyserDetectorClass("pil2stats", pil2, [MinMaxSumMeanDeviationProcessor()], panelName="Area Detector", iFileLoader=PilatusTiffLoader);
pil2stats.setAlive(True);
pil2stats.readoutNexus = True

print "Usage: use pil2fit for peak fitting"
pil2fit = AnalyserDetectorClass("pil2fit", pil2, [TwodGaussianPeak()], panelName="Area Detector", iFileLoader=PilatusTiffLoader);
pil2fit.setAlive(True);
pil2fit.readoutNexus = True

print "Usage: use pilroi for Region Of Interest operations"
print "For example: pil2roi.setRoi(starX, starY, width, height) to set up the ROI"
print "             pil2roi.getRoi(starX, starY, width, height) to get current ROI"
print "             pil2roi.createMask(low, high) to mask out pixels out of low/high region"
print "             pil2roi.setAlive(True) to enable the data display on GUI panel"
print "             pil2roi.setAlive(False) to stop data update on GUI panel"
pil2roi = AnalyserWithRectangularROIClass("pil2roi", pil2, [MinMaxSumMeanDeviationProcessor()], panelName="Area Detector", iFileLoader=PilatusTiffLoader);
pil2roi.setAlive(True);
pil2roi.readoutNexus = True
#pil2roi.clearRoi();
#pil2roi.setRoi(0,0,100,100);
#pil2roi.addRoi(100, 100, 50, 50);
#pil2roi.createMask(0,5000000);
#pil2roi.applyMask(pil2roi.createMask(1000,5000));

pil2roisum = AnalyserWithRectangularROIClass("pil2roisum", pil2, [SumProcessor()], panelName="Area Detector", iFileLoader=PilatusTiffLoader);
pil2roisum.setAlive(True);
pil2roisum.readoutNexus = True

print "Use pilatusHeader as all Pilatus detector metadata holder"
pil2.setMetadataDevice(pilatusHeader);
i07.registerForPathUpdate(pil2)


#
from Diamond.Analysis.AnalyserWithMovingRectangularROI import AnalyserWithMovingRectangularROIClass
print "Usage: use mroi for beam tracking Region Of Interest operations"
mroi = AnalyserWithMovingRectangularROIClass("mroi", pil2, [MinMaxSumMeanDeviationProcessor()], panelName="Area Detector", iFileLoader=PilatusTiffLoader);
mroi.setAlive(True); #To display the result

mroi.setAngleDevice(dummyTheta, dummyGamma); #To set the angle device that this ROI will follow
#mroi.setGammaZero(-11.736);
mroi.setGammaZero(0)
mroi.setDistance(1.800)

#mroi.clearRois()
mroi.setBeamCentre(1308, 1653)
#mroi.setBeamRoiSize(20, 40)

#mroi.setBeamRoiByCentre(1308, 1653, 10, 20)
#pos dummyGamma 0
#scan dummyTheta 0 5 1 mroi 0.1

#scan qdcd_ 0.02 0.1 0.01 mroi 1
