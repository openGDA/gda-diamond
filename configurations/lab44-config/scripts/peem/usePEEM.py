from Peem.UViewDetector import UViewDetectorRoiClass;
from Diamond.Analysis.Analyser import AnalyserWithRectangularROIClass;
from Diamond.Analysis.Processors import MinMaxSumMeanDeviationProcessor;
from peem.leem_instances import leem_fov, leem_obj, leem_stv
from gda.scan import ConcurrentScan
from gda.jython.commands.GeneralCommands import alias
#from Diamond.Utility.UtilFun import UtilFunctions
#from gdascripts.analysis.datasetprocessor.twod.TwodGaussianPeak import TwodGaussianPeak
#from gdascripts.analysis.datasetprocessor.twod.SumMaxPositionAndValue import SumMaxPositionAndValue
#from gda.analysis.io import PNGLoader, TIFFImageLoader

#global run, alias, sleep, ConcurrentScan
#global testMotor1, psx, psy
import __main__  # @UnresolvedImport

ViewerPanelName = "PEEM Image"

print "="*80
print "= usePEEM starting..."
print "="*80

from peem.usePEEM_tcpip import uv, uviewROI1, uviewROI2, uviewROI3, uviewROI4, imageLoader

print "Usage: use uvroi for Region Of Interest operations"
print "For example: uvroi.setRoi(starX, starY, width, height) to set up the ROI"
print "             uvroi.getRoi(starX, starY, width, height) to get current ROI from GUI"
print "             uvroi.createMask(low, high) to mask out pixels out of low/high region"
print "             uvroi.setAlive(True|False) to enable|disable the data display on GUI panel"
uvroi = AnalyserWithRectangularROIClass("uvroi", uv, [MinMaxSumMeanDeviationProcessor()], panelName=ViewerPanelName, iFileLoader=imageLoader);
#uvroi.setAlive(True);
#uvroi.setPassive(False);

print "Note: Use roi1, roi2, roi3, roi4 for UView Image Region Of Interests access";
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




def picture(tt):
	uvimaging()
	#	scan testMotor1 0 1 2 uv tt psx psy stv obj fov
	pictureScan = ConcurrentScan([__main__.testMotor1, 0, 1, 2, uv, tt, __main__.psx, __main__.psy, leem_stv, leem_obj, leem_fov])
	pictureScan.runScan()
	uvpreview();

def uvpreview():
	uv.detector.setCameraInProgress(False)  # @UndefinedVariable
	try:
		uv.setToAuto()
	except AttributeError:
		pass
	uv.setPixelClock(10)
	uv.setCollectionTime(0.1)
	uv.setImageAverage(1)
	uv.detector.setCameraInProgress(True)  # @UndefinedVariable
	uv.detector.setCameraADC(2)  # @UndefinedVariable

def uvimaging():
	uv.detector.setCameraInProgress(False)  # @UndefinedVariable
	try:
		uv.setToSoft()
	except AttributeError:
		pass
	uv.setPixelClock(10)
	uv.setImageAverage(0)
	uv.detector.setCameraSequentialMode(True)  # @UndefinedVariable
	uv.detector.setCameraADC(1)  # @UndefinedVariable

alias("multishots")
alias("acquireimages")
alias("acquireimagesdetector")

alias("uvpreview")
alias("uvimaging")
alias("picture")

print "="*80
print "= usePEEM completed successfully"
print "="*80