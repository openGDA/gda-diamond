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
import os
import subprocess
from fast_scan import FastScan
from gda.jython.ScriptBase import checkForPauses
from i12utilities import setSubdirectory
from gdascripts.configuration.properties.localProperties import LocalProperties

verbose = True

from gda.data import NumTracker
from gda.jython import InterfaceProvider
from gda.util import PropertyUtils


"""
Performs software triggered tomography
"""
def tomoScani12(description, sampleAcquisitionTime, flatAcquisitionTime, numberOfFramesPerProjection, numberofProjections,
                 isContinuousScan, desiredResolution, timeDivider, positionOfBaseAtFlat=-100.0, positionOfBaseInBeam=0.0, isToBeReconstructed=False):
    #
    if verbose:
        print "About to start tomography scan"
    steps = {1:0.03, 2:0.06, 4:0.06, 8:0.2}
    ##numprojections = {1:6000, 2:3000, 4:3000, 8:900}
    xBin = {1:1, 2:1, 4:2, 8:2}
    yBin = {1:1, 2:1, 4:2, 8:1}
    exposureVsRes = {1:1, 2:1, 4:4, 8:4}
    updateScriptController("Tomo scan starting")
    timeDividedAcq = sampleAcquisitionTime * timeDivider
    timeDividedAcq = timeDividedAcq / exposureVsRes[desiredResolution]
    pco = Finder.find("pco")
    pco.stop();
    
    pco.setExternalTriggered(False)
    if verbose:
        print "pco external triggered:"+`pco.isExternalTriggered()`
    #
    ad = pco.getController().getAreaDetector()
    
    cachedBinX = ad.getBinX()
    cachedBinY = ad.getBinY() 
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
    isTomoScanSuccess = True
    try:
        #tomoScan(positionOfBaseInBeam, positionOfBaseAtFlat, timeDividedAcq, 0, 180, steps[desiredResolution], 0, 0, 10, 10, 0, additionalScannables=[fastScan])
        tomoScan(positionOfBaseInBeam, positionOfBaseAtFlat, timeDividedAcq, 0, 180, steps[desiredResolution], 0, 0, 10, 10, 0, additionalScannables=[fastScan])
        #tomoScan(positionOfBaseInBeam, positionOfBaseAtFlat, timeDividedAcq, 0, 1, 0.5, 0, 0, 1, 1, 0, additionalScannables=[fastScan]) #fast test
    except Exception, ex:
        isTomoScanSuccess = False
        raise Exception ("ERROR running tomoScan: "+str(ex))
    finally:
        ad.setBinX(cachedBinX)
        ad.setBinY(cachedBinY)
    
    if isTomoScanSuccess and isToBeReconstructed:
        try:
            inNXSFile = getPathToNXSFile()
            outDir = getPathToOutputDir()
            localTomoFile = getPathToLocalTomoFile()
            templateSettingsFile = getPathToTemplateSettingsFile()
            launchRecon(inNXSFile, outDir, localTomoFile, templateSettingsFile)
        except Exception, ex:
            raise Exception ("Error launching reconstruction: "+str(ex))

def launchRecon(inNXSFile, outDir, localTomoFile, templateSettingsFile):
    exe_sh = getPathToReconstructionShellScript()
    exe_py = getPathToReconstructionPythonScript()
    
    args = [exe_sh]
    args += [exe_py]
    #args += ["-h"]
    args += [ "-f", inNXSFile]
    args += [ "-o", outDir]
    args += [ "--local", localTomoFile]
    args += [ "--template", templateSettingsFile]
    args += [ "--sino"]
    args += [ "--recon"]
    args += [ "--quick"]
    print args
    try:
        proc = subprocess.Popen( args, executable = exe_sh, stdout = subprocess.PIPE, stderr = subprocess.PIPE )
        proc.wait()
        (out, err) = proc.communicate()
        print "Return value after spawning reconstruction script was %s\n" % proc.returncode
        print "Reconstruction script's stout...\n", out
        print "Reconstruction script's sterr...\n", err
    except Exception, ex:
        msg = "Error spawning reconstruction script: " + str(ex)
        print msg
        #raise Exception(msg)

def getPathToTomographyReconstructionRoot():
    # eg, '/dls_sw/i12/software/gda_git/gda-tomography.git/uk.ac.diamond.tomography.reconstruction'
    git_dir = PropertyUtils.getExistingDirFromLocalProperties("gda.install.git.loc")
    trr_path = os.path.join(git_dir, 'gda-tomography.git')
    trr_path = os.path.join(trr_path, 'uk.ac.diamond.tomography.reconstruction')
    return trr_path

def getPathToReconstructionShellScript(scriptBasename='tomodo.sh'):
    # eg, "/dls_sw/i12/software/gda_git/gda-tomography.git/uk.ac.diamond.tomography.reconstruction/scripts/tomodo.sh"
    trr_path = getPathToTomographyReconstructionRoot()
    shscript_dir = os.path.join(trr_path, 'scripts')
    shscript_path = shscript_dir + os.sep + scriptBasename
    return shscript_path

def getPathToReconstructionPythonScript(scriptBasename='tomodo.py'):
    # eg, "/dls_sw/i12/software/gda_git/gda-tomography.git/uk.ac.diamond.tomography.reconstruction/scripts/tomodo.py"
    trr_path = getPathToTomographyReconstructionRoot()
    pyscript_dir = os.path.join(trr_path, 'scripts')
    pyscript_path = pyscript_dir + os.sep + scriptBasename
    return pyscript_path

def getPathToNXSFile():
    numTracker = NumTracker(LocalProperties.get(LocalProperties.GDA_BEAMLINE_NAME))
    # the line below uses GDA_DATAWRITER_DIR
    dir = InterfaceProvider.getPathConstructor().createFromDefaultProperty()
    scan_number = numTracker.getCurrentFileNumber()
    file_path = os.path.join(dir, str(scan_number))
    return file_path + '.nxs'

def getPathToOutputDir(outDirBasename='processing'):
    # the line below uses GDA_DATAWRITER_DIR
    dir = InterfaceProvider.getPathConstructor().createFromDefaultProperty()
    outputdir_path = os.path.join(os.path.dirname(dir), outDirBasename)
    return outputdir_path

def getPathToLocalTomoFile(localTomoBasename='localTomo.xml'):
    # eg, '/dls_sw/i12/software/gda/i12-config/properties/localTomo.xml'
    config_dir = LocalProperties.getConfigDir()
    localtomo_dir = os.path.join(config_dir, 'properties')
    localtomofile_path = localtomo_dir + os.sep + localTomoBasename
    return localtomofile_path

def getPathToTemplateSettingsFile(settingsBasename='settings.xml'):
    # eg, '/dls_sw/i12/software/gda_git/gda-tomography.git/uk.ac.diamond.tomography.reconstruction/resources/settings.xml'
    trr_path = getPathToTomographyReconstructionRoot()
    settingsfile_dir = os.path.join(trr_path, 'resources')
    settingsfile_path = settingsfile_dir + os.sep + settingsBasename
    return settingsfile_path

def changeSubDir(subdir):
    setSubdirectory(subdir)
    updateScriptController("Subdirectory set to " + subdir)
    
def getSubdir():
    subdir = Finder.find("GDAMetadata").getMetadataValue("subdirectory")
    updateScriptController("Subdirectory:" + subdir)
    
def updateScriptController(msg):
    scriptController = Finder.find("tomoAlignmentConfigurationScriptController")
    if scriptController != None:
        scriptController.update(scriptController, msg)

def moveTomoAlignmentMotors(motorMoveMap):
    updateScriptController("Moving tomo alignment motors")
    if verbose:
        print 'moveTomoAlignmentMotors'
    try:
        for motor, position in motorMoveMap.iteritems():
            checkForPauses()
            try:
                Finder.find(motor).asynchronousMoveTo(position)
            except:
                exceptionType, exception, traceback = sys.exc_info()
                if verbose:
                    print "Problem moving tomo alignment motors" + `exception`
                updateScriptController(exception)
        for motor, position in motorMoveMap.iteritems():
            m = Finder.find(motor)
            while m.isBusy():
                updateScriptController("Aligning Tomo motors:" + m.name + ": " + `round(m.position, 2)`)
                if verbose:
                    print 'waiting for motor '+`m.getName()`
                sleep(5)
        if verbose:
            print "is ss1_tx busy:" +`Finder.find("ss1_tx").isBusy()`
            print 'motor moving done'
    except:
        exceptionType, exception, traceback = sys.exc_info()
        if verbose:
            print "Problem moving tomo alignment motors" + `exception`
        updateScriptController(exception)

        
def getModule():
    cam1_x = Finder.find("cam1_x")
    cameraModuleLookup = Finder.find("moduleMotorPositionLUT")
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
    motionLut = Finder.find("cameraMotionLUT")
    if moduleNum == 1:
        return motionLut.lookupValue(t3m1ZValue, "m1_t3_x")
    elif moduleNum == 2:
        return motionLut.lookupValue(t3m1ZValue, "m2_t3_x")
    elif moduleNum == 3:
        return motionLut.lookupValue(t3m1ZValue, "m3_t3_x")
    elif moduleNum == 4:
        return motionLut.lookupValue(t3m1ZValue, "m4_t3_x")


def lookupT3x(moduleNum, t3m1ZValue):
    lookupKeys = Finder.find("cameraMotionLUT").getLookupKeys()
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
    t3_m1z = Finder.find("t3_m1z")
    t3_x = Finder.find("t3_x")
    t3_m1z_to_lookup = t3_m1z.getPosition() - t3_m1z.getUserOffset()
    lookupT3xVal = lookupT3x(moduleNum, t3_m1z_to_lookup)
    return lookupT3xVal - t3_x.userOffset

def getT3M1yLookupValue(moduleNum, t3m1ZValue):
    motionLut = Finder.find("cameraMotionLUT")
    if moduleNum == 1:
        return motionLut.lookupValue(t3m1ZValue, "m1_t3_m1y")
    elif moduleNum == 2:
        return motionLut.lookupValue(t3m1ZValue, "m2_t3_m1y")
    elif moduleNum == 3:
        return motionLut.lookupValue(t3m1ZValue, "m3_t3_m1y")
    elif moduleNum == 4:
        return motionLut.lookupValue(t3m1ZValue, "m4_t3_m1y")

def lookupT3M1y(moduleNum, t3m1ZValue):
    lookupKeys = Finder.find("cameraMotionLUT").getLookupKeys()
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
    t3_m1z = Finder.find("t3_m1z")
    t3_m1y = Finder.find("t3_m1y")
    t3_m1z_to_lookup = t3_m1z.getPosition() - t3_m1z.getUserOffset()
    lookupT3m1yVal = lookupT3M1y(moduleNum, t3_m1z_to_lookup)
    return lookupT3m1yVal - t3_m1y.userOffset

'''
move t3_m1z to the desired position, subsequently move t3_x and t3_m1y to positions relevant
'''
def moveT3M1ZTo(moduleNum, t3M1zPosition):
    try:
        t3_m1z = Finder.find("t3_m1z")
        t3_m1y = Finder.find("t3_m1y")
        t3_x = Finder.find("t3_x")
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
        t3_x = Finder.find("t3_x")
        t3_m1y = Finder.find("t3_m1y")
        ss1_rx = Finder.find("ss1_rx")
        ss1_rz = Finder.find("ss1_rz")
        cam1_z = Finder.find("cam1_z")
        cam1_x = Finder.find("cam1_x")
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
        
        cameraModuleLookup = Finder.find("moduleMotorPositionLUT")
        
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
        commandQ = Finder.find("commandQueueProcessor")
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
        scriptController = Finder.find("tomoAlignmentConfigurationScriptController")
        try:
            self.status = "Running"
            self.tomographyConfigurationManager.setConfigRunning(self.configId)
            if verbose:
                print 'Attempting to move into requested module'
            checkForPauses()
            moveToModule(self.moduleNum)
            checkForPauses()
            if verbose:
                print 'Aligning cam stage and sample stage motors'
            moveTomoAlignmentMotors(self.motorMoveMap)
            if verbose:
                print 'All motors in place - starting tomography scan'
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
