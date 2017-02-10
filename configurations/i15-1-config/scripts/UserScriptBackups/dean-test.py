import scisoftpy as dnp
def whichGapSize():
    """a quick script to determine the best gap to use for finding the centre.
    """
    gaps = dnp.arange(0.1,1.1,0.1)
    pos s3gapY 3
    pos s3cenY 0
    for gap in gaps:
        currentDummy1 = dummy1.getActualPosition()
        pos s3gapX gap
        
        print "the gap is " + str(gap)
        scan s3cenX -2 2 0.1 dummy1 currentDummy1+20 9 od1
#         currentDummy1 = dummy1.getActualPosition()
#         pos s3gapX 3
#         pos s3gapY gap
#         scan s3cenY -2 2 0.1 dummy1 currentDummy1+20 9 od1
    print "whichGapSize complete"

def MTWD_collection():
    sleep(30*60)
    
    positions = [-168.9,-179.5,-188.6,-197.8,-206.3]
    names = ["CeO2_30x20s_changer","MTWD42_30x20s_changer","MTWD44_30x20s_changer","MTWD47_30x20s_changer","MTWD63_30x20s_changer"]
    
    for i,position in enumerate(positions):
        pos samX position
        peCollectDark(30*20)
        pos samY 1
        filename = names[i]+"_samY1"
        print filename
        peCollectData(30*20,filename)
        pos samY 0.5
        filename = names[i]+"_samY0p5"
        print filename
        peCollectData(30*20,filename)
        pos samY 0
        filename = names[i]+"_samY0"
        print filename
        peCollectData(30*20,filename)



def lai3_optimism(counttime=60):
    pos samX -140
    velocity = 30./counttime
    caput("BL15J-MO-TABLE-01:SAMPLE:X.VELO",velocity)
    # collect a dark
    peCollectDark(counttime)
    # start the move
    caput("BL15J-MO-TABLE-01:SAMPLE:X.VAL",-110)
    # collect the data
    peCollectData(60,filename="LaI3_insitu_30x2s_0p5pF_v2")
    caput("BL15J-MO-TABLE-01:SAMPLE:X.VELO",counttime)
    

def coarseAlignThoseSlits():
    """ aligns the requested slits. For the moment only does s3. 
    """
    from gda.jython.commands.InputCommands import requestInput as raw_input # needed in absence of peak finding
    ######## DEFINITIONS ########
    XScanSlitWidth = 0.5
    YScanSlitWidth = 0.2
    
    # Remove the user offsets
    print "Removing EPICS User offsets"
    caput("BL15J-AL-SLITS-03:X:SIZE.OFF", 0)
    caput("BL15J-AL-SLITS-03:Y:SIZE.OFF", 0)
    caput("BL15J-AL-SLITS-03:X:CENTER.OFF", 0)
    caput("BL15J-AL-SLITS-03:Y:CENTER.OFF", 0)
    
    # home the motors
    caput("BL15J-AL-SLITS-03:HM:HMGRP", "All")
    sleep(0.2)
    caput("BL15J-AL-SLITS-03:HM:HOME", 1)
    sleep(0.2)
    i = 0
    print("waiting for the motors to home"),
    while caget("BL15J-AL-SLITS-03:HM:HOMING") == "1":
        print("."),
        sleep(1)
        i += 1
        if i % 20 < 0.1:
            print " "
            print "                              ",
        if i > 120:
            raise NameError("Homing timed out") 
    print "homing complete."
    # set slits to nominal centre and fully open
    #pos s3cenX (0.10866-7.6822)/2 
    #positive and negative limits; set halfway between 
    #pos s3gapX 10.0871-0.5 
    #fully open limit, minus 0.5 mm
    #pos s3cenY (8.2584-0.10066)/2 
    #positive and negative limits; set halfway between 
    #pos s3gapY 9.44013-0.5 
    #fully open limit, minus 0.5 mm
    # and now all in one:
    print "Opening the slits to initial configuration"
    pos s3cenX (0.10866-7.6822)/2 s3gapX 10.0871-0.5 s3cenY (8.2584-0.10066)/2 s3gapY 9.44013-0.5 
    ############## LIMITS ############
    #10.0871    -1.31104  ### X gap limits
    #0.10866    -7.6822  #### X cen limits
    #9.44013    -0.10634 ### Y gap limits
    #8.2584    -0.10066 ### Y cen limits
    
    ############## SCANS ############## 
    ################ X ################
    # scan the gap from open` to closed
    print "coarsely locating the x-closed position, starting scan..."
    currentDummy1 = dummy1.getActualPosition()
    scan s3gapX (10.0871-0.5) (-0.0117+0.5) 0.3 dummy1 currentDummy1+20 5 od2
    gapXValue = float(raw_input("Please identify the value at which the slits open "))
    print "Opening the s3gapX to 0.5 mm larger than %f" % gapXValue
    pos s3gapX gapXValue+XScanSlitWidth
    
    # scan the centre across the beam
    print "trying to find the x-centre, starting scan..."
    currentDummy1 = dummy1.getActualPosition()
    scan s3cenX -7.6822+0.5 0.10866-0.5 0.3 dummy1 currentDummy1+20 5 od2
    cenXValue = float(raw_input("Please identify the peak location "))
    print "Moving the slits to the centre"
    pos s3cenX cenXValue
    
    # finer scan to find slit opeing preciesely
    # (currently just a copy of the above scan!)
    print "final alignment of the x-closed position, starting scan..." 
    pos s3gapX gapXValue
    currentDummy1 = dummy1.getActualPosition()
    scan s3gapX gapXValue+1 (-0.0117+0.5) 0.1 dummy1 currentDummy1+20 9 od2
    print "You previously entered"+str(gapXValue)
    gapXValue = -float(raw_input("Please identify the value at which the slits open "))
    # set the offset based on this value
    caput("BL15J-AL-SLITS-03:X:SIZE.OFF",gapXValue)
    pos s3gapX XScanSlitWidth
    
    # scan the centre across the beam
    print "final alignment of the x-centre, starting scan..."
    currentDummy1 = dummy1.getActualPosition()
    scan s3cenX cenXValue-1 cenXValue+1 0.1 dummy1 currentDummy1+20 9 od2
    print "You previously entered"+str(cenXValue)
    cenXValue = -float(raw_input("Please identify the peak location "))
    # set the offset based on this value
    caput("BL15J-AL-SLITS-03:X:CENTER.OFF",cenXValue)
    pos s3cenX 0
    
    ######################################## Y ##########################################################
    #####################################################################################################
    # scan the gap from open to closed
    print "coarsely locating the y-closed position, starting scan..."
    currentDummy1 = dummy1.getActualPosition()
    scan s3gapY (9.44013-0.5) (-0.10634+0.5) 0.3 dummy1 currentDummy1+20 5 od2
    gapYValue = float(raw_input("Please identify the value at which the slits open "))
    print "Opening the s3gapY to 0.5 mm larger than %f" % gapYValue
    pos s3gapY gapYValue+YScanSlitWidth
    
    # scan the centre across the beam
    print "trying to find the y-centre, starting scan..."
    currentDummy1 = dummy1.getActualPosition()
    scan s3cenY -0.10066+0.5 8.2584-0.5 0.3 dummy1 currentDummy1+20 5 od2
    cenYValue = float(raw_input("Please identify the peak location "))
    print "Moving the slits to the centre"
    pos s3cenY cenYValue
    
    # finer scan to find slit opeing preciesely
    # (currently just a copy of the above scan!)
    print "locating the y-closed position, starting scan..." 
    currentDummy1 = dummy1.getActualPosition()
    scan s3gapY gapYValue+1 (-0.10634+0.5) 0.1 dummy1 currentDummy1+20 9 od2
    print "You previously entered"+str(gapYValue)
    gapYValue = -float(raw_input("Please identify the value at which the slits open "))
    # set the offset based on this value
    caput("BL15J-AL-SLITS-03:Y:SIZE.OFF", gapYValue)
    pos s3gapY YScanSlitWidth
    
    # scan the centre across the beam
    print "final alignment of the y-centre, starting scan..."
    currentDummy1 = dummy1.getActualPosition()
    scan s3cenY cenYValue-1 cenYValue+1 0.1 dummy1 currentDummy1+20 9 od2
    print "You previously entered"+str(cenYValue)
    cenYValue = -float(raw_input("Please identify the peak location "))
    # set the offset based on this value
    caput("BL15J-AL-SLITS-03:Y:CENTER.OFF",cenYValue)
    pos s3cenY 0
    print "*****************************************************"
    print "    gapX    |    cenX    ||    gapY    |    cenY    |"
    print " %10.6f   %10.6f   %10.6f   %10.6f" % (gapXValue,cenXValue,gapYValue,cenYValue)
    print "*****************************************************"
    print "                   SLITS ALIGNED                     "
    print "*****************************************************"

def fineAlignSlit():
    """ aligns the requested slits. For the moment only does s4. 
    """
    from gda.jython.commands.InputCommands import requestInput as raw_input # needed in absence of peak finding
    ######## DEFINITIONS ########
    XScanSlitWidth = 0.5
    YScanSlitWidth = 0.5
    
    #print "Opening the slits to initial configuration"
    #pos s4cenX 0 s4gapX 8.98796-0.5 s4cenY 0 s4gapY 9.40104-0.5
    
    ############## SCANS ############## 
    ################ X ################
    ## scan the gap from open` to closed
    print "coarsely locating the x-closed position, starting scan..."
    currentDummy1 = dummy1.getActualPosition()
    scan s4gapX (2*XScanSlitWidth) (0) 0.1 dummy1 currentDummy1+20 5 od2
    gapXValue = float(raw_input("Please identify the value at which the slits open "))
    print "Opening the s4gapX to 0.5 mm larger than %f" % gapXValue
    pos s4gapX gapXValue+XScanSlitWidth
    
    # scan the centre across the beam2016-05-11 12:23:27,285 INFO  gdascripts.messages.handle_messages - ! Failure failed to load all locally-defined epics pvs !

    print "trying to find the x-centre, starting scan..."
    currentDummy1 = dummy1.getActualPosition()
    scan s4cenX -XScanSlitWidth XScanSlitWidth (XScanSlitWidth/10) dummy1 currentDummy1+20 5 od2
    cenXValue = float(raw_input("Please identify the peak location "))
    print "Moving the slits to the centre"
    caput("BL15J-AL-SLITS-03:X:CENTER.OFF",cenXValue)
    pos s3cenX 0
    
    # finer scan to find slit opening precisely
    print "relocating the x-closed position, starting scan..." 
    currentDummy1 = dummy1.getActualPosition()
    scan s4gapX (1*XScanSlitWidth) (-XScanSlitWidth) (XScanSlitWidth/10) dummy1 currentDummy1+20 5 od2
    gapXValue = -float(raw_input("Please identify the value at which the slits open "))
    # set the offset based on this value
    print "setting the closed position..."
    caput("BL15J-AL-SLITS-04:X:SIZE.OFF", float(caget("BL15J-AL-SLITS-04:X:SIZE.OFF"))+gapXValue)
    print "reopening the slit..."
    pos s4gapX XScanSlitWidth
    print "X done"

def testingInputtingANumber():
    from gda.jython.commands.InputCommands import requestInput as raw_input
    #var = raw_input("Please identify the value at which the slits open ")
    gapXOffset = float(raw_input("Please identify the value at which the slits open "))
    print type(gapXOffset)
    print "moving s3gapX to %f" % (gapXOffset+0.1)
    pos s3cenX gapXOffset+0.1

def testingWaitingForSomethingToHappen():
    caput("BL15J-AL-SLITS-03:HM:HMGRP", "All")
    sleep(0.2)
    caput("BL15J-AL-SLITS-03:HM:HOME", 1)
    sleep(0.2)
    i = 0
    print("waiting for something to happen"),
    while caget("BL15J-AL-SLITS-03:HM:HOMING") == "1":
        print("."),
        sleep(1)
        i += 1
        if i > 120:
            raise NameError("Homing timed out") 
    print "homing complete."

def testingReferringToAScannable(slits=s3):
    slitsname = slits.name
    gapX = slits.getGroupMember(slitsname+'gapX')
    print gapX.getPosition()
    

#TESTING SAM.Y SCANNING
try:
    from gdascripts.pd.epics_pds import DisplayEpicsPVClass
    ocam2tot = DisplayEpicsPVClass("ocam2tot", "BL15J-DI-CAM-02:STAT:Total_RBV", "counts", "%.0f")
    ocam2mean = DisplayEpicsPVClass("ocam2mean", "BL15J-DI-CAM-02:STAT:MeanValue_RBV", "counts", "%f")
    ocam2cenX = DisplayEpicsPVClass("ocam2cenX", "BL15J-DI-CAM-02:STAT:CentroidX_RBV", "pixels", "%.0f")
    ocam2cenY = DisplayEpicsPVClass("ocam2cenY", "BL15J-DI-CAM-02:STAT:CentroidY_RBV", "pixels", "%.0f")
    ocam2sigmaX = DisplayEpicsPVClass("ocam2sigmaX", "BL15J-DI-CAM-02:STAT:SigmaX_RBV", "pixels", "%f")
    ocam2sigmaY = DisplayEpicsPVClass("ocam2sigmaY", "BL15J-DI-CAM-02:STAT:SigmaY_RBV", "pixels", "%f")
except:
    localStation_exception(sys.exc_info(), "failed to load all locally-defined epics pvs")

def resetCam(camera="cam1"):
    from time import sleep

    if camera not in [cam1,cam2,bpm1,bpm2]:
        print "Camera (%s) not recognised." % (camera)
        return
    cameraname = camera.name
    
    pvstem = "BL15J-DI-" + cameraname[:3].upper() + "-0" + cameraname[-1] + ":"
    
    if caget(pvstem+"CAM:DetectorState_RBV") == "9":
        i = 0
        print("Reconnecting to camera"),
        while i < 10:
            caput(pvstem+"CAM:RESET.PROC",0)
            print("."),
            sleep(1)
            i += 1
        if caget(pvstem+"CAM:DetectorState_RBV") == "9":
            raise NameError("Cannot connect to camera")

    #Shared settings
    caput(pvstem+"CAM:AcquireTime","0.1")
    caput(pvstem+"CAM:AcquirePeriod","0.25")

    #cam and bpm independent settings
    if cameraname[:3] == "cam":
        caput(pvstem+"CAM:DataType","UInt8")
        caput(pvstem+"CAM:ColorMode","RGB1")
    else:
        caput(pvstem+"CAM:DataType","UInt16")
        caput(pvstem+"CAM:ColorMode","Mono")

    #cam2 specific settings
    if cameraname == "cam2":
        caput("BL15J-DI-CAM-02:ROI:NDArrayPort","JCAM2.cam")
        caput("BL15J-DI-CAM-02:ROI:ReverseX","Yes")
        caput("BL15J-DI-CAM-02:ROI:ReverseY","Yes")
        #Set tabs to look at the roi
        caput("BL15J-DI-CAM-02:OVER:NDArrayPort","JCAM2.roi")
        caput("BL15J-DI-CAM-02:TIFF:NDArrayPort","JCAM2.roi")
        caput("BL15J-DI-CAM-02:HDF5:NDArrayPort","JCAM2.roi")
        caput("BL15J-DI-CAM-02:MJPG:NDArrayPort","JCAM2.over")

    #HDF5 file writing settings
    caput(pvstem+"HDF5:NumRowChunks","964")
    caput(pvstem+"HDF5:NumColChunks","1292")
    caput(pvstem+"HDF5:NumFramesChunks","1")
    caput(pvstem+"HDF5:Compression","2") #szip compression

    print "%s reset complete" % (cameraname)




from gdascripts.scannable.detector.DetectorDataProcessor import DetectorDataProcessorWithRoi
from gdascripts.analysis.datasetprocessor.twod.SumMaxPositionAndValue import SumMaxPositionAndValue

# roi1 = DetectorDataProcessorWithRoi('roi1', bpm2pdw, SumMaxPositionAndValue())

# roi1.setRoi(642,1,646,964)



print "** The script has loaded successfully **"