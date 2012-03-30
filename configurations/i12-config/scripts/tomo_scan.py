#@PydevCodeAnalysisIgnore
from time import sleep
from gdascripts.utils import caput

print "Generating simple scan"

def basicTomoScan(camera=pco,
                  theta=ss1.theta,
                  flatFieldTranslation=ss1.x,
                  flatFieldTranslationDistance=100.0,
                  fastScanScannable=fastscan,
                  shutterPV="BL12I-PS-SHTR-02:CON",
                  cameraROIStartX=1,
                  cameraROIStartY=1,
                  cameraROISizeX=4008,
                  cameraROISizeY=2672,
                  cameraBinX=1,
                  cameraBinY=1,
                  cameraExposureTime=0.5,
                  scanStartAngle=0.0,
                  scanEndAngle=180.0,
                  scanNumberOfProjections=1800,
                  darkNumberOfImages=10,
                  flatNumberOfImages=10):
    print "running simple tomo scan"
    print "inputed parameters are"
    print "camera is %s" % camera
    print "theta stage is %s" % theta
    print "translation stage is %s" % flatFieldTranslation
    print "translation distance is %g" % flatFieldTranslationDistance
    print "cameraROIStart = (%d,%d)" %(cameraROIStartX, cameraROIStartY) 
    print "cameraROISize = (%d,%d)" %(cameraROISizeX, cameraROISizeY)
    print "cameraBin = (%d,%d)" %(cameraBinX, cameraBinY) 
    print "cameraExposureTime = %g" %(cameraExposureTime)
    print "scanRange = (%g,%g)" %(scanStartAngle, scanEndAngle)
    print "scanImages = %d" % scanNumberOfProjections
    print "darkNumberOfImages = %d" %(darkNumberOfImages)
    print "flatNumberOfImages = %d" %(flatNumberOfImages)

    # set up camera parameters
    # also set some of the other things up here, such as the camera roi etc.
    print "Setting camera parameters"
    camera.getAreaDetector().setBinning(cameraBinX,
                                        cameraBinY)
        
    camera.getAreaDetector().setROI(cameraROIStartX,
                                    cameraROIStartY,
                                    cameraROISizeX,
                                    cameraROISizeY)
    # dark scan 
    print("****** Collecting Dark Images ******") 
    print("******** Closing the shutter") 
    caput(shutterPV, 1) # close the shutter
    sleep(5)
    if (camera is pco) :  
        pco.getDataSaver().setFileName("d")
    scan dum.d 0 (0.01*darkNumberOfImages) 0.01 camera cameraExposureTime
     
    print("******** Opening the shutter") 
    caput(shutterPV, 0) # Open the shutter
    sleep(5)
    
    # flat scan
    print("****** Collecting First set of Flat Images ******") 
    sleep(2)
    if (camera is pco) :  
        pco.getDataSaver().setFileName("f")
    flatFieldPosition = flatFieldTranslation() # translate the sample
    inc flatFieldTranslation flatFieldTranslationDistance
    
    scan dum.d 0 (0.01*flatNumberOfImages) 0.01 camera cameraExposureTime
    
    pos flatFieldTranslation flatFieldPosition # translate the sample back
    
    # data scan
    print("****** Collecting Tomography data ******") 
    sleep(2)
    if (camera is pco) :  
        pco.getDataSaver().setFileName("p")
    stepSize = (scanEndAngle - scanStartAngle) / scanNumberOfProjections # calculate size of steps
    
    scan theta scanStartAngle scanEndAngle stepSize camera cameraExposureTime fastScanScannable
    
    # flat scan
    print("****** Collecting second set of Flat Images ******") 
    sleep(2)
    if (camera is pco) :  
        pco.getDataSaver().setFileName("f")
    flatFieldPosition = flatFieldTranslation() # translate the sample
    inc flatFieldTranslation flatFieldTranslationDistance
    
    scan dum.d 0 (0.01*flatNumberOfImages) 0.01 camera cameraExposureTime
    
    pos flatFieldTranslation flatFieldPosition # translate the sample back
    
    print "******* Tomography Complete *******"
    nextFileNumber = int(nfn())
    print "Darkfields collected to scan         %d" % (nextFileNumber-4)
    print "Pre Flatfields collected to scan     %d" % (nextFileNumber-3)
    print "Data collected to scan               %d" % (nextFileNumber-2)
    print "Post Flatfields collected to scan    %d" % (nextFileNumber-1)
    

    

    
    
    
