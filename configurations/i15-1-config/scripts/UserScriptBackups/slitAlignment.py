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
def defineSlitLimits(sn):
    """Collect the current s3/4/5 dial limits. 
    
    sn: (string) slit name. one of: s3
                                    s4
                                    s5.
                                    
    """
    s3l = {"gXh":10.0871,"gXl":-0.01170,
           "cXh":0.10866,"cXl":-7.68220,
           "gYh":9.44013,"gYl":-0.10634,
           "cYh":8.25850,"cYl":-0.10066,
           }
    s4l = {"gXh":8.98796,"gXl":-0.10734,
           "cXh":0.09437,"cXl":-7.29861,
           "gYh":9.40104,"gYl":-0.09504,
           "cYh":7.06857,"cYl":-0.10362,
           }
    s5l = {"gXh":9.33824,"gXl":-0.10904,
           "cXh":0.11732,"cXl":-6.95832,
           "gYh":9.15625,"gYl":-0.10915,
           "cYh":7.28876,"cYl":-0.15361,
           }
    l = {"s3":s3l,"s4":s4l,"s5":s5l}
    return l[sn]
    
def fullyOpenSlits(slits):
    """ fully opens and centres the slits. 
    """
    # get string equivalent of scannable group
    sn = slits.name
    
    # get the limits
    l = defineSlitLimits(sn)
    
    #define the pvstem
    pvstem = "BL15J-AL-SLITS-0" + sn[-1] + ":"
    
    #define the four scannables.
    gapX = slits.getGroupMember(sn+'gapX')
    cenX = slits.getGroupMember(sn+'cenX')
    gapY = slits.getGroupMember(sn+'gapY')
    cenY = slits.getGroupMember(sn+'cenY')
    
    # get the four offsets
    gapXoff = float(caget(pvstem+"X:SIZE.OFF"))
    cenXoff = float(caget(pvstem+"X:CENTER.OFF"))
    gapYoff = float(caget(pvstem+"Y:SIZE.OFF"))
    cenYoff = float(caget(pvstem+"Y:CENTER.OFF"))
    
    # open the slits
    print "Opening slits %s..." % sn
    cX = (cenXoff+(l["cXh"]+l["cXl"])/2)
    gX = l["gXh"]-0.5+gapXoff
    cY = (cenYoff+(l["cYh"]+l["cYl"])/2)
    gY = l["gYh"]-0.5+gapYoff

    pos cenX cX gapX gX cenY cY gapY gY
    
    print "Slits %s fully opened." % sn
    
def keyscan(*args):
    """passes the arguments to the scan command"""
    scan args

def initialiseSlits(slits=s3):
    """ initialise the selected slits.
    
    Initialise the selected slits. In this case the term initialisation 
    refers to homing, and resetting the limits ready for coarse and fine alignment.
    
    Originally this was built in to coarse alignment, now it's here. 
    """
    from time import sleep
    from gda.jython.commands.InputCommands import requestInput as raw_input
    
    #define the four scannables.
    gapX = slits.getGroupMember(sn+'gapX')
    cenX = slits.getGroupMember(sn+'cenX')
    gapY = slits.getGroupMember(sn+'gapY')
    cenY = slits.getGroupMember(sn+'cenY')
    
    # define the distance to the hard limit to aim for
    limit_offset = 0.05
    
    #define the slit name
    sn = slits.name
    
    print "WARNING! This function will reset all limits and user offsets for slits "+slits.name+"!"
    print "the current values are: "
    print "*****************************************************"
    print "  Slit group %s current offsets:" % sn
    print "*****************************************************"
    print "    gapX    |    cenX    ||    gapY    |    cenY    |"
    print " %10.6f   %10.6f   %10.6f   %10.6f" % (gapX.userOffset,cenX.userOffset,gapY.userOffset,cenY.userOffset)
    print "*****************************************************"
    
    yes = raw_input("Are you sure you want to continue?")
    if yes not in ("y","Y","yes","Yes","YES","yep","of course"):
        return
    
    # define the pvstem - it's needed for the homing. 
    pvstem = "BL15J-AL-SLITS-0" + sn[-1] + ":"
    
    # Remove the user offsets
    print "Removing EPICS User offsets"
    
    # replace all these with motor.getMotor().setUserOffset(0.0)
    for motor in slits.getGroupMembers():
        motor.getMotor().setUserOffset(0)
    
    # home the motors
    caput(pvstem+"HM:HMGRP", "All")
    sleep(0.2)
    caput(pvstem+"HM:HOME", 1)
    sleep(0.2)
    i = 0
    print("waiting for the motors to home"),
    while caget(pvstem+"HM:HOMING") == "1":
        print("."),
        sleep(1)
        i += 1
        if i % 20 < 0.1:
            print " "
            print "                              ",
        if i > 120:
            raise NameError("Homing timed out") 
    print "Homing complete."
    print ""
    print "Resetting the limits."
    l = defineSlitLimits(slits)
    
    

def coarseAlignThoseSlits(slits=s3, XScanSlitWidth = 0.5, YScanSlitWidth = 0.2):
    """ aligns the requested slits from scratch. starts with homing. 
    """
    from gda.jython.commands.InputCommands import requestInput as raw_input # needed in absence of peak finding
    from time import sleep
    
    # define the distance to the hard limit to aim for
    limit_offset = 0.05
    
    #define the slit name
    sn = slits.name
    
    # define the pvstem
    pvstem = "BL15J-AL-SLITS-0" + sn[-1] + ":"
    
    #define the four scannables.
    gapX = slits.getGroupMember(sn+'gapX')
    cenX = slits.getGroupMember(sn+'cenX')
    gapY = slits.getGroupMember(sn+'gapY')
    cenY = slits.getGroupMember(sn+'cenY')
    
    # Check there are no user offsets? 
    # probably need an override or something herE? 
    if [gapX.userOffset,cenX.userOffset,gapY.userOffset,cenY.userOffset].count(0) != 4:
        print "this is better"
    if abs(gapX.userOffset) + abs(cenX.userOffset)  + abs(gapY.userOffset) + abs(cenY.userOffset) > 1e-5:
        raise ValueError('Offsets already exist') 
    
    # Remove the user offsets
    print "Removing EPICS User offsets"
    # replace all these with motor.getMotor().setUserOffset(0.0)
    caput(pvstem+"X:SIZE.OFF", 0)
    caput(pvstem+"Y:SIZE.OFF", 0)
    caput(pvstem+"X:CENTER.OFF", 0)
    caput(pvstem+"Y:CENTER.OFF", 0)
    
    # home the motors
    caput(pvstem+"HM:HMGRP", "All")
    sleep(0.2)
    caput(pvstem+"HM:HOME", 1)
    sleep(0.2)
    i = 0
    print("waiting for the motors to home"),
    while caget(pvstem+"HM:HOMING") == "1":
        print("."),
        sleep(1)
        i += 1
        if i % 20 < 0.1:
            print " "
            print "                              ",
        if i > 120:
            raise NameError("Homing timed out") 
    print "homing complete."

    l = defineSlitLimits(sn)
    print "Opening the slits to initial configuration"
    
    fullyOpenSlits(s3)
    fullyOpenSlits(s4)
    fullyOpenSlits(s5)
    ############## SCANS ############## 
    ################ X ################
    # scan the gap from closed to open
    print "coarsely locating the x-closed position, starting scan..."
    keyscan(gapX, l["gXl"]+limit_offset, l["gXh"]-limit_offset, 0.3, w, 5, d2)
    gapXValue = float(raw_input("Please identify the value at which the slits open "))
    print "Opening the gapX to XScanSlitWidth larger than %.3f (%f mm)" % (gapXValue,gapXValue+XScanSlitWidth)
    pos gapX gapXValue+XScanSlitWidth
    
    # scan the centre across the beam
    print "trying to find the x-centre, starting scan..."
    keyscan(cenX, (l["cXl"]+limit_offset), (l["cXh"]-limit_offset), 0.3,w,5, d2)
    cenXValue = float(raw_input("Please identify the peak location "))
    print "Moving the slits to the centre..."
    #peak.result.pos is the answer. 
    pos cenX cenXValue
    
    # finer scan to find slit opening preciesely
    # (currently just a copy of the above scan!)
    print "final alignment of the x-closed position, starting scan..." 
    pos gapX gapXValue
    keyscan(gapX, (l["gXl"]+limit_offset),gapXValue+1, 0.1,w,9,d2)
    print "You previously entered"+str(gapXValue)
    gapXValue = -float(raw_input("Please identify the value at which the slits open "))
    # set the offset based on this value
    caput(pvstem+"X:SIZE.OFF",gapXValue)
    pos gapX XScanSlitWidth
    
    # scan the centre across the beam
    print "final alignment of the x-centre, starting scan..."
    keyscan(cenX, cenXValue-1, cenXValue+1, 0.1,w,9,d2)
    print "You previously entered "+str(cenXValue)
    cenXValue = -float(raw_input("Please identify the peak location "))
    # set the offset based on this value
    caput(pvstem+"X:CENTER.OFF",cenXValue)
    pos cenX 0
    
    ######################################## Y ##########################################################
    #####################################################################################################
    # scan the gap from closed to open
    print "coarsely locating the y-closed position, starting scan..."
    keyscan(gapY, l["gYl"]+limit_offset, l["gYh"]-limit_offset, 0.3, w, 5, d2)
    gapYValue = float(raw_input("Please identify the value at which the slits open "))
    print "Opening the gapY to YScanSlitWidth larger than %.3f (%f mm)" % (gapYValue,gapYValue+YScanSlitWidth)
    pos gapY gapYValue+YScanSlitWidth
    
    # scan the centre across the beam
    print "trying to find the y-centre, starting scan..."
    keyscan(cenY, (l["cYl"]+limit_offset), (l["cYh"]-limit_offset), 0.3,w,5, d2)
    cenYValue = float(raw_input("Please identify the peak location "))
    print "Moving the slits to the centre..."
    pos cenY cenYValue
    
    # finer scan to find slit opening preciesely
    # (currently just a copy of the above scan!)
    print "final alignment of the y-closed position, starting scan..." 
    pos gapY gapYValue
    keyscan(gapY, (l["gYl"]+limit_offset), gapYValue+1, 0.1,w,9,d2)
    print "You previously entered"+str(gapYValue)
    gapYValue = -float(raw_input("Please identify the value at which the slits open "))
    # set the offset based on this value
    caput(pvstem+"Y:SIZE.OFF",gapYValue)
    pos gapY YScanSlitWidth
    
    # scan the centre across the beam
    print "final alignment of the y-centre, starting scan..."
    keyscan(cenY, cenYValue-1, cenYValue+1, 0.1,w,9,d2)
    print "You previously entered "+str(cenYValue)
    cenYValue = -float(raw_input("Please identify the peak location "))
    # set the offset based on this value
    caput(pvstem+"Y:CENTER.OFF",cenYValue)
    pos cenY 0
    
    print "*****************************************************"
    print "  Slit group %s aligned with the following offsets:" % sn
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
    scan s4gapX (2*XScanSlitWidth) (0) 0.1 dummy1 currentDummy1+20 5 d2
    gapXValue = float(raw_input("Please identify the value at which the slits open "))
    print "Opening the s4gapX to 0.5 mm larger than %f" % gapXValue
    pos s4gapX gapXValue+XScanSlitWidth
    
    # scan the centre across the beam
    print "trying to find the x-centre, starting scan..."
    currentDummy1 = dummy1.getActualPosition()
    scan s4cenX -XScanSlitWidth XScanSlitWidth (XScanSlitWidth/10) dummy1 currentDummy1+20 5 d2
    cenXValue = float(raw_input("Please identify the peak location "))
    print "Moving the slits to the centre..."
    caput("BL15J-AL-SLITS-03:X:CENTER.OFF",cenXValue)
    pos s3cenX 0
    
    # finer scan to find slit opening precisely
    print "relocating the x-closed position, starting scan..." 
    currentDummy1 = dummy1.getActualPosition()
    scan s4gapX (1*XScanSlitWidth) (-XScanSlitWidth) (XScanSlitWidth/10) dummy1 currentDummy1+20 5 d2
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
    
    
def setEpicsLimits():
    #Set the EPICS limits of the slits to values near the limit switch positions
    #These are only the correct value if the calibration offset is zero
    #It was slightly quicker to do this than to go into all of the EPICS windows!!!
    print "*******************************************************"
    print "WARNING: these limits only work if all the calibration "
    print "offsets are set to zero. There is currently no script "
    print "to do this! "
    print "*******************************************************"
    print "Setting EPICS limits"
    offset = 0.01
    caput("BL15J-AL-SLITS-03:X:SIZE.HLM", (10.0871-offset))
    caput("BL15J-AL-SLITS-03:X:SIZE.LLM", (-1.31104+offset))
    caput("BL15J-AL-SLITS-03:Y:SIZE.HLM", (10.0871-offset))
    caput("BL15J-AL-SLITS-03:Y:SIZE.LLM", (-0.10634+offset)) #############
    caput("BL15J-AL-SLITS-03:X:CENTER.HLM", (0.10866-offset)) #############
    caput("BL15J-AL-SLITS-03:X:CENTER.LLM", (-7.6822+offset))
    caput("BL15J-AL-SLITS-03:Y:CENTER.HLM", (8.2584-offset))
    caput("BL15J-AL-SLITS-03:Y:CENTER.LLM", (-0.10066+offset)) #############
    
    caput("BL15J-AL-SLITS-04:X:SIZE.HLM", (8.98796-offset))
    caput("BL15J-AL-SLITS-04:X:SIZE.LLM", (-0.10734+offset)) #############
    caput("BL15J-AL-SLITS-04:Y:SIZE.HLM", (9.40104-offset))
    caput("BL15J-AL-SLITS-04:Y:SIZE.LLM", (-0.09504+offset)) #############
    caput("BL15J-AL-SLITS-04:X:CENTER.HLM", (0.09437-offset)) #############
    caput("BL15J-AL-SLITS-04:X:CENTER.LLM", (-7.29861+offset))
    caput("BL15J-AL-SLITS-04:Y:CENTER.HLM", (7.06857-offset))
    caput("BL15J-AL-SLITS-04:Y:CENTER.LLM", (-0.10362+offset)) #############
    
    caput("BL15J-AL-SLITS-05:X:SIZE.HLM", (9.33824-offset))
    caput("BL15J-AL-SLITS-05:X:SIZE.LLM", (-0.10904+offset)) #############
    caput("BL15J-AL-SLITS-05:Y:SIZE.HLM", (9.15625-offset))
    caput("BL15J-AL-SLITS-05:Y:SIZE.LLM", (-0.10915+offset)) #############
    caput("BL15J-AL-SLITS-05:X:CENTER.HLM", (0.11732-offset)) #############
    caput("BL15J-AL-SLITS-05:X:CENTER.LLM", (-6.95832+offset))
    caput("BL15J-AL-SLITS-05:Y:CENTER.HLM", (7.28876-offset))
    caput("BL15J-AL-SLITS-05:Y:CENTER.LLM", (-0.15361+offset)) #############


print "** The script has loaded successfully **"