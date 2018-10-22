import math;

from gda.analysis import RCPPlotter;

from uk.ac.diamond.scisoft.analysis.plotserver import GuiBean;
from uk.ac.diamond.scisoft.analysis.plotserver import GuiParameters;
from uk.ac.diamond.scisoft.analysis.plotserver import GuiPlotMode;

from org.eclipse.dawnsci.analysis.dataset.roi import RectangularROI, RectangularROIList;


from Diamond.Analysis.Analyser import AnalyserWithRectangularROIClass

#Introduce the script logger
from Diamond.Utility.ScriptLogger import ScriptLoggerClass;
logger=ScriptLoggerClass();

class P2M_INFO(object):
	PIXEL_SIZE = 1.72e-04;
	PIXEL_NUMBER_X=1474;
	PIXEL_NUMBER_Y=1679;
	WIDTH=PIXEL_NUMBER_X * PIXEL_SIZE;
	HEIGHT=PIXEL_NUMBER_Y * PIXEL_SIZE;

	def getPosition(self, indexX, indexY):
		'''Given pixel index, return the pixel position in meter'''
		x= indexX * P2M_INFO.PIXEL_SIZE;
		y= indexY * P2M_INFO.PIXEL_SIZE;
		return [x,y];

	def getIndex(self, x, y):
		'''Given the pixel position in meter, return the pixel index'''
		indexX= int( float(x) / P2M_INFO.PIXEL_SIZE );
		indexY= int( float(y) / P2M_INFO.PIXEL_SIZE );
		return [indexX,indexY];
	
	def getPixels(self, length):
		'''Given the real length in meter, return the pixel numbers'''
		return int( float(length) / P2M_INFO.PIXEL_SIZE );
	
	def getLength(self, number):
		'''Given the pixel numbers, return real length in meters'''
		return (number * P2M_INFO.PIXEL_SIZE);
		

class AnalyserWithMovingRectangularROIClass(AnalyserWithRectangularROIClass):
	
	def __init__(self, name, detector, processors=[], panelName="Area Detector", iFileLoader=None):

		AnalyserWithRectangularROIClass.__init__(self, name, detector, processors, panelName, iFileLoader);
#		super(DetectorAnalyserClass, self).__init__(name, detector, processors, panel_name, iFileLoader);
		self.extraNames = ['file'];
		self.outputFormat = ['%f','%s'];

		self.angleDevice=None;
		self.distance=100;
		self.xCentre, self.yCentre = 0, 0; #Beam centre in Pixel
		
		self.x, self.y, self.w, self.h = 0,0,0,0 #roi
		
		self.deviceInfo=P2M_INFO();

	def info(self):
		print "Angle Device: " + self.angleDevice.getName();
		print "Distnace between Sample and Detector" + str(self.distance);
		print "Beam centre: (" + str(self.xCentre), + ", "+ str(self.yCentre);
		
	
	def setAngleDevice(self, angleDevice):
		self.angleDevice=angleDevice;

	def setDistance(self, distance):
		self.distance=self.deviceInfo.getPixels(distance);

	def getDistance(self):
		return self.deviceInfo.getLength(self.distance);

	def setBeamCentre(self, x, y):
		self.xCentre, self.yCentre = x, y;
	
	def setRoi(self, x0, y0, width, height):
		self.x=x0-width/2.0;
		self.y=y0-height/2.0;
		self.w, self.h=width, height;

		self.clearRoi();
		self.addRoi(self.x, self.y, self.w, self.h, 0);
		self.dTheta=math.atan( (self.h/2.0)/self.distance );
		
	def getRoi(self):
		#Get the ROI info from GUI
		#To get the current GUI situation
		guibean=RCPPlotter.getGuiBean(self.panel);
		roiList=guibean[GuiParameters.ROIDATALIST];
		
#		for roi in roiList:
#			[x,y,w,h,angle]=self.getRoiParameters(roi);

		roi = roiList[0];
		[x,y,w,h,angle]=self.getRoiParameters(roi);
		return roi;
	
	def moveRoi(self):
		self.clearRoi();
		self.addRoi(self.x, self.y, self.w, self.h, 0);

	def findRoi(self, theta=None):
		if theta is None:
			theta=self.angleDevice.getPosition();
			
		cy0=self.distance * math.tan( math.radians(2.0*theta) + self.dTheta);
		cy1=self.distance * math.tan( math.radians(2.0*theta) - self.dTheta);
		
		self.y=self.yCentre-cy0;
		self.h=int( abs(cy1-cy0) + 0.5);
		return [self.x, self.y, self.w, self.h];


	def readout(self):
		self.findRoi();
		self.moveRoi();
		
		result = AnalyserWithRectangularROIClass.readout();
		
		return result;

##########################################
#run("Diamond/Analysis/DetectorAnalyserMovingROI")
exec("ppr, ppr1 = None, None")
from Diamond.Analysis.Processors import MinMaxSumMeanDeviationProcessor;

from gda.analysis.io import PilatusTiffLoader

ppr1 = AnalyserWithMovingRectangularROIClass("ppr1", dummyCamera, [MinMaxSumMeanDeviationProcessor()], panelName="Area Detector", iFileLoader=PilatusTiffLoader);
ppr1.setAlive(True); #To display the result
ppr1.setPassive(False);#To drive the pil1

ppr1.setAngleDevice(testMotor1); #To set the angle device that this ROI will follow

ppr1.setDistance(0.5); #To set the distance between sample and detector in meter
ppr1.setBeamCentre(200, 100); #To set the beam centre position on the image in pixel
ppr1.setRoi(200, 100, 40, 10); #To set the ROI using centre position and width, height. Note that x must be aligned with the x beam centre.

#scan testMotor1 0 0.8 0.05 ppr1 1
