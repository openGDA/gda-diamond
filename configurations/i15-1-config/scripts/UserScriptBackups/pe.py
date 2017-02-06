from time import sleep
import scisoftpy as dnp

pePV = "BL15J-EA-DET-01:"
peVisitPath = "x:\\2016\\cm14470-5\\processing\\"

def peOn():
    caput("BL15J-EA-DET-01:CAM:Acquire","0") #0 = off, 1 = on
    caput("BL15J-EA-DET-01:CAM:ImageMode","Continuous") #Continuous / Single / Multiple
    caput("BL15J-EA-DET-01:CAM:Acquire","1") #0 = off, 1 = on

def peOff():
    caput("BL15J-EA-DET-01:CAM:Acquire","0") #0 = off, 1 = on
    caput("BL15J-EA-DET-01:CAM:ImageMode","Multiple") #Continuous / Single / Multiple

def peCollectDarkLegacy(exposure):
    caput("BL15J-PS-SHTR-01:CON","Close") #Close / Open / Reset
    peOff()
    caput("BL15J-EA-DET-01:PROC3:EnableBackground","0") #0 = off, 1 = on
    scan x 1 1 1 peLegacy exposure
    caput("BL15J-EA-DET-01:PROC3:SaveBackground","1") #Push button?
    caput("BL15J-EA-DET-01:PROC3:EnableBackground","1") #0 = off, 1 = on
    peOn()

def peCollectDataLegacy(exposure):
    caput("BL15J-PS-SHTR-01:CON","Reset") #Close / Open / Reset
    caput("BL15J-PS-SHTR-01:CON","Open") #Close / Open / Reset
    pos d1pneumatic 0 #d1 out
    sleep(2)
    peOff()
    scan x 1 1 1 peLegacy exposure
    peOn()
    caput("BL15J-PS-SHTR-01:CON","Close") #Close / Open / Reset

def peCollectSampleLegacy(exposure):
    spinOn
    peCollectDarkLegacy(exposure)
    peCollectDataLegacy(exposure)
    peCollectDataLegacy(exposure)
    peCollectDataLegacy(exposure)
    spinOff

def peCollectSampleLegacyPointless(exposure):
    peCollectDarkLegacy(exposure)
    peCollectDataLegacy(exposure)
    
def peTestSetup(acquireTime):
    caput("BL15J-EA-DET-01:CAM:Acquire","0") #0 = off, 1 = on
    caput("BL15J-EA-DET-01:CAM:ImageMode","Continuous") #Continuous / Single / Multiple
    caput("BL15J-EA-DET-01:CAM:AcquireTime",acquireTime)
    caput("BL15J-EA-DET-01:PROC2:EnableOffsetScale","1")
    caput("BL15J-EA-DET-01:CAM:Acquire","1") #0 = off, 1 = on
    frameScale = float(1./acquireTime)
    caput("BL15J-EA-DET-01:PROC2:Scale",frameScale)

def peSetupStream(filename,repeats=1,dark=False):
    """Sets up an HDF stream which is ready to receive frames."""
    caput(pePV+"PROC2:EnableCallbacks",0)
    caput(pePV+"PROC4:EnableCallbacks",0)
    if dark == False:
        caput(pePV+"HDF5:NumCapture",repeats)
        caputS(pePV+"HDF5:FileName",filename)
        caput(pePV+"HDF5:Capture",1)
        caput(pePV+"HDF5:EnableCallbacks",1)
    else:
        caput(pePV+"HDF5B:NumCapture",repeats)
        caputS(pePV+"HDF5B:FileName",filename)
        caput(pePV+"PROC3:EnableBackground","0") #For file writing
        caput(pePV+"PROC5:EnableBackground","0") #For array view
        caput(pePV+"HDF5B:Capture",1)
        caput(pePV+"HDF5B:EnableCallbacks",1)

def peGrabFrameToStream(exposure):
    """Grabs a single frame and sends it to the current HDF5 stream
    
    Does not work for darks, as I don't see why you'd want to do this for a dark."""
    zebraTime = float(caget("BL15J-EA-ZEBRA-02:DIV1_DIV"))
    acquireTime = zebraTime/1000. ##acquireTime in seconds
    acquisitions = int(exposure / acquireTime)
    print "Requesting "+str(acquisitions)+" x "+str(acquireTime)+" second acquisitions"
    
    caput(pePV+"PROC2:EnableCallbacks","0") # to stop premature accumulation
    caput(pePV+"PROC4:EnableCallbacks","0") # to stop premature accumulation
    caput(pePV+"PROC2:FilterType","RecursiveAve")
    caput(pePV+"PROC2:NumFilter",acquisitions)
    caput(pePV+"PROC4:FilterType","RecursiveAve")
    caput(pePV+"PROC4:NumFilter",acquisitions)
    
    nextFrame = int(caget("BL15J-EA-DET-01:CAM:ArrayCounter_RBV"))+1
    print "Waiting for next new frame..."
    waitFor("BL15J-EA-DET-01:CAM:ArrayCounter_RBV",nextFrame,checkTime=0.1,timeOut=acquireTime*2.)
    print "...collecting data..."
    waitFor("BL15J-EA-DET-01:CAM:ArrayCounter_RBV",nextFrame+1,checkTime=0.1,timeOut=acquireTime*2.)
    ##do the collection
    nextCapture = int(caget("BL15J-EA-DET-01:HDF5:NumCaptured_RBV")) + 1
    caput("BL15J-EA-DET-01:HDF5:EnableCallbacks","1")
    caput("BL15J-EA-DET-01:PROC2:EnableCallbacks","1") #For file writing
    caput("BL15J-EA-DET-01:PROC4:EnableCallbacks","1") #For array view
    caput("BL15J-EA-DET-01:PROC2:EnableFilter","1") #For file writing
    caput("BL15J-EA-DET-01:PROC4:EnableFilter","1") #For array view
    sleep(0.1)
    waitFor("BL15J-EA-DET-01:HDF5:NumCaptured_RBV",nextCapture,checkTime=0.1,timeOut=exposure+acquireTime*2)
    #put it back to off afterwards and reset the filter
    caput("BL15J-EA-DET-01:HDF5:EnableCallbacks","0")
    caput("BL15J-EA-DET-01:PROC2:ResetFilter","1") #For file writing
    caput("BL15J-EA-DET-01:PROC4:ResetFilter","1") #For array view
    caput("BL15J-EA-DET-01:PROC4:NumFilter","1")
    caput("BL15J-EA-DET-01:PROC2:EnableCallbacks","0")
    print "...frame collection complete."

def peGrabData(exposure,repeats=1,filename="pe",dark=False):
    """CHANGES TO MAKE
    1. Have one proc for one thing, rather than re-using procs 4/5 to feed the arr.
       Do this by changing which proc feeds the arr, rather than changing the proc behaviour."""
    zebraTime = float(caget("BL15J-EA-ZEBRA-02:DIV1_DIV"))
    acquireTime = zebraTime/1000. ##acquireTime in seconds
    if (exposure % acquireTime) < 1e-10:
        caput("BL15J-EA-CALC-03.P",1) #Flag for collecting data in calc record
        caput("BL15J-EA-CALC-03.M",acquireTime) #Place acquireTime into calc record
        acquisitions = int(exposure / acquireTime)
        print "Requesting "+str(acquisitions)+" x "+str(acquireTime)+" second acquisitions"
        ##setup the collection
        caput("BL15J-EA-DET-01:PROC2:EnableCallbacks","0") # to stop premature accumulation
        caput("BL15J-EA-DET-01:PROC4:EnableCallbacks","0") # to stop premature accumulation
        caput("BL15J-EA-DET-01:PROC2:FilterType","RecursiveAve")
        caput("BL15J-EA-DET-01:PROC2:NumFilter",acquisitions)
        caput("BL15J-EA-DET-01:PROC4:FilterType","RecursiveAve")
        caput("BL15J-EA-DET-01:PROC4:NumFilter",acquisitions)
        if dark == False:
            caput("BL15J-EA-DET-01:PROC4:FilterCallbacks","0") #Out every array #ADDED 31/07/2016
            caput("BL15J-EA-DET-01:HDF5:NumCapture",repeats)
            caputS("BL15J-EA-DET-01:HDF5:FileName",filename)
        else:
            caput("BL15J-EA-DET-01:PROC4:FilterCallbacks","1") #Out array N only
            caput("BL15J-EA-DET-01:HDF5B:NumCapture",repeats)
            caputS("BL15J-EA-DET-01:HDF5B:FileName",filename)
            caput("BL15J-EA-DET-01:PROC3:EnableBackground","0") #For file writing
            caput("BL15J-EA-DET-01:PROC5:EnableBackground","0") #For array view
        ##wait for the next frame
        nextFrame = int(caget("BL15J-EA-DET-01:CAM:ArrayCounter_RBV"))+1
        print "Waiting for next new frame..."
        waitFor("BL15J-EA-DET-01:CAM:ArrayCounter_RBV",nextFrame,checkTime=0.1,timeOut=acquireTime*2.)
        print "...collecting data..."
        waitFor("BL15J-EA-DET-01:CAM:ArrayCounter_RBV",nextFrame+1,checkTime=0.1,timeOut=acquireTime*2.)
        ##do the collection
        if dark == False:
            caput("BL15J-EA-DET-01:HDF5:EnableCallbacks","1")
            caput("BL15J-EA-DET-01:PROC2:EnableCallbacks","1") #For file writing
            caput("BL15J-EA-DET-01:PROC4:EnableCallbacks","1") #For array view
            #waitFor("BL15J-EA-DET-01:PROC2:EnableCallbacks","1",checkTime=0.1,timeOut=10)
            caput("BL15J-EA-DET-01:PROC2:EnableFilter","1") #For file writing
#             caput("BL15J-EA-DET-01:PROC2:ResetFilter","1") #For file writing
            
            caput("BL15J-EA-DET-01:PROC4:EnableFilter","1") #For array view
#             caput("BL15J-EA-DET-01:PROC4:ResetFilter","1") #For array view
            
            caput("BL15J-EA-DET-01:HDF5:Capture","1")
            sleep(0.1)
            waitFor("BL15J-EA-DET-01:HDF5:Capture_RBV",0,checkTime=0.1,timeOut=exposure+acquireTime*2)
            #put it back to off afterwards and reset the filter
            caput("BL15J-EA-DET-01:HDF5:EnableCallbacks","0")
            caput("BL15J-EA-DET-01:PROC2:ResetFilter","1") #For file writing
            caput("BL15J-EA-DET-01:PROC4:ResetFilter","1") #For array view
            caput("BL15J-EA-DET-01:PROC4:NumFilter","1")
            caput("BL15J-EA-DET-01:PROC2:EnableCallbacks","0")
            print "...collection complete!"
        if dark == True:
            caput("BL15J-EA-DET-01:HDF5B:EnableCallbacks","1")
            caput("BL15J-EA-DET-01:PROC2:EnableCallbacks","1")
            caput("BL15J-EA-DET-01:PROC4:EnableCallbacks","1") #For array view
            caput("BL15J-EA-DET-01:PROC2:ResetFilter","1")
            caput("BL15J-EA-DET-01:PROC2:EnableFilter","1")
            caput("BL15J-EA-DET-01:PROC4:ResetFilter","1") #For array view
            caput("BL15J-EA-DET-01:PROC4:EnableFilter","1") #For array view
            caput("BL15J-EA-DET-01:HDF5B:Capture","1")
            waitFor("BL15J-EA-DET-01:HDF5B:Capture_RBV",0,checkTime=0.1,timeOut=exposure+acquireTime*2+20) #20s added 11/09/2016 as it kept timing out for a single 2 s collection
            #put it back to off afterwards
            caput("BL15J-EA-DET-01:HDF5B:EnableCallbacks","0")
            caput("BL15J-EA-DET-01:PROC2:ResetFilter","1")
            caput("BL15J-EA-DET-01:PROC4:ResetFilter","1") #For array view
            caput("BL15J-EA-DET-01:PROC2:EnableCallbacks","0")
            caput("BL15J-EA-DET-01:PROC4:EnableCallbacks","0") #For array view
            caput("BL15J-EA-DET-01:PROC3:SaveBackground","1")
            caput("BL15J-EA-DET-01:PROC3:EnableBackground","1")
            caput("BL15J-EA-DET-01:PROC5:SaveBackground","1") #For array view
            caput("BL15J-EA-DET-01:PROC5:EnableBackground","1") #For array view
            caput("BL15J-EA-DET-01:PROC4:EnableCallbacks","1") #Turn back on array view
            caput("BL15J-EA-DET-01:PROC4:NumFilter","1")
            caput("BL15J-EA-DET-01:PROC4:FilterCallbacks","0") #Out every array
            print "...dark collection complete!"
        print "File "+str(filename)+" written"
        caput("BL15J-EA-CALC-03.P",0) #Flag for collecting data
    else:
        raise Exception("exposure time must be a multiple of the acquire time, currently "+str(acquireTime)+" s")

def peCollectDark(exposure,filename="pe_dark",repeats=1):
    #caput("BL15J-PS-SHTR-01:CON","Close") #Close / Open / Reset
    pos d1pneumatic 1 #d1 closed (in)
    waitFor("BL15J-DI-PHDGN-01:STA","3",checkTime=0.5,timeOut=10) #Closed
    peGrabData(exposure,repeats,filename,dark=True)
    
def peCollectData(exposure,filename="pe",repeats=1):
    #caput("BL15J-PS-SHTR-01:CON","Reset") #Close / Open / Reset
    #caput("BL15J-PS-SHTR-01:CON","Open") #Close / Open / Reset
    # check the hutch is open
    if caget("BL15J-PS-SHTR-01:STA") != "1":
        theMostCommonOfErrors()
    
    pos d1pneumatic 0 #d1 open (out)
    waitFor("BL15J-DI-PHDGN-01:STA","1",checkTime=0.5,timeOut=10) #Open
    peGrabData(exposure,repeats,filename,dark=False)
    pos d1pneumatic 1 #d1 open (out)
    #caput("BL15J-PS-SHTR-01:CON","Close") #Close / Open / Reset
    
def peSetDetector(acquireTime=1,setGain=""):
    zebraTime = float(acquireTime * 1000)
    print "Setting aquireTime to "+str(acquireTime)+" s"
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

def peSetAreaDetectorLegacy():
    """Legacy script to re-set the areaDetector plug-in chain to those required for GDA peLegacy detector scans"""
    ##areaDetector settings for peLegacy data collections required post-IOC reboot
    caput("BL15J-EA-DET-01:ARR:NDArrayPort","pe1.proc.proc3")
    caput("BL15J-EA-DET-01:PROC3:NDArrayPort","pe1.proc.proc2")
    caput("BL15J-EA-DET-01:PROC3:EnableCallbacks","1")
    ##Additional areaDetector settings required since Phil starting fiddling with it
    caput("BL15J-EA-DET-01:PROC2:NDArrayPort","pe1.cam")
    caput("BL15J-EA-DET-01:PROC2:EnableCallbacks","1")
    caput("BL15J-EA-DET-01:PROC2:Scale","1")
    caput("BL15J-EA-DET-01:PROC2:EnableOffsetScale","0")
    caput("BL15J-EA-DET-01:PROC2:EnableFilter","1")
    caput("BL15J-EA-DET-01:PROC2:FilterType","Sum")
    caput("BL15J-EA-DET-01:PROC2:NumFilter","1")
    caput("BL15J-EA-DET-01:PROC3:Scale","1")
    caput("BL15J-EA-DET-01:PROC3:EnableOffsetScale","0")
    caput("BL15J-EA-DET-01:HDF5:FileName","pe")
alias peSetAreaDetectorLegacy

def peSetAreaDetector():
    """Script to set up the areaDetector plug-in chain for grabbed detector collections"""
    print "Please set the desired file path in HDF and HDFB tables"
    ##roi (work-around until GDA array view stops setting AD values)
    caput("BL15J-EA-DET-01:ROI:NDArrayPort","pe1.proc.proc5")
    caput("BL15J-EA-DET-01:ROI:EnableCallbacks","1")
    caput("BL15J-EA-DET-01:ROI:MinCallbackTime","0.0")
    caput("BL15J-EA-DET-01:ROI:BlockingCallbacks","0")
    caput("BL15J-EA-DET-01:ROI:EnableScale","0")
    caput("BL15J-EA-DET-01:ROI:EnableZ","0")
    ##stat
    caput("BL15J-EA-DET-01:STAT:NDArrayPort","pe1.proc.proc5")
    caput("BL15J-EA-DET-01:STAT:EnableCallbacks","1")
    caput("BL15J-EA-DET-01:STAT:MinCallbackTime","0")
    caput("BL15J-EA-DET-01:STAT:BlockingCallbacks","0")
    caput("BL15J-EA-DET-01:STAT:ComputeStatistics","1")
    ##arr
    caput("BL15J-EA-DET-01:ARR:NDArrayPort","pe1.proc.proc5")
    caput("BL15J-EA-DET-01:ARR:EnableCallbacks","1")
    caput("BL15J-EA-DET-01:ARR:MinCallbackTime","0")
    caput("BL15J-EA-DET-01:ARR:BlockingCallbacks","0")
    ##proc
    caput("BL15J-EA-DET-01:PROC:NDArrayPort","pe1.tfm")
    caput("BL15J-EA-DET-01:PROC:EnableCallbacks","1")
    caput("BL15J-EA-DET-01:PROC:MinCallbackTime","0")
    caput("BL15J-EA-DET-01:PROC:BlockingCallbacks","0")
    caput("BL15J-EA-DET-01:PROC:EnableOffsetScale","1.0")
    caput("BL15J-EA-DET-01:PROC:EnableFilter","0")
    caput("BL15J-EA-DET-01:PROC:DataTypeOut","1") #Unit8 bit output for mjpg
    ##over
    caput("BL15J-EA-DET-01:OVER:EnableCallbacks","0")
    ##fimg
    caput("BL15J-EA-DET-01:FIMG:EnableCallbacks","0")
    ##tiff
    caput("BL15J-EA-DET-01:TIFF:EnableCallbacks","0")
    ##hdf
    caput("BL15J-EA-DET-01:HDF5:NDArrayPort","pe1.proc.proc3")
    caput("BL15J-EA-DET-01:HDF5:EnableCallbacks","0")
    caput("BL15J-EA-DET-01:HDF5:MinCallbackTime","0")
    caput("BL15J-EA-DET-01:HDF5:BlockingCallbacks","0")
    caputS("BL15J-EA-DET-01:HDF5:FileTemplate","%s%s.hdf5") ##TEMPORARY!!
    caput("BL15J-EA-DET-01:HDF5:FileWriteMode","Stream")
    caput("BL15J-EA-DET-01:HDF5:Compression_RBV","3") #zlib compression
    caput("BL15J-EA-DET-01:HDF5:LazyOpen","1")
    ##mjpg
    caput("BL15J-EA-DET-01:MJPG:NDArrayPort","pe1.proc")
    caput("BL15J-EA-DET-01:MJPG:EnableCallbacks","1")
    caput("BL15J-EA-DET-01:MJPG:MinCallbackTime","0")
    caput("BL15J-EA-DET-01:MJPG:BlockingCallbacks","0")
    ##hdfb
    caput("BL15J-EA-DET-01:HDF5B:NDArrayPort","pe1.proc.proc5")
    caput("BL15J-EA-DET-01:HDF5B:EnableCallbacks","0")
    caput("BL15J-EA-DET-01:HDF5B:MinCallbackTime","0")
    caput("BL15J-EA-DET-01:HDF5B:BlockingCallbacks","0")
    caputS("BL15J-EA-DET-01:HDF5B:FileTemplate","%s%s.hdf5") ##TEMPORARY!!
    caput("BL15J-EA-DET-01:HDF5B:FileWriteMode","Stream")
    caput("BL15J-EA-DET-01:HDF5B:Compression_RBV","3") #zlib compression
    caput("BL15J-EA-DET-01:HDF5B:LazyOpen","1")
    ##tfm
    caput("BL15J-EA-DET-01:TFM:NDArrayPort","pe1.cam")
    caput("BL15J-EA-DET-01:TFM:EnableCallbacks","1")
    caput("BL15J-EA-DET-01:TFM:MinCallbackTime","0")
    caput("BL15J-EA-DET-01:TFM:BlockingCallbacks","0")
    caput("BL15J-EA-DET-01:TFM:Type","3") #Correct rotation
    ##proc2
    caput("BL15J-EA-DET-01:PROC2:NDArrayPort","pe1.tfm")
    caput("BL15J-EA-DET-01:PROC2:EnableCallbacks","1")
    caput("BL15J-EA-DET-01:PROC2:MinCallbackTime","0")
    caput("BL15J-EA-DET-01:PROC2:BlockingCallbacks","0")
    caput("BL15J-EA-DET-01:PROC2:EnableFilter","1")
    caput("BL15J-EA-DET-01:PROC2:FilterType","0") #RecursiveAve
    caput("BL15J-EA-DET-01:PROC2:NumFilter","1")
    caput("BL15J-EA-DET-01:PROC2:FilterCallbacks","1") #Array N only
    caput("BL15J-EA-DET-01:PROC2:DataTypeOut","4") #Int32 bit output
    ##proc3
    caput("BL15J-EA-DET-01:PROC3:NDArrayPort","pe1.proc.proc2")
    caput("BL15J-EA-DET-01:PROC3:EnableCallbacks","1")
    caput("BL15J-EA-DET-01:PROC3:MinCallbackTime","0")
    caput("BL15J-EA-DET-01:PROC3:BlockingCallbacks","0")
    ##proc4
    caput("BL15J-EA-DET-01:PROC4:NDArrayPort","pe1.tfm")
    caput("BL15J-EA-DET-01:PROC4:EnableCallbacks","1")
    caput("BL15J-EA-DET-01:PROC4:MinCallbackTime","0")
    caput("BL15J-EA-DET-01:PROC4:BlockingCallbacks","0")
    caput("BL15J-EA-DET-01:PROC4:EnableFilter","1")
    caput("BL15J-EA-DET-01:PROC4:FilterType","0") #RecursiveAve
    caput("BL15J-EA-DET-01:PROC4:NumFilter","1")
    caput("BL15J-EA-DET-01:PROC4:FilterCallbacks","0") #Every array
    caput("BL15J-EA-DET-01:PROC4:DataTypeOut","4") #Int32 bit output
    ##proc5
    caput("BL15J-EA-DET-01:PROC5:NDArrayPort","pe1.proc.proc4")
    caput("BL15J-EA-DET-01:PROC5:EnableCallbacks","1")
    caput("BL15J-EA-DET-01:PROC5:MinCallbackTime","0")
    caput("BL15J-EA-DET-01:PROC5:BlockingCallbacks","0")
    ##stat1
    caput("BL15J-EA-DET-01:STAT:NDArrayPort","pe1.cam")
    caput("BL15J-EA-DET-01:STAT:EnableCallbacks","1")
    caput("BL15J-EA-DET-01:STAT:MinCallbackTime","0")
    caput("BL15J-EA-DET-01:STAT:BlockingCallbacks","0")
    caput("BL15J-EA-DET-01:STAT:ComputeStatistics","1")
alias peSetAreaDetector

def peSetPath(path=peVisitPath):
    if path[:2] != "x:" :
        path = peVisitPath + path
    caputS("BL15J-EA-DET-01:HDF5:FilePath",path)
    caputS("BL15J-EA-DET-01:HDF5B:FilePath",path)
    sleep(2)
    if caget("BL15J-EA-DET-01:HDF5:FilePathExists_RBV") != "1" or caget("BL15J-EA-DET-01:HDF5B:FilePathExists_RBV") != "1":
        print "Directory has not been recognised. Make sure that it exists."

def peEcalCollection(exposure,filename,points=[799,700,600,500,400,300,200]):
    """Energy calibration data collection."""
    #peSetupStream(filename,len(points))
    #sleep(240)
    peCollectDark(exposure)
    for i,tempz in enumerate(points):
        pos det1Z tempz
        if i > 0:
            sleep(60)
        #peGrabFrameToStream(exposure)
        pos det1Z
        tempname = filename+"_"+str(i+1)+"_"+str(exposure)+"s"+"_stod_"+str(det1Z.getPosition())+"mm"
        print tempname
        peCollectData(exposure,tempname)

def peSetMonitorROI(cenX = 1890,cenY = 2103,roiSizeX = 250, roiSizeY=67):
    """Sets up to roi6/stat6 to monitor the dark current
    
    previously had roiSizeX = roiSizeY = 750 and centre = 1890,2065. Dean changed it to try and
    avoid the horizontal lines which can mess up the stability monitor. 
    """
    caput(pePV+"ROI6:NDArrayPort","pe1.proc.proc5")
    caput(pePV+"ROI6:EnableCallbacks",1)
    caput(pePV+"ROI6:EnableX",1)
    caput(pePV+"ROI6:EnableY",1)
    caput(pePV+"ROI6:MinX",str(cenX-roiSizeX))
    caput(pePV+"ROI6:SizeX",str(roiSizeX*2))
    caput(pePV+"ROI6:MinY",str(cenY-roiSizeY))
    caput(pePV+"ROI6:SizeY",str(roiSizeY*2))
    caput(pePV+"STAT6:NDArrayPort","pe1.roi.roi6")
    caput(pePV+"STAT6:EnableCallbacks",1)
    caput(pePV+"STAT6:ComputeStatistics",1)
    caput(pePV+"STAT6:ComputeCentroid",0)
    caput(pePV+"STAT6:ComputeHistogram",0)
    caput(pePV+"STAT6:ComputeProfiles",0)
    peDarkIPV = pePV+"STAT6:MeanValue_RBV"
    
def negExp(p1,p2,xdata,*args):
    return p1*dnp.exp(-p2*xdata[0])

def peMonitorStability(setStable=0.01,countedStable=5,preWait=0):
    #pe1statMean = DisplayEpicsPVClass("pe1statMean", "BL15J-EA-DET-01:STAT:MeanValue_RBV", "counts", "%1.4f")
    if preWait > 0:
        print "Waiting for "+str(preWait)+" seconds before starting stability monitor..."
        sleep(preWait)
    peDarkIPV = pePV+"STAT6:MeanValue_RBV"
    zebraTime = float(caget("BL15J-EA-ZEBRA-02:DIV1_DIV"))
    acquireTime = zebraTime/1000. ##acquireTime in seconds
    detReady = False
    xdata = []
    ydata = []
    i = 0
    countStable = 0
    dnp.plot.setdefname('Detector monitor')
    dnp.plot.clear()
    print "Waiting for stability..."
    while detReady == False:
        sleep(acquireTime)
        xdata.append(float(i) * acquireTime)
        currentY = float(caget(peDarkIPV))
        ydata.append(currentY)
        i = i+1
        if i > 5:
            #fr = dnp.fit.fit([negExp, dnp.fit.function.offset], dnp.array(xdata), dnp.array(ydata), [ 3.0, 0.2, currentY], [(-4,4), 0, (currentY-abs(currentY)*10,currentY+abs(currentY)*10)])
            #fr = dnp.fit.fit([negExp, dnp.fit.function.offset], dnp.array(xdata), dnp.array(ydata), [ 3.0, 2., currentY], [0, (0.01,0.000001), (currentY-abs(currentY)*10,currentY+abs(currentY)*10)])
            fr = dnp.fit.fit([negExp, dnp.fit.function.offset], dnp.array(xdata), dnp.array(ydata), [ ydata[0], 0.001, currentY], [0, (0.01,0.000001), (currentY-abs(currentY)*10,currentY+abs(currentY)*10)])
            print(fr)
            plotdata = fr.makeplotdata()
            xdatas = dnp.array(xdata)
            dnp.plot.line(xdatas,plotdata[0], title="Detector stability") #Detector intensity data, blue
            dnp.plot.addline(xdatas,plotdata[1]) #Exponential fit to intensity data, brown
            dnp.plot.addline(xdatas,plotdata[2]) #Difference plot, pink
            dnp.plot.addline(xdatas,plotdata[3]) #Difference offset value, magenta
            dnp.plot.addline(xdatas,plotdata[5]) #Predicted final zero value
            timeStable = dnp.log(setStable)/-fr[1]
            if timeStable < (10 * float(i) * acquireTime):
                dnp.plot.addline(dnp.array([timeStable,timeStable]),dnp.array([plotdata[0].min(),plotdata[0].max()])) #Predicted end time, green
            if xdatas.max() > timeStable:
                countStable = countStable + 1
                print "Stable for "+str(countStable)+" of 5 frames"
            else:
                if countStable > 0:
                    print "Unstable; waiting for stability..."
                countStable = 0
        else:
            xdatas = dnp.array(xdata)
            ydatas = dnp.array(ydata)
            dnp.plot.line(xdatas,ydatas, title="Detector stability monitor")
        if countStable > countedStable-1:
            detReady = True
            print "Detector is stable after "+str(timeStable)+" seconds"
            print "New dark value is " + str(plotdata[5][0])
        if (i*acquireTime) > 900:
            detReady = True
            print "Timed out after 15 mins without reaching stability"
    #print(str(xdata))
    #print(str(ydata))

class LackOfPhotonsException(Exception):
    pass

def theMostCommonOfErrors():
    print "I feel like there's something missing..."
    sleep(1)
    print("... something ..."),
    sleep(0.5)
    print "critical."
    sleep(1)
    raise LackOfPhotonsException("You need to open the shutter")

def peQuickFire():
    caput("BL15J-EA-DET-01:PROC2:EnableCallbacks","0")
    nextCounter = int(caget("BL15J-EA-DET-01:PROC2:ArrayCounter_RBV")) + 1 
    caput("BL15J-EA-DET-01:PROC2:EnableCallbacks","1")
    waitFor("BL15J-EA-DET-01:PROC2:ArrayCounter_RBV",nextCounter,checkTime=0.1,timeOut=20)
    caput("BL15J-EA-DET-01:PROC2:EnableCallbacks","0")

print "pe scripts loaded"

from org.eclipse.scanning.api.annotation.scan import AnnotatedDevice

class PeTestDetector (AnnotatedDevice):
    pass