from time import sleep
from gdascripts.utils import caput
from tomo.pcoDetectorWrapper import PCODetectorWrapper
from gda.jython.commands.ScannableCommands import inc, scan, pos
#from gda.device.detector.pco import PCODetector
#pco1 = globals()["pco"]

print "Generating simple scan"

try:
    print "Deleting hdfpco wrapper"
    del hdfpco #@UndefinedVariable
    print "Deleting hdfpco wrapper complete"

except:
    print "Cannot delete hdfpco wrapper, it does not exist yet"
finally:
    sleep(2)
    hdfpco=PCODetectorWrapper("hdfpco", pco) #@UndefinedVariable

def tomographyScan(numberOfProjections=1800,exposureTime=0.5,flatFieldTranslationDistance=-100.0, #@UndefinedVariable
                   camera=hdfpco, numImagesPerPoint=1,
                   flatFieldTranslation=ss1.x, #@UndefinedVariable
                   numberOfFlatImages=10, 
                   fastScanScannable=fastscan, shutterPV="BL12I-PS-SHTR-02:CON", #@UndefinedVariable
                   startAngle=0.0, endAngle=180.0,numberOfDarkImages=10,motor=ss1.theta): #@UndefinedVariable
    print "running tomography scan"
    print "inputed parameters are:"
    print "rotation stage to scan is %s" % motor
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
    caput(shutterPV, 1) # close the shutter
    sleep(5)
    if (camera is hdfpco) :
        camera.collectDarkSet(numberOfDarkImages)
    print("******** Opening the shutter") 
    caput(shutterPV, 0) # Open the shutter
    darkfilename=camera.getFullFilename()
    print "Dark field collected     :  %s" % darkfilename
    sleep(5)
    
    # flat field collection
    print("****** Collecting First set of Flat Images ******") 
    sleep(2)
    flatFieldPosition = flatFieldTranslation() # translate the sample
    inc([flatFieldTranslation, flatFieldTranslationDistance])
    if (camera is hdfpco) :  
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
    scan([motor,startAngle,endAngle,stepSize,camera,exposureTime,fastScanScannable])
    tomoimages=camera.getFullFilename()
    print "Tomo Images collected    :  %s" % tomoimages
    # flat field collection
    print("****** Collecting second set of Flat Images ******") 
    sleep(2)
    flatFieldPosition = flatFieldTranslation() # translate the sample
    inc([flatFieldTranslation, flatFieldTranslationDistance])
    if (camera is hdfpco) :  
        camera.collectFlatSet(numberOfFlatImages, 2)
    pos([flatFieldTranslation, flatFieldPosition]) # translate the sample back
    flatfilename2=camera.getFullFilename()
    print "Post Flat field collected:  %s" % flatfilename2
    print "******* Tomography Complete *******"
    
