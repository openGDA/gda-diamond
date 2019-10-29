
from Diamond.Pilatus.PilatusInfo import PilatusInfo;

from Diamond.Pilatus.ADPilatusPseudoDevice import ADPilatusPseudoDeviceClass

from Diamond.Analysis.Analyser import AnalyserDetectorClass;
from Diamond.Analysis.Analyser import AnalyserWithRectangularROIClass;

from Diamond.Analysis.Processors import DummyTwodPorcessor, MinMaxSumMeanDeviationProcessor, SumProcessor;

from gdascripts.analysis.datasetprocessor.twod.TwodGaussianPeak import TwodGaussianPeak
from gdascripts.analysis.datasetprocessor.twod.SumMaxPositionAndValue import SumMaxPositionAndValue

from gda.analysis.io import PilatusTiffLoader


print "To create pil3 as the base detector for Pilatus 100K in EH2"

pil3 = ADPilatusPseudoDeviceClass("pil3", "Area Detector", "pilatus3");
pil3.setAlive(False);
pil3.addShutter('fs');
#pil3.setFile("pilatus3","p100kImage");
pil3.setFile("pilatus3","p3Image");#Modified according to beamline scientist on 13/03/2013

#For the RCP GUI
pil3sum = AnalyserDetectorClass("pil3sum", pil3, [SumProcessor()], panelName="Area Detector", iFileLoader=PilatusTiffLoader);
pil3sum.setAlive(True);
pil3sum.readoutNexus = True

pil3stats = AnalyserDetectorClass("pil3stats", pil3, [MinMaxSumMeanDeviationProcessor()], panelName="Area Detector", iFileLoader=PilatusTiffLoader);
pil3stats.setAlive(True);
pil3stats.readoutNexus = True

pil3fit = AnalyserDetectorClass("pil3fit", pil3, [TwodGaussianPeak()], panelName="Area Detector", iFileLoader=PilatusTiffLoader);
pil3fit.setAlive(True);
pil3fit.readoutNexus = True

pil3roi = AnalyserWithRectangularROIClass("pil3roi", pil3, [MinMaxSumMeanDeviationProcessor()], panelName="Area Detector", iFileLoader=PilatusTiffLoader);
pil3roi.setAlive(True);
pil3roi.readoutNexus = True
#pil3roi.clearRoi();
#pil3roi.setRoi(0,0,100,100);
#pil3roi.addRoi(100, 100, 50, 50);
#pil3roi.createMask(0,5000000);
#pil3roi.applyMask(pil3roi.createMask(1000,5000));

pil3roisum = AnalyserWithRectangularROIClass("pil3roisum", pil3, [SumProcessor()], panelName="Area Detector", iFileLoader=PilatusTiffLoader);
pil3roisum.setAlive(True);
pil3roisum.readoutNexus = True

print "Use pilatusHeader as all Pilatus detector metadata holder"
pil3.setMetadataDevice(pilatusHeader);

i07.registerForPathUpdate(pil3)

