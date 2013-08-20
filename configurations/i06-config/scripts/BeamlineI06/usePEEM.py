

#from gda.device.detector.uview import CorbaBridgeConnection, UViewImageDetector
from gda.device.detector.uview import UViewImageDetectorROI
#from gda.device.peem import ElmitecPEEM


from Diamond.Peem.LeemModule import LeemModuleClass
from Diamond.Peem.LeemModule import LeemFieldOfViewClass;
from Diamond.Peem.UViewDetector import UViewDetectorClass;
from Diamond.Peem.UViewDetector import UViewDetectorRoiClass;
from Diamond.Utility.PeemImage import PeemImageClass

from Diamond.Analysis.Analyser import AnalyserDetectorClass;
from Diamond.Analysis.Analyser import AnalyserWithRectangularROIClass;
from Diamond.Analysis.Processors import DummyTwodPorcessor, MinMaxSumMeanDeviationProcessor;
from Diamond.Utility.UtilFun import UtilFunctions

from gdascripts.analysis.datasetprocessor.twod.TwodGaussianPeak import TwodGaussianPeak
from gdascripts.analysis.datasetprocessor.twod.SumMaxPositionAndValue import SumMaxPositionAndValue
from gda.analysis.io import PNGLoader, TIFFImageLoader

print "-------------------------------------------------------------------"
print "To set up the PEEM Corba Bridge Connection"

try:
    peemBridge = finder.find("peemBridge");
    msImpl=peemBridge.connect()
except:
    exceptionType, exception, traceback=sys.exc_info();
    print "Connection to the CORBA Bridge failed. Please check!"
    logger.dump("---> ", exceptionType, exception, traceback);
    
if not peemBridge.isConnected():
    print "Connection to the CORBA Bridge failed. Please check!"
    logger.dump("Connection to the CORBA Bridge failed. Please check!");
    raise "CORBA Bridge Error";
#    return;
    

#Set up the LEEM
print "Note: Use object name 'leem' for LEEM2000 control"
leem = finder.find("leem")
leem.connect()

print "      Use object name 'ca71' for PEEM drain current monitoring";
print "      Use object name 'startVoltage' for Start Voltage control";
print "      Use object name 'objective' for Objective control";
ca71 = LeemModuleClass("ca71", leem, 42);
startVoltage = LeemModuleClass("startVoltage", leem, 38);
stv=startVoltage;

objective = LeemModuleClass("objective", leem, 11);
obj=objective;

objStigmA = LeemModuleClass("objStigmA", leem, 12);
objStigmB = LeemModuleClass("objStigmB", leem, 13);

fov = LeemFieldOfViewClass("fov", msImpl);

#Setup the UView
print "-------------------------------------------------------------------"
#PEEM UViewImage Detector
#uview = finder.find("uview")
uview.configure()

print "-------------------------------------------------------------------"
ViewerPanelName = "PEEM Image"

##Create a GDA pseudo device that use the UView detector client
uv = UViewDetectorClass("uv", ViewerPanelName, uview);
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


#Obsoleted UViewImage Region Of Interests support
uviewROI1 = UViewImageDetectorROI()
uviewROI1.setName("uviewROI1")
uviewROI1.setBaseDetector("uview")
uviewROI1.setBoundaryColor("Red")
uviewROI1.configure()

uviewROI2 = UViewImageDetectorROI()
uviewROI2.setName("uviewROI2")
uviewROI2.setBaseDetector("uview")
uviewROI2.setBoundaryColor("Green")
uviewROI2.configure()

uviewROI3 = UViewImageDetectorROI()
uviewROI3.setName("uviewROI3")
uviewROI3.setBaseDetector("uview")
uviewROI3.setBoundaryColor("Blue")
uviewROI3.configure()

uviewROI4 = UViewImageDetectorROI()
uviewROI4.setName("uviewROI4")
uviewROI4.setBaseDetector("uview")
uviewROI4.setBoundaryColor("Yellow")
uviewROI4.configure()

print "Note: Use roi* for UView Image Region Of Interests access";
roi1 = UViewDetectorRoiClass("roi1", uviewROI1);
roi2 = UViewDetectorRoiClass("roi2", uviewROI2);
roi3 = UViewDetectorRoiClass("roi3", uviewROI3);
roi4 = UViewDetectorRoiClass("roi4", uviewROI4);


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

def picture(tt):
	uvimaging()
#    scan testMotor1 0 1 2 uv tt psx psy stv obj fov
	pictureScan = ConcurrentScan([testMotor1, 0, 1, 2, uv, tt, psx, psy, stv, obj, fov])
	pictureScan.runScan()
	uvpreview();

def uvpreview():
	uv.detector.setCameraInProgress(True)
	uv.setImageAverage(0)
	uv.setCollectionTime(0.5)
	sleep(1)
	uv.setCollectionTime(0.25)
	sleep(0.5)
	uv.setCollectionTime(0.1)
	uv.setImageAverage(1)
	uv.detector.setCameraSequentialMode(False)

def uvimaging():
	uv.detector.setCameraInProgress(True)
	uv.setImageAverage(0)
	uv.detector.setCameraSequentialMode(True)

alias("multishots")
alias("acquireimages")

alias("uvpreview")
alias("uvimaging")
alias("picture")


