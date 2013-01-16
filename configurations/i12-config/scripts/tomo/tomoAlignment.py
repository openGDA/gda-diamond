"""
Performs software triggered tomography
"""

from bisect import bisect_left, bisect_right
from gda.commandqueue import JythonCommandCommandProvider
from gda.factory import Finder
from gdascripts.messages import handle_messages
from time import sleep, gmtime, strftime
from tomographyScan import tomoScan
import math
import sys
import os
import subprocess
from fast_scan import FastScan
from topup_pause import TopupPause
from gda.jython.ScriptBase import checkForPauses
from i12utilities import setSubdirectory, cfn
from i12utilities import pwd
from gda.configuration.properties import LocalProperties
from gda.jython.commands.ScannableCommands import scan
import scisoftpy as dnp
verbose = True
f = Finder.getInstance()

from gda.data import NumTracker
from gda.data import PathConstructor
from gda.util import PropertyUtils
import uk.ac.diamond.scisoft.analysis.dataset.Image as Image
import uk.ac.gda.tomography.TomographyResourceUtil
import uk.ac.gda.tomography.parameters.TomoParametersFactory as TomoParametersFactory

"""
Performs software triggered tomography
"""
def isLiveMode():
    gdaMode = LocalProperties.get("gda.mode")
    print gdaMode
    if gdaMode == "live" or gdaMode == "localhost":
        return True
    return False

def tomoScani12(description, sampleAcquisitionTime, flatAcquisitionTime, numberOfFramesPerProjection,
                 isContinuousScan, desiredResolution, timeDivider, positionOfBaseAtFlat= -100.0, positionOfBaseInBeam=0.0, isToBeReconstructed=False, minY=0, maxY=2672):
    #
    if verbose:
        print "About to start tomography scan"
    stepsSize = f.find('scanResolutionLut').lookupValue(desiredResolution, "Stepsize")
    ##numprojections = {1:6000, 2:3000, 4:3000, 8:900}
    xBin = f.find('scanResolutionLut').lookupValue(desiredResolution, "XBin")
    yBin = f.find('scanResolutionLut').lookupValue(desiredResolution, "YBin")
    exposureVsRes = f.find('scanResolutionLut').lookupValue(desiredResolution, "ExposureToDivideBy")
    updateScriptController("Tomo scan starting")
    timeDividedAcq = sampleAcquisitionTime * timeDivider
    timeDividedAcq = timeDividedAcq / int(exposureVsRes)
    
    pco = f.find("pco")
    pco.stop();
    '''Setting the camera to is 2-ADC'''
    pco.setADCMode(1)  
    pco.setExternalTriggered(isLiveMode())
        
    if verbose:
        print "pco external triggered:" + `pco.isExternalTriggered()`
    #
    adBase = pco.getController().getAreaDetector()
    pco.getController().getProc1().getPluginBase().disableCallbacks()
    pco.getController().getProc2().getPluginBase().disableCallbacks()
    pco.getController().getRoi1().getPluginBase().disableCallbacks()
    pco.getController().getRoi2().getPluginBase().disableCallbacks()
    pco.getController().getArray().getPluginBase().disableCallbacks()
    pco.getController().getMJpeg1().getPluginBase().disableCallbacks()
    pco.getController().getMJpeg2().getPluginBase().disableCallbacks()
    
    cachedBinX = adBase.getBinX()
    cachedBinY = adBase.getBinY()
    try:
        pco.getController().disarmCamera()
        setAdBaseRoi(adBase, pco, int(xBin), int(yBin), minY, maxY - minY)
    except:
        exceptionType, exception, traceback = sys.exc_info()
        print "Problem moving tomo alignment motors" + `exception`
    if verbose:
        print "Tomo scan starting"
        print "type : " + `stepsSize`
        print "Description: " + `description`
        print "Sample acquisition time: " + `sampleAcquisitionTime`
        print "flatAcquisitionTime: " + `flatAcquisitionTime`
        print "numberOfFramesPerProjection: " + `numberOfFramesPerProjection`
        print "isContinuousScan: " + `isContinuousScan`
        print "timeDivider: " + `timeDivider`
        print "positionOfBaseAtFlat:" + `positionOfBaseAtFlat`
        print "positionOfBaseInBeam: " + `positionOfBaseInBeam`
        print "desiredResolution: " + `int(desiredResolution)`
        print 'Sample Acq#' + `sampleAcquisitionTime`
        print 'Sample Acq Time divided#' + `timeDividedAcq`
    fastScan = FastScan('fastScan')
    topUp = TopupPause("topUp")
    isTomoScanSuccess = True
    numberOfDarks = 10 
    numberOfFlats = 10
    #stepsSize = 90
    
    try:
        pco.getController().disarmCamera()
        startTime = strftime("%Y-%m-%d %H:%M:%S", gmtime())
        #tomoScan(description, positionOfBaseInBeam, positionOfBaseAtFlat, timeDividedAcq, 0, 180, stepsSize, 0, 0, 1, 1, 0, additionalScannables=[fastScan],topUp])
        tomoScan(description, positionOfBaseInBeam, positionOfBaseAtFlat, timeDividedAcq, 0, 180, stepsSize, 0, 0, numberOfDarks, numberOfFlats, 0, additionalScannables=[fastScan])
        endTime = strftime("%Y-%m-%d %H:%M:%S", gmtime())
        scanNumber = int(cfn())
    except Exception, ex:
        print "in exception"
        isTomoScanSuccess = False
    finally:
        pco.getController().disarmCamera()
        #
        setAdBaseRoi(adBase, pco, cachedBinX, cachedBinY, 1, 2672)
        #
        if not isTomoScanSuccess:
            raise Exception ("ERROR running tomoScan: " + str(ex))
    
    if isTomoScanSuccess and isToBeReconstructed:
        try:
            inNXSFile = getPathToNXSFile()
            outDir = getPathToOutputDir()
            localTomoFile = getPathToLocalTomoFile()
            templateSettingsFile = getPathToTemplateSettingsFile()
            launchRecon(inNXSFile, outDir, localTomoFile, templateSettingsFile)
        except Exception, ex:
            raise Exception ("Error launching reconstruction: " + str(ex))
    return {"StartTime":startTime, "EndTime":endTime, "ScanNumber":scanNumber}

def setAdBaseRoi(adBase, pco, xBin, yBin, minY, sizeY):
    adBase.setBinX(xBin)
    adBase.setBinY(yBin)
    adBase.setMinY(minY)
    adBase.setSizeY(sizeY)
    initialisePCOPlugins(pco)

def initialisePCOPlugins(pco):
    pcoController = pco.getController()
    adBase = pcoController.getAreaDetector()
    
    pcoController.stop()
    pcoController.disarmCamera()
    sleep(2)
    tiff = pcoController.getTiff()
    isTiffCallbackEnabled = tiff.getPluginBase().isCallbacksEnabled_RBV()
    
    tiff.getPluginBase().enableCallbacks()
    tiff.getPluginBase().setNDArrayPort(adBase.getPortName_RBV())
    
    hdf = pcoController.getHdf()
    isHdfCallbackEnabled = hdf.getPluginBase().isCallbacksEnabled_RBV()
    
    hdf.getPluginBase().enableCallbacks()
    hdf.getPluginBase().setNDArrayPort(adBase.getPortName_RBV())
    
    adBase.setAcquireTime(0.5)
    adBase.setImageMode(2)
    adBase.setTriggerMode(0)
    #Works for the time being but need to figure out why this is required to do twice.
    pcoController.armCamera()
    sleep(2)
    adBase.startAcquiring()
    sleep(5)
    adBase.stopAcquiring()
    #caput("BL12I-EA-DET-02:CAM:Acquire", 1)
    pcoController.disarmCamera()
    
    pcoController.armCamera()
    sleep(2)
    adBase.startAcquiring()
    sleep(3)
    adBase.stopAcquiring()
    #caput("BL12I-EA-DET-02:CAM:Acquire", 1)
    pcoController.disarmCamera()
    
    if not isTiffCallbackEnabled:
        tiff.getPluginBase().disableCallbacks()
    
    if not isHdfCallbackEnabled:
        hdf.getPluginBase().disableCallbacks()

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
        proc = subprocess.Popen(args, executable=exe_sh, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
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
    dir = PathConstructor.createFromDefaultProperty()
    scan_number = numTracker.getCurrentFileNumber()
    file_path = os.path.join(dir, str(scan_number))
    return file_path + '.nxs'

def getPathToOutputDir(outDirBasename='processing'):
    # the line below uses GDA_DATAWRITER_DIR
    dir = PathConstructor.createFromDefaultProperty()
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
    subdir = f.find("GDAMetadata").getMetadataValue("subdirectory")
    updateScriptController("Subdirectory:" + subdir)
    
def updateScriptController(msg):
    scriptController = f.find("tomoAlignmentConfigurationScriptController")
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
                f.find(motor).asynchronousMoveTo(position)
            except:
                exceptionType, exception, traceback = sys.exc_info()
                if verbose:
                    print "Problem moving tomo alignment motors" + `exception`
                updateScriptController(exception)
        for motor, position in motorMoveMap.iteritems():
            m = f.find(motor)
            while m.isBusy():
                updateScriptController("Aligning Tomo motors:" + m.name + ": " + `round(m.position, 2)`)
                if verbose:
                    print 'waiting for motor ' + `m.getName()` + " to move to " + `position` + " currently at " + `round(m.position, 2)`
                sleep(5)
        if verbose:
            print 'motor moving done'
    except:
        exceptionType, exception, traceback = sys.exc_info()
        if verbose:
            print "Problem moving tomo alignment motors" + `exception`
        updateScriptController(exception)

def getModule():
    cam1_x = f.find("cam1_x")
    cameraModuleLookup = f.find("moduleMotorPositionLUT")
    mod1Lookup = round(cameraModuleLookup.lookupValue(1, "cam1_x"), 2)
    moduleNum = 0
    cam1_xPosition = round(cam1_x.position, 2)
    if cam1_xPosition == mod1Lookup:
        moduleNum = 1
    else:
        mod2Lookup = round(cameraModuleLookup.lookupValue(2, "cam1_x"), 2)
        if cam1_xPosition == mod2Lookup:
            moduleNum = 2
        else:
            mod3Lookup = round(cameraModuleLookup.lookupValue(3, "cam1_x"), 2)
            if cam1_xPosition == mod3Lookup:
                moduleNum = 3
            else:
                mod4Lookup = round(cameraModuleLookup.lookupValue(4, "cam1_x"), 2)
                if cam1_xPosition == mod4Lookup:
                    moduleNum = 4
    #Ravi changed this to test the GUI.
    updateScriptController("Module:" + `moduleNum`)
    return moduleNum
    
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
        cam1_roll = f.find("cam1_roll")
        cameraModuleLookup = f.find("moduleMotorPositionLUT")
        
        ss1RxLookup = cameraModuleLookup.lookupValue(moduleNum, "ss1_rx")
        sampleTiltZ = 0.0
        cameraSafeZ = -10.0
        updateScriptController("Module align:moving ss1_rx to" + `round(ss1RxLookup, 2)`)
        checkForPauses()
        ss1_rx.asynchronousMoveTo(ss1RxLookup)
        while ss1_rz.isBusy():
            updateScriptController("Module align:waiting for ss1_rz to" + `round(ss1_rz.position, 2)`)
            sleep(5)
        
        updateScriptController("Module align:moving ss1_rz to" + `round(sampleTiltZ, 2)`)
        checkForPauses()
        ss1_rz.asynchronousMoveTo(sampleTiltZ)
        
        cam1xLookup = cameraModuleLookup.lookupValue(moduleNum, "cam1_x")
        cam1zLookup = cameraModuleLookup.lookupValue(moduleNum, "cam1_z")
        cam1RollLookup = cameraModuleLookup.lookupValue(moduleNum, "cam1_roll")
        #ss1RzLookup = cameraModuleLookup.lookupValue(moduleNum, "ss1_rz")
        
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
            displayVal = round(ss1_rz.getPosition(), 3)
            updateScriptController("Module align:waiting for ss1_rz:" + `displayVal`)
            sleep(5)
            
        checkForPauses()
        cam1_roll.asynchronousMoveTo(cam1RollLookup)
        #ss1_rz.asynchronousMoveTo(ss1RzLookup)
        
        checkForPauses()
        t3_x.asynchronousMoveTo(t3xLookup)
        checkForPauses()
        t3_m1y.asynchronousMoveTo(t3m1yLookup)
        
        while ss1_rx.isBusy():
            displayVal = round(ss1_rx.getPosition(), 3)
            updateScriptController("Module align:waiting for ss1_rx:" + `displayVal`)
            sleep(5)
        
        while t3_x.isBusy(): 
            displayVal = round(t3_x.getPosition(), 3)
            updateScriptController("Module align:waiting for t3_x " + `displayVal`)
        
        while t3_m1y.isBusy():
            displayVal = round(t3_m1y.getPosition(), 3)
            updateScriptController("Module align:waiting for t3_m1y " + `displayVal`)
            
        while ss1_rz.isBusy():
            displayVal = round(ss1_rz.getPosition(), 3)
            updateScriptController("Module align:waiting for ss1_rz:" + `displayVal`)
            sleep(5)
            
        while cam1_roll.isBusy():
            displayVal = round(cam1_roll.getPosition(), 3)
            updateScriptController("Module align:waiting for cam1_roll:" + `displayVal`)
            sleep(5)
            
        updateScriptController("Module align:complete")
        handle_messages.simpleLog("complete module alignment:")
    except:
        exceptionType, exception, traceback = sys.exc_info()
        updateScriptController(exception)
        handle_messages.log(None, "Cannot change module", exceptionType, exception, traceback, False)

def moveVerticalBy(canMoveY1, moveY2BeforeY3Upwards, position):
    y1 = f.find("ss1_y1")
    y2 = f.find("ss1_y2")
    y3 = f.find("ss1_y3")
    movingUp = position > 0
    remainingToMove = position
    if movingUp:
        print "Moving up:" + `position` 
        if canMoveY1:
            #Move y1 and then y2 and then y3
            remainingToMove = moveVerticalMotorUp(y1, remainingToMove)
        if remainingToMove > 0:
            if moveY2BeforeY3Upwards:
                remainingToMove = moveVerticalMotorUp(y2, remainingToMove)
                if remainingToMove > 0:
                    remainingToMove = moveVerticalMotorUp(y3, remainingToMove)
            else:
                remainingToMove = moveVerticalMotorUp(y3, remainingToMove)
                if remainingToMove > 0:
                    remainingToMove = moveVerticalMotorUp(y2, remainingToMove)
    else:
        print "Moving down" + `position`
        if moveY2BeforeY3Upwards:
            remainingToMove = moveVerticalMotorDown(y3, remainingToMove)
            if remainingToMove < 0:
                remainingToMove = moveVerticalMotorDown(y2, remainingToMove)
        else:
            remainingToMove = moveVerticalMotorDown(y2, remainingToMove)
            if remainingToMove < 0:
                remainingToMove = moveVerticalMotorDown(y3, remainingToMove)
        if canMoveY1 and remainingToMove < 0:
            #Move y1 and then y2 and then y3
            remainingToMove = moveVerticalMotorDown(y1, remainingToMove)
    print "Still remaining to move " + `remainingToMove`
    while y1.isBusy() or y2.isBusy() or y3.isBusy():
        updateScriptController("y1:" + `round(y1.getPosition(), 2)` + "  y2:" + `round(y2.getPosition(), 2)` + "  y3:" + `round(y3.getPosition(), 2)`)
        sleep(2)
    if remainingToMove != 0:
        e = Exception("Cannot complete vertical move - Motors reached limit")
        updateScriptController(e)
        raise e
    print "Vertical Move Complete"
    updateScriptController("Vertical Move Complete")

def moveVerticalMotorUp(motor, remainingToMove):
    motorPos = motor.getPosition()
    motorUpperLimit = motor.getUpperMotorLimit() - 0.2
    if motorPos < motorUpperLimit:
        movable = motorUpperLimit - motorPos
        print "Motor movable" + `motor.getName()` + "  " + `movable`
        print "remaining to move:" + `remainingToMove`
        if remainingToMove > movable:
            toMove = movable
        else:
            toMove = remainingToMove
        remainingToMove = remainingToMove - toMove
        try:
            print `motor.getName()` + "to move to :" + `motorPos + toMove`
            motor.asynchronousMoveTo(motorPos + toMove)
        except:
            exceptionType, exception, traceback = sys.exc_info()
            print "Motor Up:" + `exception`
            updateScriptController(exception)
            remainingToMove = remainingToMove + toMove
    print "remaining to move:" + `remainingToMove`
    return remainingToMove

def moveVerticalMotorDown(motor, remainingToMove):
    #remainingToMove is always negative
    motorPos = motor.getPosition()
    motorLimit = motor.getLowerMotorLimit() + 0.2
    if motorPos > motorLimit:
        movable = motorPos - motorLimit
        if abs(remainingToMove) > abs(movable):
            toMove = abs(movable)
        else:
            toMove = abs(remainingToMove)
        remainingToMove = remainingToMove + toMove
        try:
            print `motor.getName()` + "to move:" + `motorPos - toMove`
            motor.asynchronousMoveTo(motorPos - toMove)
        except:
            exceptionType, exception, traceback = sys.exc_info()
            print "Motor Down:" + `exception`
            updateScriptController(exception)
            remainingToMove = remainingToMove - toMove
    return remainingToMove

def getVerticalMotorPositions():
    print "getting Vertical Motor Positions"
    y1 = f.find("ss1_y1")
    y2 = f.find("ss1_y2")
    y3 = f.find("ss1_y3")
    verticals = {}
    verticals[y1.name] = y1.getPosition()
    verticals[y2.name] = y2.getPosition()
    verticals[y3.name] = y3.getPosition()
    updateScriptController(verticals)
    return verticals

def autoFocus(acqTime):
    cam1_z = f.find("cam1_z")
    pco = f.find("pco")
    print isLiveMode()
    if not isLiveMode():
        pco.setExternalTriggered(False)
    moduleLookup = f.find("moduleMotorPositionLUT")
    module = getModule()
    if module < 1 and module > 4:
        raise Exception("No module set so can't autofocus") 
    cam1zLookup = moduleLookup.lookupValue(module, "cam1_z")
    afxCropStart = int(moduleLookup.lookupValue(module, "AFCropStartX"))
    afyCropStart = int(moduleLookup.lookupValue(module, "AFCropStartY"))
    afxCropEnd = int(moduleLookup.lookupValue(module, "AFCropEndX"))
    afyCropEnd = int(moduleLookup.lookupValue(module, "AFCropEndY"))
    updateScriptController("Scanning cam1_z to auto-focus")
    scan([cam1_z, cam1zLookup - 2, cam1zLookup + 2.2, 0.2, pco, acqTime])
    #scan([cam1_z, -76, -81, .1, pco, 2.5])
    print pwd() + "/projections";
    
    numImgs = 20
    pathname = pwd() + "/projections/"
    updateScriptController("About to analyse images in " + `pathname`)
    autofocusImages(pathname, afxCropStart, afyCropStart, afxCropEnd, afyCropEnd, numImgs)
    #cam1_z.moveTo(nxsModel.entry1.pco.cam1_z[biggestIndex])
    
def loadImageIntoPlot(tiffimageFullPath):
    dataset = dnp.io.load(tiffimageFullPath)[0]
    dataset.metadata = None
    dnp.plot.image(dataset)

def autoFocusRight(pathname, numImgs=51):
    autofocusImages(pathname, 3265, 1137, 3815, 1534, numImgs)

def autoFocusLeft(pathname, numImgs=51):
    autofocusImages(pathname, 111, 974, 565, 1345, numImgs)
    
def autofocusImages(pathname, cropxStart, cropyStart, cropxEnd, cropyEnd, numImgs, shouldPlot=False):
    try:
        index = 0
        biggestSum = 0
        biggestIndex = 0
        imageName = None
        
        for num in range(0, numImgs):
            fileName = pathname + ("p_%05d.tif" % num)
            updateScriptController("Analysing Image: " + `fileName`)
            dataset = dnp.io.load(fileName)[0]
            if shouldPlot:
                dataset.metadata = None
                dnp.plot.image(dataset)
            
            ds = dataset.getSlice([cropyStart, cropxStart], [cropyEnd, cropxEnd], [1, 1])
            
            if shouldPlot:
                dnp.plot.image(ds)
            medianFilter = Image.medianFilter(dnp.abs(ds), [3, 3])
            sobell = Image.sobelFilter(dnp.abs(medianFilter))
            if shouldPlot:
                dnp.plot.image(sobell)
            sobellSum = dnp.abs(sobell).sum()
            print "index:" + `index`
            print "SobellSum:" + `sobellSum`
            if sobellSum > biggestSum :
                biggestSum = sobellSum
                biggestIndex = index
                imageName = fileName
            index = index + 1
            print '________________'
        
        print "BiggestIndex:" + `biggestIndex`
        print "Image Name:" + `imageName`
        nexusFile = pwd() + ".nxs"
        print "Nexus file looking into :" + `nexusFile`
        nxsModel = dnp.io.load(nexusFile)
        cam1_zBestFocusVal = nxsModel.entry1.pco.cam1_z[biggestIndex]
        print cam1_zBestFocusVal
    finally:
        updateScriptController("Complete:\nImage Name:\n" + `str(imageName)` + "\nCam1_z value= " + `cam1_zBestFocusVal`)

class TomoAlignmentConfigurationManager:
    def __init__(self):
        self.tomoAlignmentConfigurations = {}
        self.currentConfigInProgress = None
        self.tomoResourceUtil = uk.ac.gda.tomography.TomographyResourceUtil()
        pass
    
    def getRunningConfig(self):
        updateScriptController('RunningConfig#' + `self.currentConfigInProgress`)
        return self.currentConfigInProgress
    
    def setupTomoScan(self, tomoConfigFilePath):
        print tomoConfigFilePath
        if self.currentConfigInProgress != None:
            updateScriptController('Tomography Scan already in progress...')
            if verbose:
                print "Tomography Scan already in progress..."
            return
        tomoExperimentResource = self.tomoResourceUtil.getResource(tomoConfigFilePath, False)
        self.tomoResourceUtil.reloadResource(tomoExperimentResource)
        tomoExperiment = tomoExperimentResource.getContents()[0]
        tomoExperimentParams = tomoExperiment.getParameters()
        tomoExperimentConfigSet = tomoExperimentParams.getConfigurationSet()
        
        self.tomoAlignmentConfigurations.clear()
        configCount = 0
        for i in range(tomoExperimentConfigSet.size()):
            aC = tomoExperimentConfigSet.get(i)
            if aC.getSelectedToRun():
                self.tomoAlignmentConfigurations[configCount] = TomoAlignmentConfiguration(self, aC)
                configCount = configCount + 1
        self.runConfigs()
    
    def setConfigRunning(self, configId):
        if configId == None:
            self.currentConfigInProgress = None
        else:
            statusList = {}
            for k, v in self.tomoAlignmentConfigurations.iteritems():
                statusList[str(v.configId)] = v.status
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
    def __init__(self, tomographyConfigurationManager, aC):
        self.tomographyConfigurationManager = tomographyConfigurationManager
        self.alignmentConfiguration = aC
        self.configId = aC.id
        self.description = aC.description
        self.moduleNum = aC.detectorProperties.moduleParameters.moduleNumber
        self.sampleAcquisitionTime = aC.sampleExposureTime
        self.flatAcquisitionTime = aC.flatExposureTime
        self.numberOfFramesPerProjection = aC.detectorProperties.numberOfFramerPerProjection
        self.isContinuousScan = (aC.scanMode == "Continuous")
        self.desiredResolution = self.getResolutionInteger(aC.detectorProperties.desired3DResolution)
        self.timeDivider = aC.detectorProperties.acquisitionTimeDivider
        self.positionOfBaseAtFlat = aC.outOfBeamPosition
        self.positionOfBaseInBeam = aC.inBeamPosition
        self.tomoAxisRotation = aC.tomoRotationAxis
        self.minY = aC.detectorProperties.detectorRoi.minY
        self.maxY = aC.detectorProperties.detectorRoi.maxY
        motorPositions = {}
        for i in range(aC.motorPositions.size()):
            motorPosition = aC.motorPositions[i]
            motorPositions[motorPosition.name] = motorPosition.position
        self.motorMoveMap = motorPositions

        self.status = None

    def getResolutionInteger(self, strValue):
        if strValue == "X2":
            return 2
        elif strValue == "X4":
            return 4
        elif strValue == "X8":
            return 8
        return 1
    
    def writeInfoToAlignmentConfiguration(self, result):
        print "StartTime" + `result['StartTime']`
        print "EndTime" + `result['EndTime']`
        print "ScanNumber" + `result['ScanNumber']`
        scanCollected = TomoParametersFactory.eINSTANCE.createScanCollected()
        scanCollected.startTime = result['StartTime']
        scanCollected.endTime = result['EndTime']
        scanCollected.scanNumber = str(result['ScanNumber'])
        self.alignmentConfiguration.getScanCollected().add(scanCollected)
        self.alignmentConfiguration.eResource().save(None)
        
    
    def doTomographyAlignmentAndScan(self):
        scriptController = Finder.getInstance().find("tomoAlignmentConfigurationScriptController")
        try:
            self.status = "Starting"
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
            self.status = "Running"
            self.tomographyConfigurationManager.setConfigRunning(self.configId)
            
            result = tomoScani12(self.description,
                        self.sampleAcquisitionTime,
                        self.flatAcquisitionTime,
                        self.numberOfFramesPerProjection,
                        self.isContinuousScan,
                        self.desiredResolution,
                        self.timeDivider,
                        self.positionOfBaseAtFlat,
                        self.positionOfBaseInBeam,
                        minY=self.minY,
                        maxY=self.maxY)
            self.writeInfoToAlignmentConfiguration(result)
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

