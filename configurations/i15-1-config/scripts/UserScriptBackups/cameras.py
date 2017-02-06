from time import sleep

camList = ["cam1","cam2","bpm1","bpm2","eye"]
bpmList = ["bpm1","bpm2"]
camPVs = {"cam1":"BL15J-DI-CAM-01:",
          "cam2":"BL15J-DI-CAM-02:",
          "bpm1":"BL15J-DI-BPM-01:",
          "bpm2":"BL15J-DI-BPM-02:",
          "eye" :"BL15J-DI-EYE-01:"}
camColour = {"cam1":True,
             "cam2":True,
             "bpm1":False,
             "bpm2":False,
             "eye" :False}
camArrayPort = {"cam1":"JCAM1",
                "cam2":"JCAM2",
                "bpm1":"JBPM1",
                "bpm2":"JBPM2",
                "eye" :"JEYE1"}

camVisitPath = "/dls/i15-1/data/2016/cm14470-4/processing/"

def camReset(cam):
    if cam not in camPVs.keys():
        print "Camera \"%s\" not recognised." % cam
        return
    
    if caget(camPVs[cam]+"CAM:DetectorState_RBV") == "9":
        print "Attempting to reconnect to camera %s" % cam
        caput(camPVs[cam]+"CAM:RESET.PROC",0)
        #waitFor(camPVs[cam]+"CAM:DetectorState_RBV","0",checkTime=1,timeOut=30)
        
    #cam tab
    caput(camPVs[cam]+"CAM:AcquireTime","0.1")
    caput(camPVs[cam]+"CAM:AcquirePeriod","0.25")
    if camColour[cam] == True:
        caput(camPVs[cam]+"CAM:DataType","UInt8")
        caput(camPVs[cam]+"CAM:ColorMode","RGB1")
    else:
        caput(camPVs[cam]+"CAM:DataType","UInt16")
        caput(camPVs[cam]+"CAM:ColorMode","Mono")
    caput(camPVs[cam]+"CAM:Gain","0.0")
    caput(camPVs[cam]+"CAM:GainAuto",0)
    caput(camPVs[cam]+"CAM:ExposureAuto",0)
    caput(camPVs[cam]+"CAM:BalanceWhiteAut0",0)
    caput(camPVs[cam]+"CAM:TriggerSource",5)
    
    #roi tab
    caput(camPVs[cam]+"ROI:EnableCallbacks",1)
    caput(camPVs[cam]+"ROI:MinCallbackTime",0)
    caput(camPVs[cam]+"ROI:NDArrayPort",camArrayPort[cam]+".cam")
    if cam == "cam2":
        caput(camPVs[cam]+"ROI:NDArrayPort","JCAM2.cam")
        caput(camPVs[cam]+"ROI:ReverseX","Yes")
        caput(camPVs[cam]+"ROI:ReverseY","Yes")
    caput(camPVs[cam]+"ROI:DataTypeOut",8)
    #if cam == "eye":
        #SET UP THE ADPYTHON SMALLER ROI HERE!

    #stat tab
    caput(camPVs[cam]+"STAT:EnableCallbacks",1)
    caput(camPVs[cam]+"STAT:NDArrayPort",camArrayPort[cam]+".roi")
    caput(camPVs[cam]+"STAT:MinCallbackTime",0)
    caput(camPVs[cam]+"STAT:BlockingCallbacks",0)
    caput(camPVs[cam]+"STAT:ComputeStatistics",1)
    caput(camPVs[cam]+"STAT:ComputeCentroid",0)
    caput(camPVs[cam]+"STAT:ComputeHistogram",0)
    caput(camPVs[cam]+"STAT:ComputeProfiles",0)

    #arr tab
    caput(camPVs[cam]+"ARR:EnableCallbacks",1)
    caput(camPVs[cam]+"ARR:NDArrayPort",camArrayPort[cam]+".roi")
    caput(camPVs[cam]+"ARR:MinCallbackTime",0)
    caput(camPVs[cam]+"ARR:BlockingCallbacks",0)

    #proc
    caput(camPVs[cam]+"PROC:EnableCallbacks",1)
    caput(camPVs[cam]+"PROC:NDArrayPort",camArrayPort[cam]+".roi")
    caput(camPVs[cam]+"PROC:MinCallbackTime",0)
    caput(camPVs[cam]+"PROC:BlockingCallbacks",0)
    if camColour[cam] == True:
        caput(camPVs[cam]+"PROC:EnableBackground",0)
        caput(camPVs[cam]+"PROC:EnableFlatField",0)
        caput(camPVs[cam]+"PROC:EnableOffsetScale",0)
    else:
        caput(camPVs[cam]+"PROC:EnableBackground",0)
        caput(camPVs[cam]+"PROC:EnableFlatField",0)
        caput(camPVs[cam]+"PROC:EnableOffsetScale",1)
        caput(camPVs[cam]+"PROC:Offset",0)
        caput(camPVs[cam]+"PROC:Scale",0.0039)
        caput(camPVs[cam]+"PROC:EnableLowClip",0)
        caput(camPVs[cam]+"PROC:EnableHighClip",1)
        caput(camPVs[cam]+"PROC:HighClip",255)
        caput(camPVs[cam]+"PROC:Scale",0.0039)
        caput(camPVs[cam]+"PROC:Scale",0.0039)
    caput(camPVs[cam]+"PROC:EnableFilter",0)
    caput(camPVs[cam]+"PROC:DataTypeOut",1)
    
    #over tab
    if cam == "eye":
        caput(camPVs[cam]+"OVER:EnableCallbacks",1)
        caput(camPVs[cam]+"OVER:MinCallbackTime",0)
        caput(camPVs[cam]+"OVER:NDArrayPort",camArrayPort[cam]+".roi")
        caput(camPVs[cam]+"OVER:1:Use",1)
        caput(camPVs[cam]+"OVER:1:Shape",1) #Rectangle
        caput(camPVs[cam]+"OVER:1:Red",128)
        caput(camPVs[cam]+"OVER:1:Green",128)
        caput(camPVs[cam]+"OVER:1:Blue",128)
        caput(camPVs[cam]+"OVER:1:DrawMode",1) #XOR
        caput(camPVs[cam]+"OVER:1:PositionX",322)
        caput(camPVs[cam]+"OVER:1:SizeX",1292)
        caput(camPVs[cam]+"OVER:1:PositionY",126)
        caput(camPVs[cam]+"OVER:1:SizeY",964)
        caput(camPVs[cam]+"OVER:2:Use",1)
        caput(camPVs[cam]+"OVER:2:Shape",1) #Rectangle
        caput(camPVs[cam]+"OVER:2:Red",128)
        caput(camPVs[cam]+"OVER:2:Green",128)
        caput(camPVs[cam]+"OVER:2:Blue",128)
        caput(camPVs[cam]+"OVER:2:DrawMode",1) #XOR
        caput(camPVs[cam]+"OVER:2:PositionX",321)
        caput(camPVs[cam]+"OVER:2:SizeX",1294)
        caput(camPVs[cam]+"OVER:2:PositionY",125)
        caput(camPVs[cam]+"OVER:2:SizeY",966)
    else:
        caput(camPVs[cam]+"OVER:EnableCallbacks",0)

    #tiff tab
    caput(camPVs[cam]+"TIFF:EnableCallbacks",0)
    caput(camPVs[cam]+"TIFF:NDArrayPort",camArrayPort[cam]+".roi")

    #fimg tab
    caput(camPVs[cam]+"FIMG:EnableCallbacks",0)
    caput(camPVs[cam]+"FIMG:NDArrayPort",camArrayPort[cam]+".roi")

    #hdf tab
    caput(camPVs[cam]+"HDF5:EnableCallbacks",0)
    caput(camPVs[cam]+"HDF5:NDArrayPort",camArrayPort[cam]+".roi.roi6")
    caput(camPVs[cam]+"HDF5:MinCallbackTime",0)
    caput(camPVs[cam]+"HDF5:BlockingCallbacks",0)
    caput(camPVs[cam]+"HDF5:FileWriteMode",2)
    caput(camPVs[cam]+"HDF5:NumRowChunks",caget(camPVs[cam]+"CAM:SizeY"))
    caput(camPVs[cam]+"HDF5:NumColChunks",caget(camPVs[cam]+"CAM:SizeX"))
    caput(camPVs[cam]+"HDF5:NumFramesChunks","1")
    caput(camPVs[cam]+"HDF5:Compression","3") #zlib compression
    caput(camPVs[cam]+"HDF5:ZLevel","6") #zlib compression level

    #mjpg tab
    caput(camPVs[cam]+"MJPG:EnableCallbacks",1)
    caput(camPVs[cam]+"MJPG:MinCallbackTime",0)
    caput(camPVs[cam]+"MJPG:BlockingCallbacks",0)
    if cam == "eye":
        caput(camPVs[cam]+"MJPG:NDArrayPort",camArrayPort[cam]+".over")
    else:
        caput(camPVs[cam]+"MJPG:NDArrayPort",camArrayPort[cam]+".proc")
    caput(camPVs[cam]+"MJPG:MAXW",caget(camPVs[cam]+"CAM:SizeX"))
    caput(camPVs[cam]+"MJPG:MAXH",caget(camPVs[cam]+"CAM:SizeY"))

    #py tab
    if cam[:3] == "bpm" or cam == "eye":
        caput(camPVs[cam]+"PY:NDArrayPort",camArrayPort[cam]+".roi")
        caput(camPVs[cam]+"PY:MinCallbackTime",0.25)
        caput(camPVs[cam]+"PY:BlockingCallbacks",0)
        caputS(camPVs[cam]+"PY:Filename","/dls/science/groups/i15-1/adPython/adPythonComFWHM_"+cam+".py")
        caputS(camPVs[cam]+"PY:Classname","ComFWHM")
        caput(camPVs[cam]+"PY:ReadFile",1)
        caput(camPVs[cam]+"PY:EnableCallbacks",1)

    if caget(camPVs[cam]+"CAM:DetectorState_RBV") == "9":
        print "Could not connect to \"%s\" " % cam
    else:
        print "camReset(\"%s\") complete!" % cam

def camResetAll():
    camReset(cam1)
    camReset(cam2)
    camReset(bpm1)
    camReset(bpm2)
    camReset(eye)
alias camResetAll

def camFlip(cam,flipX=True,flipY=True):
    if cam not in camPVs.keys():
        print "Camera \"%s\" not recognised." % cam
        return
    
    temp = ""
    
    if flipX == True:
        temp = temp + " FlipX done."
        if caget(camPVs[cam]+"ROI:ReverseX")=="1":
            caput(camPVs[cam]+"ROI:ReverseX","0")
        else:
            caput(camPVs[cam]+"ROI:ReverseX","1")
    
    if flipY == True:
        temp = temp + " FlipY done."
        if caget(camPVs[cam]+"ROI:ReverseY")=="1":
            caput(camPVs[cam]+"ROI:ReverseY","0")
        else:
            caput(camPVs[cam]+"ROI:ReverseY","1")
    print "camFlip(\"%s\") complete!" % cam + str(temp)

def bpm1In():
    pos bpm1pneumatic 1
    waitFor("BL15J-DI-BPM-01:STA",3,checkTime=0.5,timeOut=4)
    return True
alias bpm1In

def bpm1Out():
    pos bpm1pneumatic 0
    waitFor("BL15J-DI-BPM-01:STA",1,checkTime=0.5,timeOut=4)
    return True
alias bpm1Out

def bpm2In():
    pos bpm2pneumatic 1
    waitFor("BL15J-DI-BPM-02:STA",3,checkTime=0.5,timeOut=4)
    return True
alias bpm2In

def bpm2Out():
    pos bpm2pneumatic 0
    waitFor("BL15J-DI-BPM-02:STA",1,checkTime=0.5,timeOut=4)
    return True
alias bpm2Out

def checkCam(camera):
    """Checks whether a camera is currently running.
    
    Returns True if a camera is in Acquire state, and False if not."""
    if camera not in camPVs.keys():
        print "Camera %s not recognised." % camera
        return False
    
    if caget(camPVs[camera]+"CAM:DetectorState_RBV") != "1":
        print "Camera %s is not ready. Attempting a quick reset" % camera
        return camQuickReset(camera)
    else:
        return True

def camQuickReset(camera):
    if caget(camPVs[camera]+"CAM:DetectorState_RBV") != "1":
        if caget(camPVs[camera]+"CAM:DetectorState_RBV") == "9": #If it's disconnected
            caput(camPVs[camera]+"CAM:RESET.PROC","1")
            #waitFor(camPVs[camera]+"CAM:DetectorState_RBV","0",checkTime=1.0,timeOut=15.0)
            sleep(15)
        if caget(camPVs[camera]+"CAM:DetectorState_RBV") == "0":
            caput(camPVs[camera]+"ROI6:EnableCallbacks",0)
            caput(camPVs[camera]+"CAM:ImageMode",2) #Continuous
            caput(camPVs[camera]+"CAM:Acquire",1)
            print "Quick reset complete."
            return True
        else:
            print "Quick reset failed."
            return False
    else:
        print "Camera appears to be collecting already."
        return True

def camSetupStream(camera,filename,repeats=1):
    """Sets up an HDF stream which is ready to receive frames."""
    if checkCam(camera) == False:
        return
    camera
    caput(camPVs[camera]+"HDF5:Capture",0)
    caput(camPVs[camera]+"ROI6:EnableCallbacks",0)
    caput(camPVs[camera]+"HDF5:NumCapture",repeats)
    caputS(camPVs[camera]+"HDF5:FileName",filename)
    caput(camPVs[camera]+"HDF5:Capture",1)
    caput(camPVs[camera]+"HDF5:EnableCallbacks",1)

def camGrabFrameToStream(camera,newAcquireTime=""):
    """Grabs a single frame and sends it to the current HDF5 stream
    
    Edited on 15/09/2016 to add ability to change acquireTime upon data collection."""
    acquireTime = max(float(caget(camPVs[camera]+"CAM:AcquireTime")),float(caget(camPVs[camera]+"CAM:AcquirePeriod")))
    caput(camPVs[camera]+"CAM:Acquire",0)
    waitFor(camPVs[camera]+"CAM:Acquire",0,checkTime=0.1,timeOut=acquireTime*2.)
    caput(camPVs[camera]+"CAM:ImageMode",0) #Single
    waitFor(camPVs[camera]+"CAM:ImageMode",0,checkTime=0.1,timeOut=acquireTime*2.)
    if newAcquireTime != "":
        oldAcquireTime = float(caget(camPVs[camera]+"CAM:AcquireTime"))
        caput(camPVs[camera]+"CAM:AcquireTime",newAcquireTime)
        acquireTime = max(float(caget(camPVs[camera]+"CAM:AcquireTime")),float(caget(camPVs[camera]+"CAM:AcquirePeriod"))) 
    nextFrame = int(caget(camPVs[camera]+"HDF5:NumCaptured_RBV")) + 1
    caput(camPVs[camera]+"ROI6:EnableCallbacks",1)
    waitFor(camPVs[camera]+"ROI6:EnableCallbacks",1,checkTime=0.1,timeOut=acquireTime*2.)
    caput(camPVs[camera]+"CAM:Acquire",1)
    waitFor(camPVs[camera]+"HDF5:NumCaptured_RBV",nextFrame,checkTime=acquireTime*0.2,timeOut=acquireTime*2.+10.)
    caput(camPVs[camera]+"ROI6:EnableCallbacks",0)
    waitFor(camPVs[camera]+"ROI6:EnableCallbacks",0,checkTime=0.1,timeOut=acquireTime*2.)
    if newAcquireTime != "":
        caput(camPVs[camera]+"CAM:AcquireTime",oldAcquireTime)
        acquireTime = max(float(caget(camPVs[camera]+"CAM:AcquireTime")),float(caget(camPVs[camera]+"CAM:AcquirePeriod")))
    caput(camPVs[camera]+"CAM:ImageMode",2) #Continuous
    waitFor(camPVs[camera]+"CAM:ImageMode",2,checkTime=0.1,timeOut=acquireTime*2.)
    caput(camPVs[camera]+"CAM:Acquire",1)
    waitFor(camPVs[camera]+"CAM:Acquire",1,checkTime=0.1,timeOut=acquireTime*2.)

def camGrabFrame(camera,filename):
    """Grabs a single frame and saves as an HDF5 with the given filename"""
    camSetupStream(camera,filename)
    camGrabFrameToStream(camera)

def camOptimise(camera,gain=False):
    """Optimises the acquire time or gain of a camera to give the optimal intensity.
    
    An optimisation is done based on the stat max value.
    Optimising based on acquireTime is highly recommended (gain=False).
    At high gain the stat max value normally saturates due to noise, so gain optimisation should be avoided.
    Works for 16 or 8 bit cameras."""
    if caget(camPVs[camera]+"CAM:DataType") == "1": #UInt16
        bitRate = 16
    else:
        bitRate = 8
    upperVal = (2**bitRate * 0.95)
    lowerVal = (2**bitRate * 0.80)
    optimalVal = (2**bitRate * 0.90)
    
    if gain == False:
        optimisePV = "CAM:AcquireTime"
    else:
        optimisePV = "CAM:Gain"
    
    if checkCam(camera) == True:
        optimal = False
        while optimal == False:
            acquireTime = max(float(caget(camPVs[camera]+"CAM:AcquireTime")),float(caget(camPVs[camera]+"CAM:AcquirePeriod")))
            currentVal = float(caget(camPVs[camera]+optimisePV))
            maxVal = float(caget(camPVs[camera]+"STAT:MaxValue_RBV"))
            if maxVal > lowerVal and maxVal < upperVal:
                optimal = True
                return #True
            if maxVal > upperVal:
                if gain == False:
                    newVal = currentVal/2.
                else:
                    newVal = currentVal - 2.
                    if newVal < 0:
                        print "Camera still saturating; cannot be optimised with gain."
                        return
                caput(camPVs[camera]+optimisePV,newVal)
                acquireTime = max(float(caget(camPVs[camera]+"CAM:AcquireTime")),float(caget(camPVs[camera]+"CAM:AcquirePeriod")))
                sleep(acquireTime*2.)
            if maxVal < lowerVal:
                if gain == False:
                    newVal = (optimalVal/maxVal)*currentVal
                else:
                    newVal = currentVal + 2.
                    if newVal > 30:
                        print "Maximum gain reached; cannot be optimised further with gain."
                        return
                caput(camPVs[camera]+optimisePV,newVal)
                acquireTime = max(float(caget(camPVs[camera]+"CAM:AcquireTime")),float(caget(camPVs[camera]+"CAM:AcquirePeriod")))
                sleep(acquireTime*2.)
    print "Done!"
    
def camPyOn(camera):
    caput(camPVs[camera]+"PY:EnableCallbacks",1)
    if caget(camPVs[camera]+"PY:PluginState_RBV") != "0" or float(caget(camPVs[camera]+"PY:DroppedArrays_RBV")) > 0:
        raise NameError("Camera "+str(camera)+" adPython plug-in not working")
    
def camPyOff(camera):
    caput(camPVs[camera]+"PY:EnableCallbacks",0)
    
def pslReset():
    pvstem = "BL15J-EA-PSL-01:"
    
    #caput(pvstem+"CAM:RESET.PROC","1")
    #sleep(10)
    
    #cam tab
    caput(pvstem+"CAM:DataType","1") #UInt16
    
    caput(pvstem+"CAM:BinX","1")
    caput(pvstem+"CAM:MinX","0")
    caput(pvstem+"CAM:SizeX","2016")
    caput(pvstem+"CAM:BinY","1")
    caput(pvstem+"CAM:MinY","0")
    caput(pvstem+"CAM:SizeY","1080")
    
    caput(pvstem+"CAM:AcquireTime","1")
    caput(pvstem+"CAM:NumImages","1")
    caput(pvstem+"CAM:ImageMode","2") #Continuous
    
    caput(pvstem+"CAM:GETFEATURES","1")
    caput(pvstem+"CAM:LEFTSHIFT","1")
    
    caput(pvstem+"CAM:PixelFormat","3") #Mono16
    caput(pvstem+"CAM:Display_mode","1")
    caput(pvstem+"CAM:Preamp_Gain_Mode","1")
    caput(pvstem+"CAM:Best_Fit","1")
    

    caput("BL15J-EA-PSL-01:CAM:Acquire","1") #Turn on acquisition
    print "pslReset complete"
alias pslReset

def camSetPath(camera,path=camVisitPath):
    if path[:4] != "/dls" :
        path = peVisitPath + path
        camPVs[camera]+"CAM:DataType"
    caputS(camPVs[camera]+"HDF5:FilePath",path)
    sleep(2)
    if caget(camPVs[camera]+"HDF5:FilePathExists_RBV") != "1":
        print "Directory has not been recognised. Make sure that it exists."

def camGetAcquireTime(camera):
    acquireTime = max(float(caget(camPVs[camera]+"CAM:AcquireTime")),float(caget(camPVs[camera]+"CAM:AcquirePeriod")))
    return acquireTime

print "cameras scripts loaded"