"""
Performs software triggered tomography
"""

from bisect import bisect_left, bisect_right
from gda.commandqueue import JythonCommandCommandProvider
from gda.factory import Finder
from gda.jython.commands.ScannableCommands import scan
from gdascripts.messages import handle_messages
from i12utilities import pwd
from subprocess import Popen, PIPE, STDOUT
from time import sleep
from tomographyScan import tomoScan
import math
import os
import sys
from fast_scan import FastScan
from gda.jython.ScriptBase import checkForPauses 

f = Finder.getInstance()

"""
Performs software triggered tomography
"""
def tomoScani12(description, sampleAcquisitionTime, flatAcquisitionTime, numberOfFramesPerProjection, numberofProjections,
                 isContinuousScan, desiredResolution, timeDivider, positionOfBaseAtFlat, positionOfBaseInBeam):
    
    updateScriptController("Tomo scan starting")
    print "Description: " + `description`
    print "Sample acquisition time: " + `sampleAcquisitionTime`
    print "flatAcquisitionTime: " + `flatAcquisitionTime`
    print "numberOfFramesPerProjection: " + `numberOfFramesPerProjection`
    print "numberofProjections: " + `numberofProjections`
    print "isContinuousScan: " + `isContinuousScan`
    print "timeDivider: " + `timeDivider`
    print "positionOfBaseAtFlat:" + `positionOfBaseAtFlat`
    print "positionOfBaseInBeam: " + `positionOfBaseInBeam`
    #scan([ix, 0, 200, 0.2])
    print 'Sample Acq#' + `sampleAcquisitionTime`
    #fscan = FastScan("fscan")
    fastScan = FastScan('fastScan')
    tomoScan(positionOfBaseInBeam, positionOfBaseAtFlat, sampleAcquisitionTime, 0, 180, 1, 0, 0, 0, 0, 0, [fastScan])
    
'''
Runs the external program - matlab to evaluate the images collected and provide with resolutions for the motors to move
'''
def runExternalMatlabForTilt(count):
    lastImageFilename = "p_00017.tif"
    finalImageFullPathName = os.path.join(pwd(), lastImageFilename)
    matlabCmdName = '/scratch/i12Workspc_git/gda-dls-beamlines-i12.git/i12/scripts/tomo/call_matlab.sh'
    print "Calling matlab:" + matlabCmdName + "(" + 'create_flatfield' + "," + finalImageFullPathName + "," + str(count) + "," + 'true'
    updateScriptController("Calling matlab:" + matlabCmdName + "(" + 'create_flatfield' + "," + finalImageFullPathName + "," + str(count) + "," + 'true')
    p = Popen([matlabCmdName, 'create_flatfield', finalImageFullPathName, str(count), 'true'], stdout=PIPE, stdin=PIPE, stderr=STDOUT)
    result = ()
    for line in p.stdout:
        if line.__len__() >= 7 and line[0:7] == 'output=':
            splits = line[7:].rstrip().split(',')
            splitsStripped = []
            for x in splits: splitsStripped.append(x.strip())
            if (splits[0] == 'NaN' or splits[1] == 'NaN'):
                raise Exception("Matlab code hasn't executed correctly - returned no values to move motors")
            t2 = [float(x) for x in splitsStripped]
            result = t2[0], t2[1]
        print 'matlab>' + line.rstrip()
        updateScriptController("matlab>" + line.rstrip())
    p.wait()
    return result

def updateScriptController(msg):
    scriptController = f.find("tomoAlignmentConfigurationScriptController")
    if scriptController != None:
        scriptController.update(scriptController, msg)

def doTiltAlignment(module, exposureTime):
    tiltBallLookupTable = f.find("tiltBallRoiLut")
    currSubDir = f.find("GDAMetadata").getMetadataValue("subdirectory")
    ss1_tx = f.find("ss1_tx")
    ss1_theta = f.find("ss1_theta")
    pco = f.find('pco')
    '''Set PCO external triggered to False'''
    isExternalTriggered = pco.isExternalTriggered()
    pco.setExternalTriggered(False)
    ss1_rz = f.find('ss1_rz')
    ss1_rx = f.find('ss1_rx')
    currSs1TxPos = ss1_tx.getPosition() 
    txOffset = tiltBallLookupTable.lookupValue(module, "balloffset")
    pcoTomography = f.find("pcoTomography")
    pcoTomography.abort()
    try:
        minY = tiltBallLookupTable.lookupValue(module, "minY")
        maxY = tiltBallLookupTable.lookupValue(module, "maxY")
        minX = tiltBallLookupTable.lookupValue(module, "minX")
        maxX = tiltBallLookupTable.lookupValue(module, "maxX")
        print 'Setting camera for tilt'
        pcoTomography.setupForTilt(int(minY), int(maxY), int(minX), int(maxX))
        updateScriptController("Camera setup for tilt")
        print 'Moving ss1_tx to ' + `currSs1TxPos + txOffset`
        updateScriptController("Moving ss1_tx from: " + `round(currSs1TxPos, 3)` + " to: " + `round(currSs1TxPos + txOffset, 3)`)
        ss1_tx.moveTo(currSs1TxPos + txOffset)
        f.find("GDAMetadata").setMetadataValue("subdirectory", "tmp")
        print 'Scanning Theta with exposure time (1/2) ' + `exposureTime`
        updateScriptController("Preparing to scan")
        scan([ss1_theta, 0, 340, 20, pco , `exposureTime`])
        updateScriptController("First Scan Complete")
        firstScanFolder = str(pwd())
        updateScriptController("Calling matlab analysis")
        motors_to_move_for_tilt = runExternalMatlabForTilt(1)
        print 'Moving ss1_rz from ' + `ss1_rz.getPosition()` + ' by ' + `motors_to_move_for_tilt[0]`
        updateScriptController('Moving ss1_rz from ' + `round(ss1_rz.getPosition(), 3)` + ' by ' + `round(motors_to_move_for_tilt[0] , 3)`)
        print 'Moving ss1_rx from ' + `ss1_rx.getPosition()` + ' by ' + `motors_to_move_for_tilt[1]`
        updateScriptController('Moving ss1_rx from ' + `round(ss1_rx.getPosition(), 3)` + ' by ' + `round(motors_to_move_for_tilt[1], 3)`)
        ss1_rz.asynchronousMoveTo(ss1_rz.getPosition() - motors_to_move_for_tilt[0])
        ss1_rx.asynchronousMoveTo(ss1_rx.getPosition() - motors_to_move_for_tilt[1])
        while ss1_rz.isBusy() or ss1_rx.isBusy():
            updateScriptController("ss1_rz :" + `round(ss1_rz.getPosition(), 3)` + "  ss1_rx:" + `round(ss1_rx.getPosition(), 3)`)
            sleep(2)
        print 'Scanning Theta with exposure time (2/2) ' + `exposureTime`
        updateScriptController("Preparing to scan (2/2) with exposure time " + `exposureTime`)
        scan([ss1_theta, 0, 340, 20, pco , `exposureTime`])
        secondScanFolder = str(pwd())
        runExternalMatlabForTilt(2)
    except:
        exceptionType, exception, traceback = sys.exc_info()
        handle_messages.log(None, "Problem while doing tilt alignment", exceptionType, exception, traceback, False)
        print "Problem while doing tilt alignment", exception
        raise exception
    finally:
        f.find("GDAMetadata").setMetadataValue("subdirectory", currSubDir)
        if ss1_tx.getPosition != currSs1TxPos:
            ss1_tx.moveTo(currSs1TxPos)
        pco.setExternalTriggered(isExternalTriggered)
        pcoTomography.resetAfterTiltToInitialValues()
    print 'Tomo tilt complete'
    print "TiltReturn:" + firstScanFolder + "," + secondScanFolder
    updateScriptController("TiltReturn:" + firstScanFolder + "," + secondScanFolder)

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
        print "Moving t3_m1z to :" + `t3M1zPosition`
        t3_m1z.asynchronousMoveTo(t3M1zPosition)
        #moving y
        t3m1ZToLookup = t3M1zPosition - t3_m1z.userOffset
        lookupT3M1YVal = lookupT3M1y(moduleNum, t3m1ZToLookup)
        t3m1yOffset = t3_m1y.userOffset
        t3_m1y.asynchronousMoveTo(lookupT3M1YVal + t3m1yOffset)
        print "Moving t3_m1y to :" + `lookupT3M1YVal + t3m1yOffset`
        
        #moving x
        lookupT3xVal = lookupT3x(moduleNum, t3m1ZToLookup)
        t3xOffset = t3_x.userOffset
        t3_x.asynchronousMoveTo(lookupT3xVal + t3xOffset)
        print "Moving t3_x to :" + `lookupT3xVal + t3xOffset`
        #wait for motors to complete
        while t3_m1z.isBusy():
            updateScriptController("Waiting for t3_m1z")
            print "Waiting for t3_m1z"
            sleep(5)
        while t3_m1y.isBusy():
            updateScriptController("Waiting for t3_m1y")
            print "Waiting for t3_m1y"
            sleep(5)
        while t3_x.isBusy():
            updateScriptController("Waiting for t3_x")
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
                 isContinuousScans, desiredResolutions, timeDividers, positionOfBaseAtFlats, positionOfBaseInBeam):
        if self.currentConfigInProgress != None:
            updateScriptController('Tomography Scan already in progress...')
            print "Tomography Scan already in progress..."
            return
        self.tomoAlignmentConfigurations.clear()
        for i in range(length):
            t = TomoAlignmentConfiguration(self, configIds[i], descriptions[i], moduleNums[i], motorMoveMaps[i], sampleAcquisitionTimes[i], flatAcquisitionTimes[i], numberOfFramesPerProjections[i], numberofProjectionss[i],
                 isContinuousScans[i], desiredResolutions[i], timeDividers[i], positionOfBaseAtFlats[i], positionOfBaseInBeam[i])
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
        print self.currentConfigInProgress
        updateScriptController('RunningConfig#' + `self.currentConfigInProgress`)
        
    def runConfigs(self):
        #print "runconfigs"
        commandQ = Finder.getInstance().find("commandQueueProcessor")
        for i in range(len(self.tomoAlignmentConfigurations)):
            config = self.tomoAlignmentConfigurations[i]
            cmdToQueue = 'tomoAlignment.tomographyConfigurationManager.tomoAlignmentConfigurations[' + `i` + '].doTomographyAlignmentAndScan()'
#            print 'Queued command:' + cmdToQueue
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
                 isContinuousScan, desiredResolution, timeDivider, positionOfBaseAtFlat, positionOfBaseInBeam):
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
        self.status = None
        pass
    
    def doTomographyAlignmentAndScan(self):
        scriptController = Finder.getInstance().find("tomoAlignmentConfigurationScriptController")
        try:
            self.status = "Running"
            self.tomographyConfigurationManager.setConfigRunning(self.configId)
            print 'Aligning module'
            checkForPauses()
            moveToModule(self.moduleNum)
            print 'Aligning alignment motors'
            checkForPauses()
            moveTomoAlignmentMotors(self.motorMoveMap)
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
