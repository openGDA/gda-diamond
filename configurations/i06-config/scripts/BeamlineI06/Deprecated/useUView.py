
from Diamond.Peem.PEEMModule import PEEMModuleClass;
from Diamond.Peem.UViewDetector import UViewDetectorClass;
from Diamond.Utility.PeemImage import PeemImageClass

from Diamond.Analysis.Analyser import AnalyserDetectorClass;
from Diamond.Analysis.Analyser import AnalyserWithRectangularROIClass;


from Diamond.Analysis.Processors import DummyTwodPorcessor, MinMaxSumMeanDeviationProcessor;

from gdascripts.analysis.datasetprocessor.twod.TwodGaussianPeak import TwodGaussianPeak
from gdascripts.analysis.datasetprocessor.twod.SumMaxPositionAndValue import SumMaxPositionAndValue

from gda.analysis.io import PNGLoader, TIFFImageLoader


ViewerPanelName = "PEEM Image"
print "-------------------------------------------------------------------"


print "-------------------------------------------------------------------"
detectorUView = finder.find("uview");

##Create a GDA pseudo device that use the UView detector client
uv = UViewDetectorClass("uv", ViewerPanelName, detectorUView);
#uv.setFileFormat('png', 2); imageLoader=PNGLoader;
uv.setFileFormat('tif'); imageLoader=TIFFImageLoader;
uv.setAlive(False);

#print "Usage: use nuv1stats to find the key statistics values such as minium, maxium  with locations, sum, mean and standard deviation"
#uvstats = AnalyserDetectorClass("nuvstats", uv, [MinMaxSumMeanDeviationProcessor()], panelName=ViewerPanelName, iFileLoader=imageLoader);
#nuvstats.setAlive(True);

#print "Usage: use nuv1fit for peak fitting"
#uvfit = AnalyserDetectorClass("nuv1fit", uv, [TwodGaussianPeak()], panelName=ViewerPanelName, iFileLoader=imageLoader);
#nuvfit.setAlive(True);

print "Usage: use uvroi for Region Of Interest operations"
print "For example: uvroi.setRoi(starX, starY, width, height) to set up the ROI"
print "             uvroi.getRoi(starX, starY, width, height) to get current ROI from GUI"
print "             uvroi.createMask(low, high) to mask out pixels out of low/high region"
print "             uvroi.setAlive(True|False) to enable|disable the data display on GUI panel"
uvroi = AnalyserWithRectangularROIClass("uvroi", uv, [MinMaxSumMeanDeviationProcessor()], panelName=ViewerPanelName, iFileLoader=imageLoader);

#uvroi.setAlive(True);
#uvroi.setPassive(False);

#uv1roi.clearRoi();
#uv1roi.setRoi(0,0,100,100);
#uv1roi.addRoi(100, 100, 50, 50);
#uv1roi.createMask(0,5000000);
#uv1roi.applyMask(nuv1roi.createMask(1000,5000));


def multishots(numberOfImages, newExpos):
    fl=uv.multiShot(numberOfImages, newExpos, False);
    if len(fl)==0:
        print "No image taken"
        return;
    for f in fl:
        print f;
        

    
def acquireimages(numberOfImages, newExpos):
    fl=uv.multiShot(numberOfImages, newExpos, True);
    if len(fl)==0:
        print "No image taken"
        return;
    for f in fl:
        print f;

alias("multishots")
alias("acquireimages")




#The old roi thing
#from Diamond.PseudoDevices.UViewDetector import UViewDetectorClass;
from Diamond.PseudoDevices.UViewDetector import UViewDetectorROIClass;
print "Note: Use roi* for UView Image Region Of Interests access";
roi1 = UViewDetectorROIClass("roi1", "uviewROI1");
roi2 = UViewDetectorROIClass("roi2", "uviewROI2");
roi3 = UViewDetectorROIClass("roi3", "uviewROI3");
roi4 = UViewDetectorROIClass("roi4", "uviewROI4");
