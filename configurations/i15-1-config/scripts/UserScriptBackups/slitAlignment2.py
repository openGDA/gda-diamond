import scisoftpy as dnp

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
           "cYh":7.97307,"cYl":-0.08449,
           }
    s5l = {"gXh":9.33824,"gXl":-0.10904,
           "cXh":0.11732,"cXl":-6.95832,
           "gYh":9.15625,"gYl":-0.10915,
           "cYh":7.28876,"cYl":-0.15361,
           }
    l = {"s3":s3l,"s4":s4l,"s5":s5l}
    return l[sn]

def initialiseSlits(slits=s3):
    """ initialise the selected slits.
    
    Initialise the selected slits. In this case the term initialisation 
    refers to homing, and resetting the limits ready for coarse and fine alignment.
    
    Originally this was built in to coarse alignment, now it's here. 
    """
    from time import sleep, clock
    from gda.jython.commands.InputCommands import requestInput as raw_input
    
    # check real slits have been entered
    if slits not in [s3,s4,s5]:
        print "Those slits (%s) not recognised." % (slits)
        return
    
    #define the slit name
    sn = slits.name
    
    #define the four scannables.
    gapX = slits.getGroupMember(sn+'gapX')
    cenX = slits.getGroupMember(sn+'cenX')
    gapY = slits.getGroupMember(sn+'gapY')
    cenY = slits.getGroupMember(sn+'cenY')
    
    # define the distance to the hard limit to aim for
    limit_offset = 0.05
    print ""
    print " WARNING! This function will reset all limits and user offsets for slits "+slits.name+"!"
    print " The current values are: "
    print "*****************************************************"
    print "            Slit group %s current offsets:" % sn
    print "*****************************************************"
    print "    gapX    |    cenX    ||    gapY    |    cenY    |"
    print " %10.6f   %10.6f   %10.6f   %10.6f" % (gapX.userOffset,cenX.userOffset,gapY.userOffset,cenY.userOffset)
    print "*****************************************************"
    
    yes = raw_input("Are you sure you want to continue?")
    if yes not in ("y","Y","yes","Yes","YES","yep","of course"):
        print "ok, stopping as per your request."
        return
    
    # define the pvstem. 
    pvstem = "BL15J-AL-SLITS-0" + sn[-1] + ":"
    
    # Remove the user offsets
    print "Removing EPICS User offsets..."
    for motor in slits.getGroupMembers():
        motor.getMotor().setUserOffset(0)
    
    # home the motors
    caput(pvstem+"HM:HMGRP", "All")
    sleep(0.2)
    caput(pvstem+"HM:HOME", 1)
    sleep(0.2)
    t0 = clock()
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
    if clock()-t0 < 0.5:
        print "That was very quick, are you sure the motor is in an on?"
        print "initialisation aborted"
        return
    else:
        print "Homing complete."
    print ""
    print "Resetting the limits..."
    
    # get the limit values from the dictionary
    l = defineSlitLimits(sn)
    
    # iterate over the motors and set the limits. 
    for motor in slits.getGroupMembers(): 
        # the key is needed to get the values from the dict. 
        key = str(motor.name[2]+motor.name[5])
        
        if motor.name[2:5]=="cen":
            caput(pvstem+motor.name[-1]+":"+"CENTER.LLM",l[key+'l'])
            caput(pvstem+motor.name[-1]+":"+"CENTER.HLM",l[key+'h'])
        elif motor.name[2:5]=="gap":
            caput(pvstem+motor.name[-1]+":"+"SIZE.LLM",l[key+'l'])
            caput(pvstem+motor.name[-1]+":"+"SIZE.HLM",l[key+'h'])
        else:
            raise NameError('error determining nature of motor %s.',motor)
    print "Initialisation Complete."

def coarseSlitAlignment(slits=s3, alignX=True, alignY=True, automatic=True, XScanSlitWidth = 0.5, YScanSlitWidth = 0.2):
    """ aligns the requested slits from scratch. Assumes they have been initialised (i.e. homed, epics limits in place.)
    """
    from gda.jython.commands.InputCommands import requestInput as raw_input
    
    # how long to wait for?
    forever = 15
    # check real slits have been entered
    if slits not in [s3,s4,s5]:
        print "Those slits (%s) not recognised." % (slits)
        return
    
    old_processors = scan_processor.processors
    scan_processor.processors = [GaussianPeakAndBackgroundP(), Discontinuity()]
    
    # define the distance to the soft limit to aim for
    limit_offset = 0.05
    
    #define the four scannables.
    gapX = slits.getGroupMember(slits.name+'gapX')
    cenX = slits.getGroupMember(slits.name+'cenX')
    gapY = slits.getGroupMember(slits.name+'gapY')
    cenY = slits.getGroupMember(slits.name+'cenY')
    
    # check all the offsets are zero (not strictly necessary, but best to make sure.)
    for motor in slits.getGroupMembers():
        motor.getMotor().setUserOffset(0.0)
    
    # open all the the slits
    fullyOpenSlits(s3)
    fullyOpenSlits(s4)
    fullyOpenSlits(s5)
    
    if alignX:
        # do the scan
        print ""
        print "coarsely locating the x-closed position, starting scan..."
        scan gapX gapX.lowerMotorLimit+limit_offset (gapX.upperMotorLimit+gapX.lowerMotorLimit)/2 0.3 w forever d2
        print "I have identified %f as the point at which the slits open" % (disc.result.disc)
        if automatic:
            gapXValue = disc.result.disc
        else:
            gapXValue = float(raw_input("What do you think? (please enter a value)")) 
        print "Opening the gapX to XScanSlitWidth."
        
        # set the offset
#         gapX.getMotor().setUserOffset(gapXValue)
        setMotorPositionAs(gapX,0,gapXValue)
        
        # move the motor
        pos gapX XScanSlitWidth
        
        print "the slits are now open to the tune of %f" % (gapX.getActualPosition())
        # do the scan
        print "trying to find the x-centre, starting scan..."
        scan cenX cenX.lowerMotorLimit+limit_offset cenX.upperMotorLimit-limit_offset 0.3 w forever d2
        print "I have identified %f as the centre of the slits" % (peak.result.pos)
        if automatic:
            cenXValue = peak.result.pos
        else:
            cenXValue = float(raw_input("What do you think? (please enter a value)")) 
        print "Moving the slits to the centre..."
        
        # set the offset
#         cenX.getMotor().setUserOffset(cenXValue)
        setMotorPositionAs(cenX,0,cenXValue)
        # move the motor
        pos cenX 0 gapX 8
        
    if alignY:
        # do the scan
        print ""
        print "coarsely locating the y-closed position, starting scan..."
        scan gapY gapY.lowerMotorLimit+limit_offset (gapY.upperMotorLimit+gapY.lowerMotorLimit)/2 0.3 w forever d2
        print "I have identified %f as the point at which the slits open" % (disc.result.disc)
        if automatic:
            gapYValue = disc.result.disc
        else:
            gapYValue = float(raw_input("What do you think? (please enter a value)")) 
        print "Opening the gapY to YScanSlitWidth"
        
        # set the offset
#         gapY.getMotor().setUserOffset(gapYValue)
        setMotorPositionAs(gapY,0,gapYValue)
        # move the motor
        pos gapY YScanSlitWidth
        
        print "the slits are now open to the tune of %f" % (gapY.getActualPosition())
        
        # do the scan
        print "trying to find the y-centre, starting scan..."
        scan cenY cenY.lowerMotorLimit+limit_offset cenY.upperMotorLimit-limit_offset 0.3 w forever d2
        print "I have identified %f as the centre of the slits" % (peak.result.pos)
        if automatic:
            cenYValue = peak.result.pos
        else:
            cenYValue = float(raw_input("What do you think? (please enter a value)")) 
        print "Moving the slits to the centre..."
        
        # set the offset
#         cenY.getMotor().setUserOffset(cenYValue)
        setMotorPositionAs(cenY,0,cenYValue)
        # move the motors
        pos cenY 0 gapY 8
        
    print ""
    print "*****************************************************"
    print "           Slit group %s coarsely aligned." % slits.name
    print "*****************************************************"
    print "    gapX    |    cenX    ||    gapY    |    cenY    |"
    print " %10.6f   %10.6f   %10.6f   %10.6f" % (gapXValue,cenXValue,gapYValue,cenYValue)
    print "*****************************************************"
    scan_processor.processors = old_processors
        
def fineSlitAlignment(slits=s3, alignX=True, alignY=True, automatic=True, XScanSlitWidth = 0.25, YScanSlitWidth = 0.25, override=False):
    """Fine alignment of the slits s3, s4, s5. 
    
    Perform a fine alignment of the slits. 
    Designed to work immediately after coarseAlignSlits, but can be run at any point to tweak the offsets.  
    
    """
    from gda.jython.commands.InputCommands import requestInput as raw_input
    # define the wait time
    forever = 15
    
    # check real slits have been entered
    if slits not in [s3,s4,s5]:
        print "Those slits (%s) not recognised." % (slits)
        return
    
    old_processors = scan_processor.processors
    scan_processor.processors = [GaussianPeakAndBackgroundP(), GaussianDiscontinuityP() ]
    
    # define the distance to the soft limit to aim for
    limit_offset = 0.05
    
    #define the four scannables.
    gapX = slits.getGroupMember(slits.name+'gapX')
    cenX = slits.getGroupMember(slits.name+'cenX')
    gapY = slits.getGroupMember(slits.name+'gapY')
    cenY = slits.getGroupMember(slits.name+'cenY')
    
    # check all the offsets are not zero
    if not override:
        for motor in slits.getGroupMembers():
            if motor.getMotor().getUserOffset() == 0:
                print "motor %s has zero offset. Have you run a coarse alignment?" % (motor.name)
                print "rerun with override=True to override this message. "
                return
    
    # open the other slits
    for s in [s3,s4,s5]:
        if s != slits:
            fullyOpenSlits(s)
            
    # now position the slits we're interested in.
    # first scan is an x-scan so want small gapX and large gapY.  
    if alignX:
        print ""
        print "Configuring slits for x-gap scan..."
        pos cenX 0 cenY 0 gapX XScanSlitWidth gapY 8
        lv = max(-0.5, gapX.lowerMotorLimit+limit_offset)
        print "Locating the x-closed position, starting scan..."
        scan gapX lv .5 .05 w forever d2
        print "I have identified %f as the point at which the slits open" % (discontinuity.result.pos)
        if automatic:
            gapXValue = discontinuity.result.pos
        else:
            gapXValue = float(raw_input("What do you think? (please enter a value)")) 
        print "Opening the gapX to XScanSlitWidth."
        
        # set the offset based on wanting the gapXValue to be zero. 
        setMotorPositionAs(gapX,0,gapXValue)
        
        # move the motor
        pos gapX XScanSlitWidth
        
        # do the scan
        print "trying to find the x-centre, starting scan..."
        scan cenX -2 2 .2 w forever d2
        print "I have identified %f as the centre of the slits" % (peak.result.pos)
        if automatic:
            cenXValue = peak.result.pos
        else:
            cenXValue = float(raw_input("What do you think? (please enter a value)")) 
        print "Moving the slits to the centre..."
        
        # set the offset based on wanting cenXValue to be 0. 
        setMotorPositionAs(cenX,0,cenXValue)
        
        # move the motor
        pos cenX 0 gapX 8
        
    if alignY:
        print ""
        print "Configuring slits for y-gap scan..."
        pos cenX 0 cenY 0 gapX 8 gapY YScanSlitWidth
        lv = max(-.5, gapY.lowerMotorLimit+limit_offset)
        print "Locating the y-closed position, starting scan..."
        scan gapY lv .5 .05 w forever d2
        print "I have identified %f as the point at which the slits open" % (discontinuity.result.pos)
        if automatic:
            gapYValue = discontinuity.result.pos
        else:
            gapYValue = float(raw_input("What do you think? (please enter a value)")) 
        print "Opening the gapY to YScanSlitWidth."
        
        # set the offset based on wanting the gapYValue to be zero. 
        setMotorPositionAs(gapY,0,gapYValue)
        
        # move the motor
        pos gapY YScanSlitWidth
        
        # do the scan
        print "trying to find the x-centre, starting scan..."
        scan cenY -2 2 0.2 w forever d2
        print "I have identified %f as the centre of the slits" % (peak.result.pos)
        if automatic:
            cenYValue = peak.result.pos
        else:
            cenYValue = float(raw_input("What do you think? (please enter a value)")) 
        print "Moving the slits to the centre..."
        
        # set the offset based on wanting cenYValue to be 0. 
        setMotorPositionAs(cenY,0,cenYValue)
        
        # move the motor
        pos cenY 0 gapY 8
        
    print ""
    print "*****************************************************"
    print "          Slit group %s fine alignment moves" % slits.name
    print "*****************************************************"
    print "    gapX    |    cenX    ||    gapY    |    cenY    |"
    print " %10.6f   %10.6f   %10.6f   %10.6f" % (gapXValue,cenXValue,gapYValue,cenYValue)
    print "*****************************************************"
    scan_processor.processors = old_processors
    
def fineAlignSlit():
    """ DEPRECATED
    aligns the requested slits. For the moment only does s4. 
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

def fullyOpenSlits(slits):
    """ fully opens and centres the slits, based only on the limit values. 
    """
    
    # set the gao between the limit and the set point.
    limit_offset = 0.1
    
    # get string equivalent of scannable group
    sn = slits.name
    
    #define the four scannables.
    gapX = slits.getGroupMember(sn+'gapX')
    cenX = slits.getGroupMember(sn+'cenX')
    gapY = slits.getGroupMember(sn+'gapY')
    cenY = slits.getGroupMember(sn+'cenY')
    
    if [gapX.getUserOffset(),cenX.getUserOffset(),gapY.getUserOffset(),cenY.getUserOffset()].count(0) == 0:
        # calculate the values
        cX = (cenX.lowerMotorLimit + cenX.upperMotorLimit)/2
        gX = gapX.upperMotorLimit - limit_offset
        cY = (cenY.lowerMotorLimit + cenY.upperMotorLimit)/2
        gY = gapY.upperMotorLimit - limit_offset
        print "Opening slits %s..." % sn
        pos cenX cX gapX gX cenY cY gapY gY
    else:
        # assume all the offsets are applied and the motor is good. 
        print "Opening slits %s..." % sn
        pos cenX 0 gapX 8 cenY 0 gapY 8
    
    print "Slits %s fully opened." % sn

def limitScan(motor,points,*args):
    "scans a motor from it's low limit to its high limit."
    "currently doesn't work"
    start = motor.lowerMotorLimit+0.05
    stop = motor.upperMotorLimit-0.05
    step = (stop-start)/points
    print start
    print stop
    print step
    print list(args)
    keyscan(motor,start,stop,step,list(args))
    #keyscan(motor,start,stop,step)
#     dscan motor start stop points args 

def setMotorPositionAs(motor,new_position,current_position=True):
    """ Sets the offset based on current values. 
    Calculates and sets the offset required to make the current_position
    actually equate to the new_position. It doesn't actually move anything. 
    If current_position is True, then it takes the retireives the current position. 
    If it's a number, it works on that instead.
    
    Here are some examples: 
    
    The offset is currently 2. I am at 3 in user units. I want to make this zero. 
    new offset = 2+3=5. I calculate and apply this by setting setMotorPositionAs(motor,0)
    
    I have observed that, in the currently offset units, I want to make 0.154 equal to 0.
    I am at a position of 5. setMotorPositionAs(motor,0,0.154) moves the offset the correct 
    amount so that I am now at 4.846.
    
    """
    from time import sleep
    # get current offset
    gco = motor.getMotor().getUserOffset()
    
    if type(current_position) == bool:
        current_position  = motor.getPosition()

    # set the new offset
    motor.getMotor().setUserOffset(new_position+gco-current_position)
    sleep(0.2) # this is to make sure the change is read back before the next step. 
    
def keyscan(*args):
    """passes the arguments to the scan command"""
    scan args

def fromStartToFinish(slits):
    initialiseSlits(slits)
    coarseSlitAlignment(slits)
    fineSlitAlignment(slits)
    print ""
    print "DONE!!!!!"
    print ""
    
    
    
    
    
def getTheOffsets(list_of_motorgroups):
    for motorgroup in list_of_motorgroups:
        for motor in motorgroup.getGroupMembers():
            print "The current offset on motor %s is % 3.5f." % (motor.name, motor.getUserOffset())

print "** The script has loaded successfully **"