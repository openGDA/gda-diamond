from Diamond.Peem.LeemModule import LeemModuleClass
#from Diamond.Peem.LeemModule import LeemFieldOfViewClass;
#from Diamond.Peem.UViewDetector import UViewDetectorClass;
#from Diamond.Peem.UViewDetector import UViewDetectorClassNew;
from Diamond.Peem.UViewDetector import UViewDetectorRoiClass;
#from Diamond.Utility.PeemImage import PeemImageClass

#from Diamond.Analysis.Analyser import AnalyserDetectorClass;
from Diamond.Analysis.Analyser import AnalyserWithRectangularROIClass;
from Diamond.Analysis.Processors import MinMaxSumMeanDeviationProcessor;
#from Diamond.Utility.UtilFun import UtilFunctions

#from gdascripts.analysis.datasetprocessor.twod.TwodGaussianPeak import TwodGaussianPeak
#from gdascripts.analysis.datasetprocessor.twod.SumMaxPositionAndValue import SumMaxPositionAndValue
#from gda.analysis.io import PNGLoader, TIFFImageLoader

global run, finder, alias, sleep, ConcurrentScan
global uv, testMotor1, psx, psy, uviewROI1, uviewROI2, uviewROI3, uviewROI4

ViewerPanelName = "PEEM Image"

print "="*80
print "= usePEEM starting..."
print "="*80

# Comment these out when uview (corba) or uviewnew (tcpip) are commented out in server_peem.xml:
useCorbaNotTcpip=False
if useCorbaNotTcpip:
	run('usePEEM_corba')
else:
	run('BeamlineI06/usePEEM_tcpip')

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

def acquireimagesdetector(detector, numberOfImages, newExpos):
	fl=detector.multiShot(numberOfImages, newExpos, True);
	if len(fl)==0:
		print "No image taken"
		return;
	for f in fl:
		print f;

if useCorbaNotTcpip:
	global fov
	def picture(tt):
		uvimaging()
	#	scan testMotor1 0 1 2 uv tt psx psy stv obj fov
		pictureScan = ConcurrentScan([testMotor1, 0, 1, 2, uv, tt, psx, psy, stv, obj, fov])
		pictureScan.runScan()
		uvpreview();
else:
	global leem_fov
	global leem_stv
	global leem_obj
	def picture(tt):
		uvimaging()
	#	scan testMotor1 0 1 2 uv tt psx psy stv obj fov
		pictureScan = ConcurrentScan([testMotor1, 0, 1, 2, uv, tt, psx, psy, leem_stv, leem_obj, leem_fov])
		pictureScan.runScan()
		uvpreview();

def uvpreview():
	uv.detector.setCameraInProgress(False)
	try:
		uv.setToAuto()
	except AttributeError:
		pass
	uv.setPixelClock(10)
	uv.setCollectionTime(0.1)
	uv.setImageAverage(1)
	uv.detector.setCameraInProgress(True)
	uv.detector.setCameraADC(2)

def uvimaging():
	uv.detector.setCameraInProgress(False)
	try:
		uv.setToSoft()
	except AttributeError:
		pass
	uv.setPixelClock(10)
	uv.setImageAverage(0)
	uv.detector.setCameraSequentialMode(True)
	uv.detector.setCameraADC(1)

alias("multishots")
alias("acquireimages")
alias("acquireimagesdetector")

alias("uvpreview")
alias("uvimaging")
alias("picture")

print "="*80
print "= usePEEM completed successfully"
print "="*80