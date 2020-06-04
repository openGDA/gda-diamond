from gda.device.scannable import ScannableMotionBase
from gda.device.detector import DetectorBase
from gda.device.scannable import SimpleScannable

from gda.jython.commands.ScannableCommands import inc, scan, pos, createConcurrentScan
from gda.scan import ScanPositionProvider
from java.lang import Thread, Runnable
from math import tan, radians
import time


class RasterScannable(ScannableMotionBase, Runnable):
    def __init__(self, motorX, motorY, exposureTime):
        self.name = "RasterScannable"
        self.setInputNames(['points'])
        self.setExtraNames([])
        self.setOutputFormat(['%.4f'])
        self.busyFlag=False
        self.motorX=motorX
        self.motorY=motorY
        self.exposureTime = exposureTime		

    def isBusy(self):
        return self.busyFlag

    def getPosition(self):
        return( 1.0 )

    def asynchronousMoveTo(self,rasterscan_path):
        self.rasterscan_path=rasterscan_path
        self.stopFlag=False
        self.busyFlag=True
        t = Thread(self)
        t.start()

    def stop(self):
        self.motorX.stop()
        self.motorY.stop()
        self.stopFlag=True
        
    def run(self):
		#wait for detector to start exposing
		totalStartTime=time.clock()
		time.sleep(1.0)
		numPoints = len(self.rasterscan_path.points)
		for i in range(numPoints):
			posn = self.rasterscan_path.points[i]
			x,y = posn
			if self.stopFlag:
				break
			print "Point %d of %d. Moving to (%f, %f) " % (i+1, numPoints, x,y)
			startMove = time.clock()
			self.motorX.moveTo(x)
			self.motorY.moveTo(y)
#			print " time to move = " , time.clock()-startMove
		totalEndTime=time.clock()
		totalMoveTime=time.clock()-totalStartTime
		print "Total move time " , totalMoveTime
		if self.exposureTime < totalMoveTime:
			print "Warning detector exposure completed before end of move"
		else:
			print "Waiting for detector exposure to finish"
		
		self.busyFlag=False



class rasterscan_path:
	def __init__(self, centerX, centerY, widthX, heightY, angleInDegrees, verticalPitch):
		pts=[]
		w_offset=[]
		w_offset.append(-widthX*0.5)
		w_offset.append(widthX*0.5)
		
		h=heightY*0.5
		tg=tan(radians(angleInDegrees))
		ctg=1.0/tg
#		print "ctg = ", ctg
		l=0
		tpl=()
		while h>=(-heightY*0.5):
			px=w_offset[l] + h*ctg
			tpl=(px+centerX),(h+centerY)
			pts.append(tpl)
			qx=-w_offset[l] + h*ctg
			tpl=(qx+centerX),(h+centerY)
			pts.append(tpl)
			l+=1
			l%=2
			h-=verticalPitch
	
		self.points=pts
		
	def points(self):
		return self.points


def scan( motorX, motorY, det, widthX=1.0, heightY=1.0, spotSize=.1, exposureTimePerPoint=.1, centerX=None, centerY=None, angleInDegrees=90 ):
	"""
	Command take an image from a detector whilst moving 2 motors, x & y so that the position (x,y) traces out a path that
	covers a grid of points
	
	        ++++++++++++++++
	^      ++++++++++++++++
	|     ++++++++++++++++     heightY
	y    ++++++++++++++++
		      widthX
	x - >


	parameters:

	motorX = motor to move to x direction 
	motorY = motor to move to y direction
	det    = detector to expose
	widthX = width of the grid in x direction at any point in y
	heightY = height of the grid in y direction
	spotSize = step in the y direction 
	exposureTimePerPoint = effective time to move x through a distance equal to the spotSize in x

	centerX = value of x in the center of the grid. If not set then the current position of motorX is used
	centerY = value of y in the center of the grid. If not set then the current position of motorY is used
	angleInDegrees = angle from x axis of side of the grid. A square has angleInDegrees=90. Default=90

	e.g. raster_scan.scan( s4_xplus, s4_xminus, pco1_tif, widthX=1.0, heightY=1.0, spotSize=.1, exposureTimePerPoint=1.0)

	"""
	XAtStart = motorX() 
	YAtStart = motorY() 
	if centerX == None:
		centerX = XAtStart
	if centerY == None:
		centerY = YAtStart 
	path=rasterscan_path(centerX=centerX, centerY=centerY, widthX=widthX, heightY=heightY, angleInDegrees=angleInDegrees, verticalPitch=spotSize)
	oldLevel=det.level
	det.level=motorX.level
	oldSpeedX = motorX.getSpeed()
	try:
		ss=SimpleScannable()
		ss.setName("ss")
		ss.setInputNames(["ss"])
		ss.setCurrentPosition(0.0)
		ss.configure()

		for x,y in path.points:
			chkX = motorX.checkPositionWithinGdaLimits(x)
			if( chkX != None):
				raise chkX
			chkY = motorX.checkPositionWithinGdaLimits(y)
			if( chkY != None):
				raise chkY

		x,y = path.points[0]
		print "Moving to first position (%f, %f)" % (x,y)
		motorX.moveTo(x)
		motorY.moveTo(y)

		numberOfYSteps = heightY/spotSize + 1
		# for each Y step we have to move X and Y in 2 separate steps
		timePerYStep = .3 * 2  
		numberOfXSteps = numberOfYSteps*(widthX/spotSize + 1)
		speedX = spotSize/exposureTimePerPoint
		motorX.setSpeed(speedX)
		#.5 sfor each y step
		exposureTime = numberOfXSteps*exposureTimePerPoint+ numberOfYSteps*timePerYStep
#		print "numberOfXSteps = %d exposureTimePerPoint = %f, speedX = %f numberOfYSteps = %d" % ( 	numberOfXSteps, exposureTimePerPoint, speedX, numberOfYSteps)
		print "Expected time =",exposureTime
		scanObject=createConcurrentScan([ss,0,0,1,RasterScannable(motorX, motorY, exposureTime), path, det, exposureTime ])
		scanObject.runScan()
		return scanObject;
	finally:
		det.level=oldLevel
		motorX.setSpeed(oldSpeedX)
		motorX.moveTo(XAtStart)
		motorY.moveTo(YAtStart)
