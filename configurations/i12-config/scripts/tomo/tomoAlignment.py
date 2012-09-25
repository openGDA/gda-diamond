"""
Performs software triggered tomography
"""

from bisect import bisect_left, bisect_right
from gda.commandqueue import JythonCommandCommandProvider
from gda.factory import Finder
from gdascripts.messages import handle_messages
from time import sleep
from tomographyScan import tomoScan
import math
import sys
from fast_scan import FastScan
from gda.jython.ScriptBase import checkForPauses
from i12utilities import setSubdirectory

verbose = False
f = Finder.getInstance()

"""
Performs software triggered tomography
"""
def tomoScani12(description, sampleAcquisitionTime, flatAcquisitionTime, numberOfFramesPerProjection, numberofProjections,
                 isContinuousScan, desiredResolution, timeDivider, positionOfBaseAtFlat, positionOfBaseInBeam):
    
    steps = {1:0.03, 2:0.06, 4:0.06, 8:0.1}
    xBin = {1:1, 2:1, 4:2, 8:2}
    yBin = {1:1, 2:1, 4:2, 8:4}
    exposureVsRes = {1:1, 2:1, 4:4, 8:8}
    updateScriptController("Tomo scan starting")
    timeDividedAcq = sampleAcquisitionTime * timeDivider
    timeDividedAcq = timeDividedAcq/exposureVsRes[desiredResolution]
    pco = f.find("pco")
    pco.stop();
    #
    pco.setExternalTriggered(True)
    #
    
    
    ad = pco.getController().getAreaDetector()
    ad.setBinX(xBin[desiredResolution])
    ad.setBinY(yBin[desiredResolution])
    if verbose:
        print "Tomo scan starting"
        print "type : " + `steps[desiredResolution]`
        print "Description: " + `description`
        print "Sample acquisition time: " + `sampleAcquisitionTime`
        print "flatAcquisitionTime: " + `flatAcquisitionTime`
        print "numberOfFramesPerProjection: " + `numberOfFramesPerProjection`
        print "numberofProjections: " + `numberofProjections`
        print "isContinuousScan: " + `isContinuousScan`
        print "timeDivider: " + `timeDivider`
        print "positionOfBaseAtFlat:" + `positionOfBaseAtFlat`
        print "positionOfBaseInBeam: " + `positionOfBaseInBeam`
        print "desiredResolution: " + `int(desiredResolution)`
        print 'Sample Acq#' + `sampleAcquisitionTime`
        print 'Sample Acq Time divided#' + `timeDividedAcq`
    fastScan = FastScan('fastScan')
    tomoScan(positionOfBaseInBeam, positionOfBaseAtFlat, timeDividedAcq, 0, 180, steps[desiredResolution], 0, 0, 1, 1, 0, additionalScannables=[fastScan])
    


def changeSubDir(subdir):
    setSubdirectory(subdir)
    updateScriptController("Subdirectory set to " + subdir)
    
def getSubdir():
    subdir = f.find("GDAMetadata").getMetadataValue("subdirectory")
    updateScriptController("Subdirectory:" + subdir)
    
def updateScriptController(msg):
    scriptController = f.find("tomoAlignmentConfigurationScriptController")
    if scriptController != None:
        scriptController.update(scriptController, msg)

def moveTomoAlignmentMotors(motorMoveMap):
    updateScriptController("Moving tomo alignment motors")
    for motor, position in motorMoveMap.iteritems():
        checkForPauses()
        f.find(motor).asynchronousMoveTo(position)
        
    for motor, position in motorMoveMap.iteritems():
        m = f.find(motor)
        while m.isBusy():
            updateScriptController("Aligning Tomo motors:" + m.name + ": " + `round(m.position, 2)`)
            sleep(5)
    print f.find("ss1_tx").isBusy()
    
        
def getModule():
    cam1_x = f.find("cam1_x")
    cameraModuleLookup = f.find("moduleMotorPositionLUT")
    mod1Lookup = round(cameraModuleLookup.lookupValue(1, "cam1_x"), 2)
    cam1_xPosition = round(cam1_x.position, 2)
    if cam1_xPosition == mod1Lookup:
        return 1
    
    mod2Lookup = round(cameraModuleLookup.lookupValue(2, "cam1_x"), 2)
    if cam1_xPosition == mod2Lookup:
        return 2
    
    mod3Lookup = round(cameraModuleLookup.lookupValue(3, "cam1_x"), 2)
    if cam1_xPosition == mod3Lookup:
        return 3
    
    mod4Lookup = round(cameraModuleLookup.lookupValue(4, "cam1_x"), 2)
    if cam1_xPosition == mod4Lookup:
        return 4
    return 0
    
def find_lt(a, x):
    'Find rightmost value less than x'
    i = bisect_left(a, x)
    if i:
        return a[i - 1]
    raise ValueError

def find_gt(a, x):
    'Find leftmost value greater than x'
    i = bisect_right(a, x)
    if i != len(a):
        return a[i]
    raise ValueError

def getT3xLookupValue(moduleNum, t3m1ZValue):
    motionLut = f.find("cameraMotionLUT")
    if moduleNum == 1:
        return motionLut.lookupValue(t3m1ZValue, "m1_t3_x")
    elif moduleNum == 2:
        return motionLut.lookupValue(t3m1ZValue, "m2_t3_x")
    elif moduleNum == 3:
        return motionLut.lookupValue(t3m1ZValue, "m3_t3_x")
    elif moduleNum == 4:
        return motionLut.lookupValue(t3m1ZValue, "m4_t3_x")


def lookupT3x(moduleNum, t3m1ZValue):
    lookupKeys = Finder.getInstance().find("cameraMotionLUT").getLookupKeys()
    if lookupKeys.__contains__(t3m1ZValue):
        return getT3xLookupValue(moduleNum, t3m1ZValue)
    try:
        z0 = find_lt(lookupKeys, t3m1ZValue)
        x0 = getT3xLookupValue(moduleNum, z0)
        z1 = find_gt(lookupKeys, t3m1ZValue)
        x1 = getT3xLookupValue(moduleNum, z1)
        x = x0 + ((x1 - x0) * (t3m1ZValue - z0) / (z1 - z0))
        return x
    except:
        exceptionType, exception, traceback = sys.exc_info()
        handle_messages.log(None, "Problem moving camera stage", exceptionType, exception, traceback, False)
        print "error in lookup t3x", exception

def getT3x(moduleNum):
    t3_m1z = f.find("t3_m1z")
    t3_x = f.find("t3_x")
    t3_m1z_to_lookup = t3_m1z.getPosition() - t3_m1z.getUserOffset()
    lookupT3xVal = lookupT3x(moduleNum, t3_m1z_to_lookup)
    return lookupT3xVal - t3_x.userOffset

def getT3M1yLookupValue(moduleNum, t3m1ZValue):
    motionLut = Finder.getInstance().find("cameraMotionLUT")
    if moduleNum == 1:
        return motionLut.lookupValue(t3m1ZValue, "m1_t3_m1y")
    elif moduleNum == 2:
        return motionLut.lookupValue(t3m1ZValue, "m2_t3_m1y")
    elif moduleNum == 3:
        return motionLut.lookupValue(t3m1ZValue, "m3_t3_m1y")
    elif moduleNum == 4:
        return motionLut.lookupValue(t3m1ZValue, "m4_t3_m1y")

def lookupT3M1y(moduleNum, t3m1ZValue):
    lookupKeys = Finder.getInstance().find("cameraMotionLUT").getLookupKeys()
    if lookupKeys.__contains__(t3m1ZValue):
        return getT3M1yLookupValue(moduleNum, t3m1ZValue)
    try:
        z0 = find_lt(lookupKeys, t3m1ZValue)
        y0 = getT3M1yLookupValue(moduleNum, z0)
        z1 = find_gt(lookupKeys, t3m1ZValue)
        y1 = getT3M1yLookupValue(moduleNum, z1)
        y = y0 + ((y1 - y0) * (t3m1ZValue - z0) / (z1 - z0))
        return y
    except:
        exceptionType, exception, traceback = sys.exc_info()
        handle_messages.log(None, "Problem moving camera stage", exceptionType, exception, traceback, False)
        if verbose:
            print "error in lookup t3x", exception

def getT3M1y(moduleNum):
    t3_m1z = f.find("t3_m1z")
    t3_m1y = f.find("t3_m1y")
    t3_m1z_to_lookup = t3_m1z.getPosition() - t3_m1z.getUserOffset()
    lookupT3m1yVal = lookupT3M1y(moduleNum, t3_m1z_to_lookup)
    return lookupT3m1yVal - t3_m1y.userOffset

'''
move t3_m1z to the desired position, subsequently move t3_x and t3_m1y to positions relevant
'''
def moveT3M1ZTo(moduleNum, t3M1zPosition):
    try:
        t3_m1z = f.find("t3_m1z")
        t3_m1y = f.find("t3_m1y")
        t3_x = f.find("t3_x")
        #moving z
        if verbose:
            print "Moving t3_m1z to :" + `t3M1zPosition`
        t3_m1z.asynchronousMoveTo(t3M1zPosition)
        #moving y
        t3m1ZToLookup = t3M1zPosition - t3_m1z.userOffset
        lookupT3M1YVal = lookupT3M1y(moduleNum, t3m1ZToLookup)
        t3m1yOffset = t3_m1y.userOffset
        t3_m1y.asynchronousMoveTo(lookupT3M1YVal + t3m1yOffset)
        if verbose:
            print "Moving t3_m1y to :" + `lookupT3M1YVal + t3m1yOffset`
        
        #moving x
        lookupT3xVal = lookupT3x(moduleNum, t3m1ZToLookup)
        t3xOffset = t3_x.userOffset
        t3_x.asynchronousMoveTo(lookupT3xVal + t3xOffset)
        if verbose:
            print "Moving t3_x to :" + `lookupT3xVal + t3xOffset`
        #wait for motors to complete
        while t3_m1z.isBusy():
            updateScriptController("Waiting for t3_m1z")
            if verbose:
                print "Waiting for t3_m1z"
            sleep(5)
        while t3_m1y.isBusy():
            updateScriptController("Waiting for t3_m1y")
            if verbose:
                print "Waiting for t3_m1y"
            sleep(5)
        while t3_x.isBusy():
            updateScriptController("Waiting for t3_x")
            if verbose:
                print "Waiting for t3_x"
            sleep(5)
    except:
        exceptionType, exception, traceback = sys.exc_info()
        updateScriptController(exception)
        handle_messages.log(None, "Problem moving camera stage", exceptionType, exception, traceback, False)

'''
Move camera module to the specified module number
'''
def moveToModule(moduleNum):
    if getModule() == moduleNum:
        handle_messages.simpleLog("Already in the requested module")
        return
    handle_messages.simpleLog("Move To module:" + `moduleNum`)
    try:
        t3_x = f.find("t3_x")
        t3_m1y = f.find("t3_m1y")
        ss1_rx = f.find("ss1_rx")
        ss1_rz = f.find("ss1_rz")
        cam1_z = f.find("cam1_z")
        cam1_x = f.find("cam1_x")
        sampleTiltX = 0.0615;
        sampleTiltZ = 0.0
        cameraSafeZ = -10.0
        updateScriptController("Module align:moving ss1_rx to" + `round(sampleTiltX, 2)`)
        checkForPauses()
        ss1_rx.asynchronousMoveTo(sampleTiltX)
        while ss1_rz.isBusy():
            updateScriptController("Module align:waiting for ss1_rz to" + `round(ss1_rz.position, 2)`)
            sleep(5)
        
        updateScriptController("Module align:moving ss1_rz to" + `round(sampleTiltZ, 2)`)
        checkForPauses()
        ss1_rz.asynchronousMoveTo(sampleTiltZ)
        
        cameraModuleLookup = f.find("moduleMotorPositionLUT")
        
        cam1xLookup = cameraModuleLookup.lookupValue(moduleNum, "cam1_x")
        cam1zLookup = cameraModuleLookup.lookupValue(moduleNum, "cam1_z")
        ss1RzLookup = cameraModuleLookup.lookupValue(moduleNum, "ss1_rz")
        t3xLookup = getT3x(moduleNum)
        t3m1yLookup = getT3M1y(moduleNum)
        offset = math.fabs(cam1_x.getPosition() - cam1xLookup)
        handle_messages.simpleLog("offset:" + `offset`)
        if offset > 0.1:
            displayVal = round(cameraSafeZ, 3)
            updateScriptController("Module align:moving cam1_z to " + `displayVal`)
            checkForPauses()
            cam1_z.moveTo(cameraSafeZ)
            displayVal = round(cam1xLookup , 3)
            updateScriptController("Module align:moving cam1_x to " + `displayVal`)
            checkForPauses()
            cam1_x.moveTo(cam1xLookup)
            displayVal = round(cam1zLookup, 3)
            updateScriptController("Module align:moving cam1_z to " + `displayVal`)
            checkForPauses()
            cam1_z.moveTo(cam1zLookup)
            
        while ss1_rz.isBusy():
            displayVal = round(ss1_rz.position)
            updateScriptController("Module align:waiting for ss1_rz:" + `displayVal`)
            sleep(5)
            
        checkForPauses()
        ss1_rz.asynchronousMoveTo(ss1RzLookup)
        
        checkForPauses()
        t3_x.asynchronousMoveTo(t3xLookup)
        checkForPauses()
        t3_m1y.asynchronousMoveTo(t3m1yLookup)
        
        while ss1_rx.isBusy():
            displayVal = round(ss1_rx.position, 3)
            updateScriptController("Module align:waiting for ss1_rx:" + `displayVal`)
            sleep(5)
        
        while t3_x.isBusy(): 
            displayVal = round(t3_x.getPosition(), 3)
            updateScriptController("Module align:waiting for t3_x " + `displayVal`)
        
        while t3_m1y.isBusy():
            displayVal = round(t3_m1y.getPosition(), 3)
            updateScriptController("Module align:waiting for t3_m1y " + `displayVal`)
            
        while ss1_rz.isBusy():
            displayVal = round(ss1_rz.position)
            updateScriptController("Module align:waiting for ss1_rz:" + `displayVal`)
            sleep(5)
            
        updateScriptController("Module align:complete")
        handle_messages.simpleLog("complete module alignment:")
    except:
        exceptionType, exception, traceback = sys.exc_info()
        updateScriptController(exception)
        handle_messages.log(None, "Cannot change module", exceptionType, exception, traceback, False)
        
class TomoAlignmentConfigurationManager:
    def __init__(self):
        self.tomoAlignmentConfigurations = {}
        self.currentConfigInProgress = None
        pass
    
    def getRunningConfig(self):
        updateScriptController('RunningConfig#' + `self.currentConfigInProgress`)
        return self.currentConfigInProgress
        
    def setupTomoScan(self, length, configIds, descriptions, moduleNums, motorMoveMaps, sampleAcquisitionTimes, flatAcquisitionTimes, numberOfFramesPerProjections, numberofProjectionss,
                 isContinuousScans, desiredResolutions, timeDividers, positionOfBaseAtFlats, positionOfBaseInBeam, tomoAxisRotation):
        if self.currentConfigInProgress != None:
            updateScriptController('Tomography Scan already in progress...')
            if verbose:
                print "Tomography Scan already in progress..."
            return
        self.tomoAlignmentConfigurations.clear()
        for i in range(length):
            t = TomoAlignmentConfiguration(self, configIds[i], descriptions[i], moduleNums[i], motorMoveMaps[i], sampleAcquisitionTimes[i], flatAcquisitionTimes[i], numberOfFramesPerProjections[i], numberofProjectionss[i],
                 isContinuousScans[i], desiredResolutions[i], timeDividers[i], positionOfBaseAtFlats[i], positionOfBaseInBeam[i], tomoAxisRotation[i])
            self.tomoAlignmentConfigurations[i] = t
        self.runConfigs()
    
    def setConfigRunning(self, configId):
        if configId == None:
            self.currentConfigInProgress = None
        else:
            statusList = {}
            for k, v in self.tomoAlignmentConfigurations.iteritems():
                statusList[v.configId] = v.status
            self.currentConfigInProgress = statusList
        updateScriptController('RunningConfig#' + `self.currentConfigInProgress`)
        
    def runConfigs(self):
        commandQ = Finder.getInstance().find("commandQueueProcessor")
        for i in range(len(self.tomoAlignmentConfigurations)):
            config = self.tomoAlignmentConfigurations[i]
            cmdToQueue = 'tomoAlignment.tomographyConfigurationManager.tomoAlignmentConfigurations[' + `i` + '].doTomographyAlignmentAndScan()'
            commandQ.addToTail(JythonCommandCommandProvider(cmdToQueue, `i + 1` + ". Tomography Alignment and Scan : " + config.description, None))
    
    def stopScan(self):
        statusList = {}
        for k, v in self.tomoAlignmentConfigurations.iteritems():
            if v.status == None or v.status == "Running":
                v.status = "Fail"
            statusList[v.configId] = v.status
        self.currentConfigInProgress = None
        updateScriptController('RunningConfig#' + `statusList`)
        
tomographyConfigurationManager = TomoAlignmentConfigurationManager()
    
class TomoAlignmentConfiguration:
    def __init__(self, tomographyConfigurationManager, configId, description, moduleNum, motorMoveMap, sampleAcquisitionTime, flatAcquisitionTime, numberOfFramesPerProjection, numberofProjections,
                 isContinuousScan, desiredResolution, timeDivider, positionOfBaseAtFlat, positionOfBaseInBeam, tomoAxisRot):
        self.tomographyConfigurationManager = tomographyConfigurationManager
        self.configId = configId
        self.description = description
        self.moduleNum = moduleNum
        self.motorMoveMap = motorMoveMap
        self.sampleAcquisitionTime = sampleAcquisitionTime
        self.flatAcquisitionTime = flatAcquisitionTime
        self.numberOfFramesPerProjection = numberOfFramesPerProjection
        self.numberofProjections = numberofProjections
        self.isContinuousScan = isContinuousScan
        self.desiredResolution = desiredResolution
        self.timeDivider = timeDivider
        self.positionOfBaseAtFlat = positionOfBaseAtFlat
        self.positionOfBaseInBeam = positionOfBaseInBeam
        self.configId = configId
        self.tomoAxisRotation = tomoAxisRot
        self.status = None
        pass
    
    def doTomographyAlignmentAndScan(self):
        scriptController = Finder.getInstance().find("tomoAlignmentConfigurationScriptController")
        try:
            self.status = "Running"
            self.tomographyConfigurationManager.setConfigRunning(self.configId)
            if verbose:
                print 'Aligning module'
            checkForPauses()
            moveToModule(self.moduleNum)
            if verbose:
                print 'Aligning alignment motors'
            checkForPauses()
            moveTomoAlignmentMotors(self.motorMoveMap)
            if verbose:
                print 'Tomography scan'
            checkForPauses()
            tomoScani12(self.description,
                        self.sampleAcquisitionTime,
                        self.flatAcquisitionTime,
                        self.numberOfFramesPerProjection,
                        self.numberofProjections,
                        self.isContinuousScan,
                        self.desiredResolution,
                        self.timeDivider,
                        self.positionOfBaseAtFlat,
                        self.positionOfBaseInBeam)
            self.status = "Complete"
        except:
            exceptionType, exception, traceback = sys.exc_info()
            if scriptController != None:
                updateScriptController(exception)
            self.status = "Fail"
        finally:
            self.tomographyConfigurationManager.setConfigRunning(self.configId)
            self.tomographyConfigurationManager.setConfigRunning(None)
            updateScriptController('Tomography Scan Complete')
