from gdascripts.messages import handle_messages
from gda.data import NumTracker
import os
from gda.data import PathConstructor
from gda.factory import Finder
import sys
import gda.device.scannable.DummyScannable
from gda.configuration.properties import LocalProperties
import subprocess
from gda.device import Scannable
from gda.jython.commands.GeneralCommands import ls_names, vararg_alias
from time import sleep
from gda.jython.commands import GeneralCommands
from gda.epics import CAClient
# set up a nice method for getting the latest file path
i12NumTracker = NumTracker("i12");
finder = Finder.getInstance()
ca=CAClient()

def wd():
    dir = PathConstructor.createFromDefaultProperty()
    return dir
    


# function to find the last file path
def pwd():
    dir = PathConstructor.createFromDefaultProperty()
    filenumber = i12NumTracker.getCurrentFileNumber();
    return os.path.join(dir, str(filenumber))
    


# function to find the next file path
def nwd():
    dir = PathConstructor.createFromDefaultProperty()
    filenumber = i12NumTracker.getCurrentFileNumber();
    return os.path.join(dir, str(filenumber + 1))
    
# function to find the next scan number
def nfn():
    filenumber = i12NumTracker.getCurrentFileNumber();
    return filenumber + 1
    
# function to find the next scan number
def cfn():
    filenumber = i12NumTracker.getCurrentFileNumber();
    return filenumber
    

# the subdirectory parts
def setSubdirectory(dirname):
    try:
        finder.find("GDAMetadata").setMetadataValue("subdirectory", dirname)
    except:
        exceptionType, exception, traceback = sys.exc_info()
        handle_messages.log(None, "problem setting metadata value -'subdirectory' to " + dirname, exceptionType, exception, traceback, False)
        print "Failed to set metadata (subdirectory) value to:", dirname, exception
        

def setDataWriterToNexus():
    oldDW = LocalProperties.get("gda.data.scan.datawriter.dataFormat")
    LocalProperties.set("gda.data.scan.datawriter.dataFormat", "NexusDataWriter")
    newDW = LocalProperties.get("gda.data.scan.datawriter.dataFormat")
    print "Old DataWriter: ", oldDW
    print "New DataWriter: ", newDW
    
def setDataWriterToSrs():
    oldDW = LocalProperties.get("gda.data.scan.datawriter.dataFormat")
    LocalProperties.set("gda.data.scan.datawriter.dataFormat", "SrsDataFile")
    newDW = LocalProperties.get("gda.data.scan.datawriter.dataFormat")
    print "Old DataWriter: ", oldDW
    print "New DataWriter: ", newDW
    
def getDataWriter():
    return LocalProperties.get("gda.data.scan.datawriter.dataFormat")
    
class DocumentationScannable(gda.device.scannable.DummyScannable):
    def __init__(self, name, mesg, url=None):
        super(DocumentationScannable, self).__init__(name)
        self.mesg = mesg
        self.url = url
        pass
    
    def __doc__(self):
        hSC = finder.find("helpScriptController")
        if self.url != None and hSC != None:
            #subprocess.Popen(['python2.6', '-m', 'webbrowser', '-t', self.url])
            hSC.update(hSC, "URL:" + `self.url`)
        return self.mesg

def ls_scannables():
    ls_names(Scannable)
    


# FOR NEW PIXIUM
pxm_allowed_PU_Mode = [1, 3, 4, 7, 13, 14, 15]
earlyFrames_translatn={}
earlyFrames_translatn[0]='Off'
earlyFrames_translatn[1]='On'

def includeEarlyFrames():
    pvName = "BL12I-EA-DET-10:CAM:MotionBlur"
    oldVal = int(ca.caget(pvName))
    # set Disregard early frames to 1 for on
    newVal = 1
    ca.caput(pvName, newVal)
    outName = "Disregard Early Frames"
    print "Old " + outName +": ", earlyFrames_translatn[oldVal] + " ("+ `oldVal`+")"
    print "New " + outName +": ", earlyFrames_translatn[newVal] + " ("+ `newVal`+")"

def excludeEarlyFrames():
    pvName = "BL12I-EA-DET-10:CAM:MotionBlur"
    oldVal = int(ca.caget(pvName))
    # set Disregard early frames to 0 for off
    newVal = 0
    ca.caput(pvName, newVal)
    outName = "Disregard Early Frames"
    print "Old " + outName +": ", earlyFrames_translatn[oldVal] + " ("+ `oldVal`+")"
    print "New " + outName +": ", earlyFrames_translatn[newVal] + " ("+ `newVal`+")"

def reportEarlyFrames(verbose=False):
    pvName = "BL12I-EA-DET-10:CAM:MotionBlur"
    outVal = ca.caget(pvName)
    if verbose:
        outVal = earlyFrames_translatn[int(outVal)] + " ("+ outVal+")"
    return outVal

def setBaseExposureTime(newVal):
    pvName = "BL12I-EA-DET-10:CAM:AcquireTime"
    oldVal = float(ca.caget(pvName))
    ca.caput(pvName, newVal)
    outName = "Base Exposure Time"
    print "Old " + outName +": ", `oldVal`
    print "New " + outName +": ", `newVal`

def getBaseExposureTime():
    pvName = "BL12I-EA-DET-10:CAM:AcquireTime_RBV"
    return ca.caget(pvName)

def setBaseAcquisitionTime(newVal):
    pvName = "BL12I-EA-DET-10:CAM:AcquirePeriod"
    oldVal = float(ca.caget(pvName))
    ca.caput(pvName, newVal)
    outName = "Base Acquisition Time"
    print "Old " + outName +": ", `oldVal`
    print "New " + outName +": ", `newVal`

def getBaseAcquisitionTime():
    pvName = "BL12I-EA-DET-10:CAM:AcquirePeriod_RBV"
    return ca.caget(pvName)

def setPUMode(newVal):
    pvName = "BL12I-EA-DET-10:CAM:PuMode"
    oldVal = int(ca.caget(pvName))
    if pxm_allowed_PU_Mode.__contains__(newVal):
        ca.caput(pvName, newVal)
    else:
        msg = "The input value %s is not allowed." %newVal
        msg += " The allowable values are: " + `pxm_allowed_PU_Mode`
        raise Exception(msg)
    outName = "PU Mode"
    print "Old " + outName +": ", `oldVal`
    print "New " + outName +": ", `newVal`

def getPUMode():
    pvName = "BL12I-EA-DET-10:CAM:PuMode_RBV"
    return ca.caget(pvName)

def setExposuresPerImage(newVal):
    pvName ="BL12I-EA-DET-10:CAM:NumExposures"
    oldVal = int(ca.caget(pvName))
    ca.caput(pvName, newVal)
    outName = "Exposures per Image"
    print "Old " + outName +": ", `oldVal`
    print "New " + outName +": ", `newVal`

def getExposuresPerImage():
    pvName ="BL12I-EA-DET-10:CAM:NumExposures_RBV"
    return ca.caget(pvName)

def pixCalibrate(useShutter=False):
    #The steps:
    #close shutter eh1shtr
    #stop detector: BL12I-EA-DET-10:CAM:Acquire (Done(0), Acquire(1))
    #    (BL12I-EA-DET-10:CAM:DetectorState_RBV (Idle(0), Acquiring(2))
    #caput Calibrate (button): BL12I-EA-DET-10:CAM:Calibrate (Calibrate (1), Done(0)
    # Calibration Running: BL12I-EA-DET-10:CAM:Calibrate_RBV (Calibrating(1), Done(0))
    # Calibration Required: BL12I-EA-DET-10:CAM:CalibrationRequired_RBV (Yes(1), No(0))
    
    # relevant PVs
    pvAcquire = "BL12I-EA-DET-10:CAM:Acquire"
    pvDetectorState = "BL12I-EA-DET-10:CAM:DetectorState_RBV"
    pvCalibrate ="BL12I-EA-DET-10:CAM:Calibrate"
    pvCalibrateRBV ="BL12I-EA-DET-10:CAM:Calibrate_RBV"
    
    # close shutter
    eh1shtr = finder.find("eh1shtr")
    
    sleep_time_s = 1    # seconds
    #caput("BL12I-PS-SHTR-02:CON", "Close") ### 1 is closed. 0 is open
    if useShutter:
        ca.caput("BL12I-PS-SHTR-02:CON", "Close")
        pvShutterState = "BL12I-PS-SHTR-02:CON"
        count = 0
        while (ca.caget(pvShutterState)!='Close'):
            GeneralCommands.pause()
            sleep(sleep_time_s)
            count+=1
            print " waited for shutter to close for " + `sleep_time_s` + " s"
    else:
        print "The use of shutter was not requested!"
    
    print " at Shutter State %s: %s" %(eh1shtr.getName(), eh1shtr())
    print " at Detector State: " + ca.caget(pvDetectorState)
    print "Stopping acquisition..."
    
    #stop detector
    ca.caput(pvAcquire, 0)
    count = 0
    while (int(ca.caget(pvDetectorState))!=0):
        GeneralCommands.pause()
        sleep(sleep_time_s)
        count+=1
        print " waited for acquisition to stop for " + `sleep_time_s` + " s"
    print "...acquisition stopped (after %i s):" %(sleep_time_s*count)
    print " at Detector State: " + ca.caget(pvDetectorState)
    
    print "Starting calibration..."
    ca.caput(pvCalibrate, 1)
    count = 0
    while (int(ca.caget(pvCalibrateRBV))!=0):
        GeneralCommands.pause()
        sleep(sleep_time_s)
        count+=1
        print " waited for calibration to complete for " + `sleep_time_s` + " s"
    print "...calibration completed (after %i s):" %(sleep_time_s*count)
    print " at Calibration Running: " + ca.caget(pvCalibrateRBV)
    print " at Detector State: " + ca.caget(pvDetectorState)
    
    baseExposureTime = getBaseExposureTime()
    baseAcquisitionTime = getBaseAcquisitionTime()
    out = "\n"
    out += "Detector calibrated to: \n"
    out += " Base Exposure Time: " + baseExposureTime + "\n"
    out += " Base Acquisition Time: " + baseAcquisitionTime + "\n"
    out += " Shutter %s: %s" %(eh1shtr.getName(), eh1shtr())
    return out

