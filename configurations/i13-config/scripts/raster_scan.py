from gda.device.scannable import PseudoDevice

from gda.jython.commands.ScannableCommands import inc, scan, pos, createConcurrentScan
from gda.scan import ScanPositionProvider

from math import tan, radians

class RasterScannable(PseudoDevice):
    def __init__(self, motorX, motorY, detector):
        self.name = "RasterScannable"
        self.setInputNames(['points'])
        self.setExtraNames([])
        self.setOutputFormat(['%.4f'])
        self.busyFlag=False
        self.motorX=motorX
        self.motorY=motorY
        self.detector=detector

    def isBusy(self):
        return self.busyFlag

    def getPosition(self):
        return( 1.0 )

    def asynchronousMoveTo(self,rasterscan_position):
        self.busyFlag=True
        for x,y in rasterscan_position.position:
            print "Moving to %f %f " % (x,y)
            self.motorX.moveTo(x)
            self.motorY.moveTo(y)
        self.busyFlag=False
    

class rasterscan_position:
    def __init__(self, position):
        self.position=position

class   rasterscan_positions(ScanPositionProvider):
    def __init__(self, centerX, centerY, widthX, heightY, angleInDegrees, verticalPitch):

	pts=[]
	w_offset=[]
	w_offset.append(-widthX*0.5)
	w_offset.append(widthX*0.5)
	
	h=heightY*0.5
	tg=tan(radians(angleInDegrees))
	ctg=1.0/tg
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

        #self.points=rasterscan_position([(0,0),(1,1),(2,2)])
	self.points=rasterscan_position(pts)

    def get(self, index):
        return self.points
    
    def size(self):
        return 1
    
    def __str__(self):
        return "rasterscan_positions"
    
    def toString(self):
        return self.__str__()

def raster_scan( motorX, motorY, detector, centerX=10, centerY=20, widthX=30, heightY=50, angleInDegrees=5, verticalPitch=.2, speedX=3):
    points=rasterscan_positions(centerX=10, centerY=20, widthX=30, heightY=50, angleInDegrees=5, verticalPitch=.2)
    scanObject=createConcurrentScan([RasterScannable(motorX, motorY,detector), points])
    scanObject.runScan()
    return scanObject;
