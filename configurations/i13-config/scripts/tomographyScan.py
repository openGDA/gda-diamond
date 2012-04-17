"""
Performs software triggered tomography
"""

from time import sleep

from pcoDetectorWrapper import PCODetectorWrapper
from gda.jython.commands.ScannableCommands import inc, scan, pos, createConcurrentScan

import sys
import time
import shutil
import gda
from gdascripts.parameters import beamline_parameters
from gdascripts.messages import handle_messages
from gda.device.scannable import ScannableBase
from gda.device.detector import DetectorBase
#from gda.device.detector.pco import PCODetector
#pco1 = globals()["pco"]

#print "Generating simple scan"

#try:
#    print "Deleting hdfpco wrapper"
#    del hdfpco #@UndefinedVariable
#    print "Deleting hdfpco wrapper complete"

#except:
#    print "Cannot delete hdfpco wrapper, it does not exist yet"
#finally:
#    sleep(2)
#    hdfpco=PCODetectorWrapper("hdfpco", pco) #@UndefinedVariable

class DummyCamera(DetectorBase):
    def __init__(self,name):
        self.name = name
        self.exposureTime=0
        self.fileNumber=0
        self.numberOfDarkImages=0;
        self.fullFilename="test_filename"
        self.numberOfFlatImages = 0
        self.flatset = 0
        self.numImagesPerPoint=0
        self.numberOfImageToCapture=0
    def log(self, msg):
        handle_messages("DummyCamera:" + msg)
        
    def setCollectionTime(self,exposureTime):
        self.exposureTime=exposureTime

    def resetFileNumber(self):
        self.fileNumber=0
        
    def collectDarkSet(self, numberOfDarkImages):
        self.numberOfDarkImages = numberOfDarkImages

    def getFullFilename(self):
        return self.fullFilename

    def collectFlatSet(self,numberOfFlatImages, flatset):
        self.numberOfFlatImages = numberOfFlatImages
        self.flatset = flatset

    def setNumImagesPerPoint(self, numImagesPerPoint):
        self.numImagesPerPoint = numImagesPerPoint

    def setNumberOfImageToCapture(self, numberOfImageToCapture):
        self.numberOfImageToCapture = numberOfImageToCapture
        
class DummyScannable(ScannableBase):
    def __init__(self, name):
        self.name = name
        self.inputNames = [name]
        self.pos=0
    def isBusy(self):
        return False
    def rawAsynchronousMoveTo(self,new_position):
        self.pos = new_position
    def rawGetPosition(self):
        return self.pos         




def testOfTomographyScan():
    tomographyScan(numberOfProjections=10,
                   exposureTime=2.,
                   flatFieldTranslationDistance=-100.0, #@UndefinedVariable
                   camera=DummyCamera("dummyCamera"),  
                   numImagesPerPoint=2,
                   flatFieldTranslation=DummyScannable("flatFieldTranslation"),
                   numberOfFlatImages=10, 
                   fastScanScannable=DummyScannable("dummyFastScannable"),
                   shutterScannable=DummyScannable("dummyScannable"),
                   startAngle=0.0, 
                   endAngle=180.0,
                   numberOfDarkImages=10,
                   theta_motor=DummyScannable("dummyThetaMotor"))

def tomographyScan(numberOfProjections,
                   exposureTime,
                   flatFieldTranslationDistance, #@UndefinedVariable
                   camera,#=hdfpco, 
                   flatFieldTranslation,#=ss1.x, #@UndefinedVariable
                   numberOfFlatImages, 
                   shutterScannable, #@UndefinedVariable
                   fastScanScannable, #=fastscan, 
                   numberOfDarkImages,
                   theta_motor, #=ss1.theta,
                   numImagesPerPoint=1,
                   startAngle=0., 
                   endAngle=180.
                   ): #@UndefinedVariable
    print "running tomography scan"
    print "inputed parameters are:"
    print "rotation stage to scan is %s" % theta_motor
    print "scan Range = (%g,%g)" %(startAngle, endAngle)
    print "total number of projections = %d" % numberOfProjections
    print "camera is %s" % camera
    print "camera exposure time = %g" %(exposureTime)
    print "number of images per projection = %d" % numImagesPerPoint
    print "Sample translation stage is %s" % flatFieldTranslation
    print "Sample translation distance is %g" % flatFieldTranslationDistance
    print "Number of flat images to collect = %d" % numberOfFlatImages
    print "Number of dark images to collect = %d" %(numberOfDarkImages)
    
    camera.setCollectionTime(exposureTime)
    camera.resetFileNumber();
    # dark field collection 
    print("****** Collecting Dark Images ******") 
    print("******** Closing the shutter") 
    shutterScannable.moveTo(1) # close the shutter
    sleep(5)
    camera.collectDarkSet(numberOfDarkImages)
    print("******** Opening the shutter") 
    shutterScannable.moveTo(0) # Open the shutter
    darkfilename=camera.getFullFilename()
    print "Dark field collected     :  %s" % darkfilename
    sleep(5)
    
    # flat field collection
    print("****** Collecting First set of Flat Images ******") 
    sleep(2)
    flatFieldPosition = flatFieldTranslation() # translate the sample
    inc([flatFieldTranslation, flatFieldTranslationDistance])
    camera.collectFlatSet(numberOfFlatImages, 1)
    pos([flatFieldTranslation, flatFieldPosition]) # translate the sample back
    flatfilename1=camera.getFullFilename()
    print "Pre Flat field collected :  %s" % flatfilename1
    # tomography projection collection scan
    print("****** Collecting Tomography data ******") 
    sleep(2)
    stepSize = (endAngle - startAngle) / numberOfProjections # calculate size of steps
    camera.setNumImagesPerPoint(numImagesPerPoint)
    camera.setNumberOfImageToCapture(numberOfProjections*numImagesPerPoint)
    scan_args = [theta_motor,startAngle,endAngle,stepSize,camera,exposureTime]
    if fastScanScannable != None:
        scan_args.append(fastScanScannable)
    print scan_args
    scan(scan_args)
    tomoimages=camera.getFullFilename()
    print "Tomo Images collected    :  %s" % tomoimages
    # flat field collection
    print("****** Collecting second set of Flat Images ******") 
    sleep(2)
    flatFieldPosition = flatFieldTranslation() # translate the sample
    inc([flatFieldTranslation, flatFieldTranslationDistance])
    camera.collectFlatSet(numberOfFlatImages, 2)
    pos([flatFieldTranslation, flatFieldPosition]) # translate the sample back
    flatfilename2=camera.getFullFilename()
    print "Post Flat field collected:  %s" % flatfilename2
    print "******* Tomography Complete *******"
    


class EnumPositionerDelegateScannable(ScannableBase):
    def __init__(self, name, delegate):
        self.name = name
        self.inputNames = [name]
        self.delegate = delegate
    def isBusy(self):
        return self.delegate.isBusy()
    def rawAsynchronousMoveTo(self,new_position):
        if int(new_position) == 1:
            self.delegate.asynchronousMoveTo("Open")
        else:
            self.delegate.asynchronousMoveTo("Close")
    def rawGetPosition(self):
        pos = self.delegate.getPosition()
        if pos == "Open":
            return 1 
        return 0

    
from gda.device.scannable import ScannableBase, ScannableUtils
from gda.device.scannable.scannablegroup import ScannableGroup
def make_tomoScanDevice(tomography_theta, tomography_shutter, tomography_translation, 
                        tomography_imageIndex):
    tomoScanDevice = ScannableGroup()
    tomoScanDevice.addGroupMember(tomography_theta)
    tomoScanDevice.addGroupMember(EnumPositionerDelegateScannable("tomography_shutter", tomography_shutter))
    tomoScanDevice.addGroupMember(tomography_translation)
    tomoScanDevice.addGroupMember(tomography_imageIndex)
    tomoScanDevice.setName("tomoScanDevice")
    tomoScanDevice.configure()
    return tomoScanDevice

from gda.device.scannable import SimpleScannable

"""
perform a simple tomogrpahy scan
"""
def tomoScan(step, darkFieldInterval, flatFieldInterval,
             inBeamPosition, outOfBeamPosition, detector, exposureTime):
    try:
        start=0.
        stop=180.
        jns=beamline_parameters.JythonNameSpaceMapping()
        tomography_theta=jns.tomography_theta
        if tomography_theta is None:
            raise "tomography_theta is not defined in Jython namespace"
        tomography_shutter=jns.tomography_shutter
        if tomography_shutter is None:
            raise "tomography_shutter is not defined in Jython namespace"
        tomography_translation=jns.tomography_translation
        if tomography_translation is None:
            raise "tomography_translation is not defined in Jython namespace"
        
        
        index=SimpleScannable()
        index.setCurrentPosition(0.0)
        index.setInputNames(["imageNumber"])
        index.setName("imageNumber")
        index.configure()
        
        tomoScanDevice = make_tomoScanDevice(tomography_theta, tomography_shutter, 
                                             tomography_translation, index)
        #generate list of positions
        numberSteps = ScannableUtils.getNumberSteps(tomography_theta, start, stop, step)
        theta_points = []
        theta_points.append(start)
        previousPoint = start
        for i in range(numberSteps):
            nextPoint = ScannableUtils.calculateNextPoint(previousPoint, step);
            theta_points.append(nextPoint)
            previousPoint = nextPoint
        
        scan_points = []
        theta_pos = theta_points[0]
        index=0
        scan_points.append((theta_pos, 0, inBeamPosition, index )) #dark
        index = index + 1        
        scan_points.append((theta_pos, 1, outOfBeamPosition, index )) #flat
        index = index + 1        
        scan_points.append((theta_pos, 1, inBeamPosition, index )) #first
        index = index + 1        
        imageSinceDark=0
        imageSinceFlat=0
        for i in range(numberSteps):
            theta_pos = theta_points[i+1]
            scan_points.append((theta_pos, 1, inBeamPosition, index ))#main image
            index = index + 1        
            
            
            imageSinceFlat = imageSinceFlat + 1
            print `imageSinceFlat` + ":" + `flatFieldInterval`
            if imageSinceFlat == flatFieldInterval:
                scan_points.append((theta_pos, 1, outOfBeamPosition, index ))
                index = index + 1        
                imageSinceFlat=0
            
            imageSinceDark = imageSinceDark + 1
            if imageSinceDark == darkFieldInterval:
                scan_points.append((theta_pos, 0, inBeamPosition, index ))
                index = index + 1        
                imageSinceDark=0
                
        scan_points.append((theta_pos, 1, outOfBeamPosition, index )) #flat
        index = index + 1        
        scan_points.append((theta_pos, 0, inBeamPosition, index )) #dark
        index = index + 1        
                
 
        scan_args = [tomoScanDevice,tuple(scan_points), detector, exposureTime  ]
        print scan_args
        scanObject=createConcurrentScan(scan_args)
#        scanObject.runScan()
        return scanObject;
    except :
        exceptionType, exception, traceback = sys.exc_info()
        handle_messages.log(None, "Error in tomoScan", exceptionType, exception, traceback, False)

def test_tomoScan():
    jns=beamline_parameters.JythonNameSpaceMapping()    
    return tomoScan(step=5, darkFieldInterval=5, flatFieldInterval=5,
             inBeamPosition=0., outOfBeamPosition=10.,detector=jns.pco1_tif , exposureTime=1.)        