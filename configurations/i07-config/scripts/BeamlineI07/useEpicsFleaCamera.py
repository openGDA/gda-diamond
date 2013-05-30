#Usage 
from Diamond.PseudoDevices.EpicsCamera import EpicsCameraClass;

from Diamond.Analysis.DetectorAnalyser import DetectorAnalyserClass;
from Diamond.Analysis.DetectorAnalyserROI import DetectorAnalyserWithRectangularROIClass;
from Diamond.Analysis.Processors import DummyTwodPorcessor, MinMaxSumMeanDeviationProcessor;

from gdascripts.analysis.datasetprocessor.twod.TwodGaussianPeak import TwodGaussianPeak
from gdascripts.analysis.datasetprocessor.twod.SumMaxPositionAndValue import SumMaxPositionAndValue

from gda.analysis.io import PNGLoader;


pvRootCamera04='BL07I-DI-PHDGN-04:CAM';
viewerName="Area Detector";


print "-------------------------------------------------------------------"
print "Usage: use cam04, cam04stats, cam04roi for the Flea camera on D4";
cam04 = EpicsCameraClass('cam04', pvRootCamera04, viewerName);
cam04.setFile('camera', 'cam04_');
cam04.setAlive(False);

print "Usage: use dcstats to find the key statistics values such as minium, maxium  with locations, sum, mean and standard deviation"
cam04stats = DetectorAnalyserClass("cam04stats", cam04, [MinMaxSumMeanDeviationProcessor()], panelName=viewerName, iFileLoader=PNGLoader);
cam04stats.setAlive(True);

cam04roi = DetectorAnalyserWithRectangularROIClass("cam04roi", cam04, [MinMaxSumMeanDeviationProcessor()], panelName=viewerName, iFileLoader=PNGLoader);

cam04roi.setAlive(True);
cam04roi.setPassive(False);
cam04roi.clearRoi();

