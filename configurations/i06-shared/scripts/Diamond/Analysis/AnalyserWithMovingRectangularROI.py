'''AnalyserWithMovingRectangularROIClass
'''

import math;

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
	'''A class to create several ROI (Region Of Interests) that can track the beam on big area detector.'''
	
	def __init__(self, name, detector, processors=[], panelName="Area Detector", iFileLoader=None):
		AnalyserWithRectangularROIClass.__init__(self, name, detector, processors, panelName, iFileLoader);
#		super(DetectorAnalyserClass, self).__init__(name, detector, processors, panel_name, iFileLoader);
		self.extraNames = ['file'];
		self.outputFormat = ['%f','%s'];

		self.distance=100;#the distance from sample to detector surface plane in pixel
		self.xCentre, self.yCentre = [None]*2 #origin on the detector surface plane in pixel
		self.xBeamCentre, self.yBeamCentre =[None]*2 #the perpendicular beam spot position in pixel on the detector used as origin 
		
		self.x, self.y, self.w, self.h = [None]*4 #the beam tracking roi 
		self.gamma0=None;#the initial gamma anle with direct beam

		self.dTheta, self.dGamma = [None]*2; #the angles that defines the roi
		
		self.thetaDevice, self.gammaDevice = [None]*2;#the angle devices that defines the beam direction
		self.deviceInfo=P2M_INFO();
		
		self.follow=True;#other rois to follow the beam tracking roi

	def info(self):
		print "Angle Devices: Theta: %s, Gamma: %s" %(self.thetaDevice.getName(), self.gammaDevice.getName());
		print "Distnace from Sample to Detector surface: %f" %self.distance;
		print "Direct beam centre: (%d, %d)" %(self.xCentre, self.yCentre);
		print "Initial Gamma with direct beam: %f " %self.gamma0;
		
	def setFollow(self, follow=True):
		'''Set to enable/disable other rois to follow the beam tracking roi.'''
		self.follow=follow;
	
	def setAngleDevice(self, thetaDevice, gammaDevice):
		'''To set the angle devices in GDA that the beam should follow.'''
		self.thetaDevice=thetaDevice;
		self.gammaDevice=gammaDevice;

	def setDistance(self, distance):
		'''To set the distance in meter from the sample to detector surface plane.'''
#		virticalDistance=distance * math.cos( math.radians(self.gamma0) )
		virticalDistance=distance * 1.0
		self.distance=self.deviceInfo.getPixels(virticalDistance);


	def getDistance(self):
		'''To get the distance from the sample to detector surface plane'''
		virticalDistance=self.distance;
		beamDistance=virticalDistance/math.acos( math.radians(self.gamma0) )
		return self.deviceInfo.getLength(virticalDistance);
#		return self.deviceInfo.getLength(beamDistance);

	def setGammaZero(self, gamma0):
		'''To set the initial gamma angle with direct beam'''
		self.gamma0= abs(gamma0);
	
	def setBeamCentre(self, x0, y0):
		'''To set the initial direct beam spot (without sample reflection) position in pixel on the detector.'''
		self.xBeamCentre, self.yBeamCentre =x0, y0;

		self.yCentre = y0;
		self.xCentre = x0 - self.distance * math.tan( math.radians(self.gamma0) )

	def setBeamRoiSize(self, width=None, height=None):
		'''To set size of the beam tracking roi. 
		If no size parameters given, the first roi defined in the side plot will be used
		'''
		if None in [self.xBeamCentre, self.yBeamCentre]:
			print "Beam Centre not defined yet! Please set the Beam Centre first"
			return;
		
		if [width, height] == [None, None]:#Not given in the command, update the side plot roi:
			#To check the current rois defined in the box profile
			self.updateRoiList();
			if [len(self.roiList), width, height] == [0, None, None]:
				print "The ROI List is empty, please specify the size of the beam tracking roi"
				return;
			
			r = self.getRoiParameters( self.roiList[0] );#to get the beam tracking roi
			self.w, self.h = r[2:4];
		else:
			self.w, self.h = width, height;
		
		self.x, self.y = self.xBeamCentre-self.w/2.0, self.yBeamCentre-self.h/2.0

		self.modifyRoi(0, self.x, self.y, self.w, self.h, 0);
			
		self.dTheta = math.atan( (self.h/2.0)/self.distance ); 
#		self.dGamma = math.atan( (self.w/2.0)/self.distance );
		self.dGamma = self.getDeltaAngle(self.gamma0);
		
	def getDeltaAngle(self, angle0):
		ta =  math.tan( math.radians(angle0) )+ (self.w/2.0)/self.distance
		angle = math.atan( ta ) - math.radians(angle0) 
		return angle;
		
	def setBeamRoiByCentre(self, x0, y0, w0, h0):
		'''To set up a beam tracking roi using the beam centre position and roi size. 
		The beam spoo centre will be redefined to use this roi centre. 
		'''
		self.setBeamCentre(x0, y0);
		self.setBeamRoiSize(w0, h0);

	def moveRois(self, angleTheta=None, angleGamma=None):
		'''To calculate the beam tracking roi position and move all rois accordingly.'''
		oldRoiTable=self.getRoiTable();#to get the current roi information
		[x0, y0, w0, h0, a0] = oldRoiTable[0]; # old beamRoi
		
		[x1, y1, w1, h1] =self.findBeamRoi(angleTheta, angleGamma) #new beamRoi
		
		xOffset, yOffset=0.0, 0.0
		wRatio, hRatio=1.0, 1.0
		if self.follow:
			xOffset, yOffset = x1-x0, y1-y0;
			wRatio, hRatio = 1.0*w1/w0, 1.0*h1/h0;
		
		newRoiTable = [ [x1, y1, w1, h1, 0] ];
		
		#to calculate the new shadow roi and add them to the roiList one by one
		for roiInfo in oldRoiTable[1:]:
			[x0, y0, w0, h0, a0] = roiInfo;
			x1, y1, w1, h1, a1 = x0+xOffset, y0+yOffset, 1.0*w0*wRatio, 1.0*h0*hRatio, a0;
			newRoiTable.append([x1, y1, w1, h1, a1])
			
		self.clearRois() #To remove all old rois
		for roiInfo in newRoiTable:
			self.addRoi(roiInfo[0],roiInfo[1],roiInfo[2],roiInfo[3],roiInfo[4],);

	def findBeamRoi(self, angleTheta=None, angleGamma=None):
		'''To calculate the beam tracking roi position'''
		if angleTheta is None:
			angleTheta=self.thetaDevice.getPosition();

		if angleGamma is None:
			angleGamma= self.gammaDevice.getPosition() ;
			
		cy0=self.distance * math.tan(math.radians(angleTheta)+self.dTheta) / math.cos(math.radians(angleGamma) );
		cy1=self.distance * math.tan(math.radians(angleTheta)-self.dTheta) / math.cos(math.radians(angleGamma) );

		cx0=self.distance * math.tan( math.radians(angleGamma) + self.dGamma );
		cx1=self.distance * math.tan( math.radians(angleGamma) - self.dGamma );
#		print "cx0 is %f, cx1 is %f" %(cx0, cx1)
		
		self.y=self.yCentre-cy0;
		self.h=int( abs(cy1-cy0) + 0.5);
		
		self.x=self.xCentre-cx0;
		self.w=int( abs(cx1-cx0) + 0.5);

		return [self.x, self.y, self.w, self.h];


	def readout(self):
		self.moveRois();
	
		result = AnalyserWithRectangularROIClass.readout(self);
		return result;

##########################################
#Usage:
#from Diamond.Analysis.AnalyserWithMovingRectangularROI import AnalyserWithMovingRectangularROIClass
#from Diamond.Analysis.Processors import MinMaxSumMeanDeviationProcessor;
#from gda.analysis.io import PilatusTiffLoader

#try:
#	del mroi;
#except:
#	pass;

#mroi = AnalyserWithMovingRectangularROIClass("mroi", pil2, [MinMaxSumMeanDeviationProcessor()], panelName="Area Detector", iFileLoader=PilatusTiffLoader);
#mroi.setAlive(True); #To display the result

#mroi.setAngleDevice(dummyTheta, dummyGamma); #To set the angle device that this ROI will follow
#mroi.setGammaZero(-11.736);
#mroi.setDistance(1.800)

#mroi.setBeamCentre(1308, 1653)
#mroi.setBeamRoiSize(10, 20)

##mroi.setBeamRoiByCentre(1308, 1653, 10, 20)
##mroi.clearRois()

#scan qdcd_0.02 0.1 0.01 mroi 1

