#@PydevCodeAnalysisIgnore
from uk.ac.gda.client.tomo.basic.beans import BasicTomographyParameters

from flat_field import FlatField

from org.edna.tomov1 import Helpers
from org.edna.tomov1.xsdata import *
from org.edna.tomov1.launchers import *
from java.io import PrintStream
from java.io import FileOutputStream

from uk.ac.gda.client.tomo import *
from uk.ac.gda.client.tomo.basic import *

from gdascripts.utils import caput

from gda.factory import Finder

print "Generating basic tomography scan"

def basicTomoScan(camera="pco",
                  theta="dum.a",
                  flatFieldTranslation="dum.b",
                  cameraROIStartX=1,
                  cameraROIStartY=1,
                  cameraROISizeX=4008,
                  cameraROISizeY=2672,
                  cameraBinX=1,
                  cameraBinY=1,
                  cameraExposureTime=0.5,
                  scanStartAngle=0.0,
                  scanEndAngle=180.0,
                  scanNumberOfPointsPerSegment=60,
                  scanNumberOfSegments=3,
                  darkNumberOfImages=10,
                  flatNumberOfImages=10,
                  reconNumberOfChunks=8,
                  reconJobName="Auto"):
    print "running basic tomo scan"
    print "inputed parameters are"
    print "camera is %s" % camera
    print "theta stage is %s" % theta
    print "translation stage is %s" % flatFieldTranslation
    print "cameraROIStart = (%d,%d)" %(cameraROIStartX, cameraROIStartY) 
    print "cameraROISize = (%d,%d)" %(cameraROISizeX, cameraROISizeY)
    print "cameraBin = (%d,%d)" %(cameraBinX, cameraBinY) 
    print "cameraExposureTime = %g" %(cameraExposureTime)
    print "scanRange = (%g,%g)" %(scanStartAngle, scanEndAngle)
    print "scanSegments = (%d,%d)" %(scanNumberOfSegments, scanNumberOfPointsPerSegment)
    print "darkNumberOfImages = %d" %(darkNumberOfImages)
    print "flatNumberOfImages = %d" %(flatNumberOfImages)
    print "reconNumberOfChunks = %d" %(reconNumberOfChunks)
    print "reconJobName = %s" %(reconJobName)    
    
    # fill the bean
    bean = BasicTomographyParameters()
    bean.setCamera(camera)
    bean.setTheta(theta)
    bean.setFlatFieldTranslation(flatFieldTranslation)
    bean.setCameraROIStartX(cameraROIStartX)
    bean.setCameraROIStartY(cameraROIStartY)
    bean.setCameraROISizeX(cameraROISizeX)
    bean.setCameraROISizeY(cameraROISizeY)
    bean.setCameraBinX(cameraBinX)
    bean.setCameraBinY(cameraBinY)
    bean.setCameraExposureTime(cameraExposureTime)
    bean.setScanStartAngle(scanStartAngle)
    bean.setScanEndAngle(scanEndAngle)
    bean.setScanNumberOfPointsPerSegment(scanNumberOfPointsPerSegment)
    bean.setScanNumberOfSegments(scanNumberOfSegments)
    bean.setDarkNumberOfImages(darkNumberOfImages)
    bean.setFlatNumberOfImages(flatNumberOfImages)
    bean.setReconNumberOfChunks(reconNumberOfChunks)
    bean.setReconJobName(reconJobName)
    
    # call the main method for running the scan
    basicTomoScanFromBean(bean)    

    
def basicTomoScanFromBean(bean):
    print "running the basic tomo scan from a bean"
    print bean
    
    print "initialising vars from the bean"
    # then we need to run the scan, this should be quite easy from this point
    # generate some values
    scanStart = bean.getScanStartAngle()
    scanStop = bean.getScanEndAngle()
    scanSteps = bean.getScanNumberOfSegments()*bean.getScanNumberOfPointsPerSegment()
    scanStep = (scanStop-scanStart)/scanSteps
    expTime = bean.getCameraExposureTime()
    sectorSteps = bean.getScanNumberOfPointsPerSegment()
    flats = bean.getFlatNumberOfImages()
    darks = bean.getDarkNumberOfImages()
    camera = Finder.find(bean.getCamera())
    theta = getMotor(bean.getTheta())
    trans = getMotor(bean.getFlatFieldTranslation())
    chunkHeight = bean.getCameraROISizeY()/bean.getReconNumberOfChunks()
    
    # before doing much of this, we should set the motor to its start position
    # so as not to time out the reconstructions.
    print "moving motor to start position"    
    theta(scanStart)
    
    # change to fast accel, slow top speed for scan
    print("changing theta to fast scanning mode")
    caput("BL12I-MO-TAB-02:ST1:THETA.ACCL", 0.01)
    caput("BL12I-MO-TAB-02:ST1:THETA.VMAX", 10.0)
    
    # first we need to run the tomography script
    # this needs to be threaded so as not to block, and so will be done later
    
    print "set up the input variables for the reconstruction"
    input = XSDataInputTomography()
    input.setByteDepthOfImage(Helpers.createXSDataInteger(2))
    input.setChunkHeight(Helpers.createXSDataInteger(chunkHeight))
    input.setImageDirectory(Helpers.createXSDataFile(nwd()))
    input.setImageWidth(Helpers.createXSDataInteger(bean.getCameraROISizeX()))
    input.setJobName(Helpers.createXSDataString("gda"))
    input.setNumberOfChunks(Helpers.createXSDataInteger(bean.getReconNumberOfChunks()))
    input.setNumberOfProjectionsPerSegment(Helpers.createXSDataInteger(bean.getScanNumberOfPointsPerSegment()))
    input.setNumberOfSegments(Helpers.createXSDataInteger(bean.getScanNumberOfSegments()))
    input.setTimeoutLength(Helpers.createXSDataFloat(180.0))
    input.setTimeoutPollingInterval(Helpers.createXSDataFloat(5.0))
    # TODO this should be in a more central place
    input.setSettingsFileName(Helpers.createXSDataFile("/dls/i12/data/2010/ee0/processing/testFiles/settings.in"))
    input.setUniqueName(Helpers.createXSDataString(str(nfn())))
    
    print "creating the callable task"
    task = BasicTomoTask()
    task.setXSDataInputTomography(input)
    
    print "Adding the task"
    rm.addRecon(task);
    
    print "Task added"
    
    try :
        del ff        
    except :
        pass
    
    ff = FlatField("ff",camera,trans)  
    
    # also set some of the other things up here, such as the camera roi etc.
    print "Setting camera parameters"
    camera.getAreaDetector().setBinning(bean.getCameraBinX(),
                                        bean.getCameraBinY())
        
    camera.getAreaDetector().setROI(bean.getCameraROIStartX(),
                                    bean.getCameraROIStartY(),
                                    bean.getCameraROISizeX(),
                                    bean.getCameraROISizeY())
    
    print "Starting the Scan"
    print " scan %s %g %g %g %s %g %s [ %g, %g, %g ] " %(theta,scanStart,scanStop,scanStep,camera,expTime,ff,flats,sectorSteps,darks,)
    scan theta scanStart scanStop scanStep camera expTime ff [flats,sectorSteps,darks]

    # change to slow accel,  high top speed for scan
    print("changing theta to general mode")
    caput("BL12I-MO-TAB-02:ST1:THETA.ACCL", 1.0)
    caput("BL12I-MO-TAB-02:ST1:THETA.VMAX", 1000.0)


# helper function to get motor names from a string    
def getMotor(motorName):
    parts = motorName.split('.')
    return Finder.find(parts[0]).getGroupMember("%s_%s"%(parts[0],parts[1]))
    
    
    
    
    