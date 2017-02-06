#detectors.py is the next iteration of pe.py

from time import sleep
from gda.data import NumTracker
#import scisoftpy as dnp

detPVs = {"det1":"BL15J-EA-DET-01:"}
detZebraTimePVs = {"det1":"BL15J-EA-ZEBRA-02:DIV1_DIV"}
detVisitPath = "x:\\2016\\cm14470-5\\processing\\"
detGainNames = {"0.25 pF"  :"0",
                "0.5 pF"  :"1",
                "1 pF"  :"2",
                "2 pF"  :"3",
                "4 pF"  :"4",
                "8 pF"  :"5"}

def detSetupStream(det="det1",repeats=1,dark=False,filename=""):
    """Sets up an HDF stream which is ready to receive frames."""
    #currentScanNumber = NumTracker("i15-1").getCurrentFileNumber() # uses the scan number from GDA
    currentScanNumber = caget(detPVs[det] + "CAM:ArrayCounter_RBV") # thes the counter in the cam tab
    caput(detPVs[det]+"PROC3:EnableCallbacks",0)
    if dark == False:
        hdfPlugin = "HDF5:"
    else:
        hdfPlugin = "HDF5B:"
    if caget(detPVs[det]+hdfPlugin+"Capture") != "0": #If file writer is not idle, reset it
        caput(detPVs[det]+hdfPlugin+"Capture",0)
        sleep(1) #Required if the file-writer already has data in it
    caput(detPVs[det]+hdfPlugin+"NumCapture",repeats)
    caputS(detPVs[det]+hdfPlugin+"FileName",det+"_"+str(currentScanNumber)+"_"+str(filename))
    caput(detPVs[det]+hdfPlugin+"Capture",1)

def detCollection(det="det1",exposureTime=1.,dark=False):
    acquireTime = detGetAcquireTime(det)
    caput(detPVs[det]+"CAM:AcquireTime",exposureTime)
    if (exposureTime % acquireTime) < 1e-10:
        acquisitions = int(exposureTime / acquireTime)
        print "Setting up "+str(acquisitions)+" x "+str(acquireTime)+" second acquisition"
        ##setup the collection
        caput(detPVs[det]+"PROC1:NumFilter",acquisitions)
        caput(detPVs[det]+"PROC3:NumFilter",acquisitions)
        detWaitForNewAcquisition(det)
        detGrabFrameToStream(det,dark,acquisitions)
        print "...collection complete!"
        detRestoreAfterCollect(det)
    else:
        raise Exception("exposureTime time must be a multiple of the acquire time, currently "+str(acquireTime)+" s")

def collectXmasTree():
    """Done with an H2O sample in a Kapton capillary"""
    #detSetDetector("det1",1)
    #detSetupStream(det="det1",repeats=1,dark=True,filename="_dark_xmasTree01")
    #detCollection(det="det1",exposureTime=10.,dark=True)
    detSetupStream(det="det1",repeats=40,dark=False,filename="_xmasTree03")
    d1in
    eh3open
    #pos det1Y 25.224 #centre of detector
    print "moving to base"
    pos det1Y -134.776 #base
    print "grabbing frames?"
    d1out
    detGrabRemainingFramesToStream(det="det1")
    sleep(2)
    inc det1Y -20
    sleep(2)
    d1in
    pos det1Y -34.776 det1Z 800 #Move to bottom of tree
    #Move distances det1Y = 220, det1Z = 600
    #Speeds should match so Z should move 2.73 times quicker than Y
    caput("BL15J-EA-DET-01:Z.VELO",40)
    caput("BL15J-EA-DET-01:Y.VELO",9)
    d1out
    pos det1Y 100.0 det1Z 200 #Move to top of tree while exposing
    d1in
    caput("BL15J-EA-DET-01:Z.VELO",40)
    caput("BL15J-EA-DET-01:Y.VELO",20)

def detQuickCollectDark(det="det1",repeats=1,dark=True):
    detSetupStream(det="det1",repeats=1,dark=True)
    detCollection("det1",acquireTime,True)

def detCollectDark(filename,acquireTime):
    eh3close
    detSetupStream("det1",1,True,filename)
    detCollection("det1",acquireTime,True)

def detCollectSample(filename,acquireTime):
    d1in
    eh3open
    detSetupStream("det1",1,False,filename)
    d1out
    detCollection("det1",acquireTime,False)
    d1in
    eh3close

def detWaitForNewAcquisition(det="det1"):
    acquireTime = detGetAcquireTime(det)
    nextFrame = int(caget(detPVs[det]+"CAM:ArrayCounter_RBV"))+1
    print "Waiting for next new acquisition..."
    waitFor(detPVs[det]+"CAM:ArrayCounter_RBV",nextFrame,checkTime=acquireTime/10.,timeOut=acquireTime*2.)
    print "...ready to collect data!"
    #waitFor(detPVs[det]+"CAM:ArrayCounter_RBV",nextFrame+1,checkTime=0.1,timeOut=acquireTime*2.)

def detEcalCollection(exposure,filename,points=[800,700,600,500,400,300,200]):
    """Energy calibration data collection."""
    #peSetupStream(filename,len(points))
    #sleep(240)
    tempname = filename+"_0_"+str(exposure)+"s"+"_dark"
    detCollectDark(tempname,exposure)
    for i,tempz in enumerate(points):
        pos det1Z tempz
        if i > 0:
            sleep(60)
        pos det1Z
        tempname = filename+"_"+str(i+1)+"_"+str(exposure)+"s"+"_stod_"+str(det1Z.getPosition())+"mm"
        print tempname
        detCollectSample(tempname,exposure)

def detGetAcquireTime(det="det1"):
    zebraTime = float(caget(detZebraTimePVs[det]))
    return zebraTime/1000. #acquireTime in seconds


def detGrabFrameToStream(det="det1",dark=False,acquisitions=1):
    if dark == False:
        hdfPlugin = "HDF5:"
    else:
        caput(detPVs[det]+"PROC2:EnableBackground","0") #For file writing
        hdfPlugin = "HDF5B:"
    acquireTime = detGetAcquireTime(det)
    exposureTime = float(caget("BL15J-EA-DET-01:CAM:AcquireTime"))
    caput(detPVs[det]+"PROC1:EnableCallbacks","0")
    caput(detPVs[det]+"PROC3:EnableCallbacks","0")
    caput(detPVs[det]+"PROC1:ResetFilter","1")
    caput(detPVs[det]+"PROC3:ResetFilter","1")
    caput(detPVs[det]+hdfPlugin+"EnableCallbacks","1")
    nextArrayCounter = int(caget(detPVs[det]+"PROC3:ArrayCounter_RBV")) + acquisitions
    nextFileCounter = int(caget(detPVs[det]+hdfPlugin+"NumCaptured_RBV")) + 1
    caput(detPVs[det]+"PROC1:EnableCallbacks","1")
    caput(detPVs[det]+"PROC3:EnableCallbacks","1")
    waitFor(detPVs[det]+"PROC3:ArrayCounter_RBV",nextArrayCounter,checkTime=acquireTime/10.,timeOut=exposureTime*3.)
    caput(detPVs[det]+"PROC1:EnableCallbacks","0")
    waitFor(detPVs[det]+hdfPlugin+"NumCaptured_RBV",nextFileCounter,checkTime=exposureTime/10.,timeOut=exposureTime*3.+2.)
    caput(detPVs[det]+hdfPlugin+"EnableCallbacks","0")
    if dark == True:
        caput("BL15J-EA-DET-01:PROC2:SaveBackground","1")
        caput("BL15J-EA-DET-01:PROC2:EnableBackground","1")
    
def detGrabRemainingFramesToStream(det="det1"):
    """Sets the HDF writer to grab the remaining frames to the stream in an asynchronous way"""
    hdfPlugin = "HDF5:"
    acquireTime = detGetAcquireTime(det)
    exposureTime = float(caget("BL15J-EA-DET-01:CAM:AcquireTime"))
    caput(detPVs[det]+"PROC1:EnableCallbacks","0")
    caput(detPVs[det]+"PROC3:EnableCallbacks","0")
    caput(detPVs[det]+"PROC1:ResetFilter","1")
    caput(detPVs[det]+"PROC3:ResetFilter","1")
    caput(detPVs[det]+hdfPlugin+"EnableCallbacks","1")
    caput(detPVs[det]+"PROC1:EnableCallbacks","1")
    caput(detPVs[det]+"PROC3:EnableCallbacks","1")

def detRestoreAfterCollect(det="det1"):
    caput(detPVs[det]+"PROC1:NumFilter",1)
    caput(detPVs[det]+"PROC1:ResetFilter",1)
    caput(detPVs[det]+"PROC1:EnableCallbacks","1")

def detQuickFire():
    """Testing script to grab a frame to a stream"""
    acquireTime = detGetAcquireTime("det1")
    caput("BL15J-EA-DET-01:PROC2:EnableCallbacks","0")
    nextCounter = int(caget("BL15J-EA-DET-01:PROC3:ArrayCounter_RBV")) + 1 
    caput("BL15J-EA-DET-01:PROC2:EnableCallbacks","1")
    waitFor("BL15J-EA-DET-01:PROC3:ArrayCounter_RBV",nextCounter,checkTime=acquireTime/10.,timeOut=20)
    caput("BL15J-EA-DET-01:PROC2:EnableCallbacks","0")


def detSetDetector(det="det1",acquireTime=1,setGain=""):
    zebraTime = float(acquireTime * 1000)
    print "Setting aquireTime to "+str(acquireTime)+" s"
    caput(detPVs[det]+"CAM:AcquireTime",acquireTime)
    caput("BL15J-EA-ZEBRA-02:DIV1_DIV",zebraTime)
    if caget("BL15J-EA-DET-01:CAM:ImageMode") != "2" or caget("BL15J-EA-DET-01:CAM:TriggerMode") != "1" or caget("BL15J-EA-DET-01:CAM:Acquire") != "1":
        caput("BL15J-EA-DET-01:CAM:Acquire","0")
        waitFor("BL15J-EA-DET-01:CAM:DetectorState_RBV","0",checkTime=0.5,timeOut=20) #Wait for Idle
        caput("BL15J-EA-DET-01:CAM:ImageMode","2")
        caput("BL15J-EA-DET-01:CAM:TriggerMode","1")
        caput("BL15J-EA-DET-01:CAM:Acquire","1")
        waitFor("BL15J-EA-DET-01:CAM:DetectorState_RBV","1",checkTime=0.5,timeOut=20) #Wait for Acquire 
    setGain = str(setGain)
    getGain = caget("BL15J-EA-DET-01:CAM:PEGain")
    initializeRequired = False
    if setGain != "":
        if setGain == "0.25 pF" or setGain == "0":
            if getGain != "0":
                initializeRequired = True
                caput("BL15J-EA-DET-01:CAM:PEGain","0")
                print "Changing gain to 0.25 pF"
            else:
                print "Gain change not required; already at 0.25 pF"
        if setGain == "0.5 pF" or setGain == "1":
            if getGain != "1":
                initializeRequired = True
                caput("BL15J-EA-DET-01:CAM:PEGain","1")
                print "changing gain to 0.5 pF"
            else:
                print "Gain change not required; already at 0.5 pF"
        if setGain == "1 pF" or setGain == "2":
            if getGain != "2":
                initializeRequired = True
                caput("BL15J-EA-DET-01:CAM:PEGain","2")
                print "Changing gain to 1 pF"
            else:
                print "Gain change not required; already at 1 pF"
        if setGain == "2 pF" or setGain == "3":
            if getGain != "3":
                initializeRequired = True
                caput("BL15J-EA-DET-01:CAM:PEGain","3")
                print "Changing gain to 2 pF"
            else:
                print "Gain change not required; already at 2 pF"
        if setGain == "4 pF" or setGain == "4":
            if getGain != "4":
                initializeRequired = True
                caput("BL15J-EA-DET-01:CAM:PEGain","4")
                print "Changing gain to 4 pF"
            else:
                print "Gain change not required; already at 4 pF"
        if setGain == "8 pF" or setGain == "5":
            if getGain != "5":
                initializeRequired = True
                caput("BL15J-EA-DET-01:CAM:PEGain","5")
                print "Changing gain to 8 pF"
            else:
                print "Gain change not required; already at 8 pF"
        if initializeRequired == True:
            print "Re-initialising detector..."
            caput("BL15J-EA-DET-01:CAM:Acquire","0")
            caput("BL15J-EA-DET-01:CAM:PEInitialize","1")
            waitFor("BL15J-EA-DET-01:CAM:DetectorState_RBV","0",checkTime=0.5,timeOut=20)
            caput("BL15J-EA-DET-01:CAM:ImageMode","Continuous")
            caput("BL15J-EA-DET-01:CAM:TriggerMode","External")
            caput("BL15J-EA-DET-01:CAM:Acquire","1")
            print "Detector ready! (but probably not stable)"

def detSetAreaDetector(det="det1"):
    """Script to set up the areaDetector plug-in chain for grabbed detector collections"""
    ##roi (work-around until GDA array view stops setting AD values)
    caput(detPVs[det]+"ROI:NDArrayPort","pe1.proc.proc2")
    caput(detPVs[det]+"ROI:EnableCallbacks","1")
    caput(detPVs[det]+"ROI:MinCallbackTime","0.0")
    caput(detPVs[det]+"ROI:BlockingCallbacks","0")
    caput(detPVs[det]+"ROI:EnableScale","0")
    caput(detPVs[det]+"ROI:EnableZ","0")
    ##stat
    caput(detPVs[det]+"STAT:NDArrayPort","pe1.proc.proc2")
    caput(detPVs[det]+"STAT:EnableCallbacks","1")
    caput(detPVs[det]+"STAT:MinCallbackTime","0")
    caput(detPVs[det]+"STAT:BlockingCallbacks","0")
    caput(detPVs[det]+"STAT:ComputeStatistics","1")
    ##arr
    caput(detPVs[det]+"ARR:NDArrayPort","pe1.proc.proc2")
    caput(detPVs[det]+"ARR:EnableCallbacks","1")
    caput(detPVs[det]+"ARR:MinCallbackTime","0")
    caput(detPVs[det]+"ARR:BlockingCallbacks","0")
    ##proc
    caput(detPVs[det]+"PROC:NDArrayPort","pe1.proc.proc2")
    caput(detPVs[det]+"PROC:EnableCallbacks","1")
    caput(detPVs[det]+"PROC:MinCallbackTime","0")
    caput(detPVs[det]+"PROC:BlockingCallbacks","0")
    caput(detPVs[det]+"PROC:EnableOffsetScale","1.0")
    caput(detPVs[det]+"PROC:EnableFilter","0")
    caput(detPVs[det]+"PROC:DataTypeOut","1") #Unit8 bit output for mjpg
    ##over
    caput(detPVs[det]+"OVER:EnableCallbacks","0")
    ##fimg
    caput(detPVs[det]+"FIMG:EnableCallbacks","0")
    ##tiff
    caput(detPVs[det]+"TIFF:EnableCallbacks","0")
    ##hdf
    caput(detPVs[det]+"HDF5:NDArrayPort","pe1.proc.proc3")
    caput(detPVs[det]+"HDF5:EnableCallbacks","0")
    caput(detPVs[det]+"HDF5:MinCallbackTime","0")
    caput(detPVs[det]+"HDF5:BlockingCallbacks","0")
    caputS(detPVs[det]+"HDF5:FileTemplate","%s%s.hdf5") ##TEMPORARY!!
    caput(detPVs[det]+"HDF5:FileWriteMode","Stream")
    caput(detPVs[det]+"HDF5:Compression_RBV","3") #zlib compression
    caput(detPVs[det]+"HDF5:LazyOpen","1")
    ##mjpg
    caput(detPVs[det]+"MJPG:NDArrayPort","pe1.proc")
    caput(detPVs[det]+"MJPG:EnableCallbacks","1")
    caput(detPVs[det]+"MJPG:MinCallbackTime","0")
    caput(detPVs[det]+"MJPG:BlockingCallbacks","0")
    ##hdfb
    caput(detPVs[det]+"HDF5B:NDArrayPort","pe1.proc.proc3")
    caput(detPVs[det]+"HDF5B:EnableCallbacks","0")
    caput(detPVs[det]+"HDF5B:MinCallbackTime","0")
    caput(detPVs[det]+"HDF5B:BlockingCallbacks","0")
    caputS(detPVs[det]+"HDF5B:FileTemplate","%s%s.hdf5") ##TEMPORARY!!
    caput(detPVs[det]+"HDF5B:FileWriteMode","Stream")
    caput(detPVs[det]+"HDF5B:Compression_RBV","3") #zlib compression
    caput(detPVs[det]+"HDF5B:LazyOpen","1")
    ##tfm
    caput(detPVs[det]+"TFM:NDArrayPort","pe1.cam")
    caput(detPVs[det]+"TFM:EnableCallbacks","1")
    caput(detPVs[det]+"TFM:MinCallbackTime","0")
    caput(detPVs[det]+"TFM:BlockingCallbacks","0")
    caput(detPVs[det]+"TFM:Type","3") #Correct rotation
    ##proc1 - recursive averaging
    caput(detPVs[det]+"PROC1:NDArrayPort","pe1.tfm")
    caput(detPVs[det]+"PROC1:EnableCallbacks","1")
    caput(detPVs[det]+"PROC1:MinCallbackTime","0")
    caput(detPVs[det]+"PROC1:BlockingCallbacks","1")
    caput(detPVs[det]+"PROC1:EnableBackground","0")
    caput(detPVs[det]+"PROC1:EnableFilter","1")
    caput(detPVs[det]+"PROC1:FilterType","0") #RecursiveAve
    caput(detPVs[det]+"PROC1:NumFilter","1")
    caput(detPVs[det]+"PROC1:FilterCallbacks","0") #Every array
    caput(detPVs[det]+"PROC1:DataTypeOut","4") #Int32 bit output
    ##proc2 - dark subtraction
    caput(detPVs[det]+"PROC2:NDArrayPort","pe1.proc.proc1")
    caput(detPVs[det]+"PROC2:EnableCallbacks","1")
    caput(detPVs[det]+"PROC2:MinCallbackTime","0")
    caput(detPVs[det]+"PROC2:BlockingCallbacks","1")
    caput(detPVs[det]+"PROC2:EnableBackground","1")
    caput(detPVs[det]+"PROC2:EnableFilter","0")
    ##proc3 - gated filter for file writer
    caput(detPVs[det]+"PROC3:NDArrayPort","pe1.proc.proc2")
    caput(detPVs[det]+"PROC3:EnableCallbacks","1")
    caput(detPVs[det]+"PROC3:MinCallbackTime","0")
    caput(detPVs[det]+"PROC3:BlockingCallbacks","1")
    caput(detPVs[det]+"PROC3:EnableBackground","0")
    caput(detPVs[det]+"PROC3:EnableFilter","1")
    caput(detPVs[det]+"PROC3:FilterType","5") #Copy to filter
    caput(detPVs[det]+"PROC3:NumFilter","1")
    caput(detPVs[det]+"PROC3:FilterCallbacks","1") #Array N only
    caput(detPVs[det]+"PROC3:DataTypeOut","4") #Int32 bit output
    ##stat1
    caput(detPVs[det]+"STAT:NDArrayPort","pe1.cam")
    caput(detPVs[det]+"STAT:EnableCallbacks","1")
    caput(detPVs[det]+"STAT:MinCallbackTime","0")
    caput(detPVs[det]+"STAT:BlockingCallbacks","0")
    caput(detPVs[det]+"STAT:ComputeStatistics","1")
    ##Set path for filewriters
    peSetPath(path=peVisitPath)

def det1ResetEPICS():
    pvstem = "BL15J-EA-DET-01:"
    caput(pvstem+"Y.HLM","10.1")
    caput(pvstem+"Y.LLM","-10.1")
    caput(pvstem+"Z.HLM","801")
    caput(pvstem+"Z.LLM","199")
    caput(pvstem+"Z.OFF","676.1561")

def peSetPath(path=peVisitPath):
    if path[:2] != "x:" :
        path = peVisitPath + path
    caputS("BL15J-EA-DET-01:HDF5:FilePath",path)
    caputS("BL15J-EA-DET-01:HDF5B:FilePath",path)
    sleep(3)
    if caget("BL15J-EA-DET-01:HDF5:FilePathExists_RBV") != "1" or caget("BL15J-EA-DET-01:HDF5B:FilePathExists_RBV") != "1":
        print "Directory has not been recognised. Make sure that it exists."

print "detectors scripts loaded"