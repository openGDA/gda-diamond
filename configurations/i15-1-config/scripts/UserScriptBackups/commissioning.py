from time import sleep
import time
import math

pneumaticPVs = {"bpm1":"BL15J-DI-BPM-01:",
                "bpm2":"BL15J-DI-BPM-02:",
                "d1":"BL15J-DI-PHDGN-01:",
                "d2":"BL15J-DI-PHDGN-02:"}

feedbackXPVs =  {"bpm1":"BL15J-DI-BPM-01:PY:Double1_RBV",
                 "bpm2":"BL15J-DI-BPM-02:PY:Double1_RBV",
                 "eye":"BL15J-DI-EYE-01:PY:Double1_RBV",
                 "bpm3":"BL15J-EA-CALC-01.G"}

feedbackIPVs =  {"bpm1":"BL15J-DI-EYE-01:STAT:MeanValue_RBV",
                 "bpm2":"BL15J-DI-BPM-02:STAT:MeanValue_RBV",
                 "eye":"BL15J-DI-EYE-01:STAT:MeanValue_RBV",
                 "bpm3":"BL15J-EA-CALC-01.I"}

deviceZ = {"blm":26640,
           "bpm1":30394,
           "bpm2":34200,
           "eye":35600,
           "bpm3":35500}


def alignXtal(verbose=True):
    #Requires all BPMs to be in and working
    bpm1In
    bpm2In
    if checkCam("bpm1") != True or checkCam("bpm2") != True:
        print "bpm1 and bpm2 need to be ready for alignXtal."
        return
    xPos = float(caget("BL15J-DI-BPM-01:PY:Double1_RBV")) #in mm
    changeBragg = 0.5 * (xPos / 3.754) #xtal to bpm1 distance = 3.754 m
    if verbose == True:
        print "bpm1: Beam seen at x = %s mm. Moving xtalBragg by %s mrad" % (xPos, changeBragg)
    inc xtalBragg changeBragg
    
    ##Stopping the BPM2 alignment as it just seems to throw it off
    #sleep(2)
    #
    #xPos = float(caget("BL15J-DI-BPM-02:PY:Double1_RBV")) #in mm
    #changeBragg = 0.5 * (xPos / 7.560) #xtal to bpm2 distance = 7.560 m
    #if verbose == True:
    #    print "bpm2: Beam seen at x = %s mm. Moving xtalBragg by %s mrad" % (xPos, changeBragg)
    #inc xtalBragg changeBragg
    
    sleep(2)
    
    checkCam("eye")
    xPos = float(caget("BL15J-DI-EYE-01:PY:Double1_RBV")) #in mm
    changeBragg = 0.5 * (xPos / 8.960) #xtal to sam distance = 8.960 m
    if verbose == True:
        print "eye: Beam seen at x = %s mm. Moving xtalBragg by %s mrad" % (xPos, changeBragg)
    inc xtalBragg changeBragg

def xtalStabilise(device,refreshTime=0.25,minI=200.):
    """Test script to see how the fine pitch can be used to stabilise the beam position.
    
    See Beam stability feedback Confluence page."""
    doFeedback = True
    feedbackStable = True
    print str(time.asctime()) + ": Feedback started."
    for i in range (0,1000):
    #while True:
        xObs = float(caget(feedbackXPVs[device]))
        currentPos = float(caget("BL15J-OP-LAUE-01:PITCH:FINE:MOV:RD"))
        xCor = (35500.*xObs)/(deviceZ[device]-deviceZ["blm"])
        newPos = currentPos + xCor
        if float(caget(feedbackIPVs[device])) < minI:
            if doFeedback == True:
                print str(time.asctime()) + ": Intensity dropped below minI. Feedback paused."
            doFeedback = False
        else:
            if doFeedback == False:
                print str(time.asctime()) + ": Feedback resumed."
            doFeedback = True
            if newPos < 15 and newPos > 0 and xCor < 1.:
                if feedbackStable == False:
                    print str(time.asctime()) + ": Feedback recovered."
                feedbackStable = True
            else:
                if feedbackStable == True:
                    print str(time.asctime()) + ": Feedback has failed. Re-centering way be required."
                feedbackStable = False
        if doFeedback == True and feedbackStable == True:
            caput("BL15J-OP-LAUE-01:PITCH:FINE:MOV:WR",newPos)
        sleep(refreshTime)

def eh3open():
    caput("BL15J-PS-SHTR-01:CON","Reset") #Close / Open / Reset
    sleep(5)
    caput("BL15J-PS-SHTR-01:CON","Open") #Close / Open / Reset
    waitFor("BL15J-PS-SHTR-01:STA",1,timeOut=60)
    print "EH3 shutter now open"
alias eh3open

def eh3close():
    caput("BL15J-PS-SHTR-01:CON","Close") #Close / Open / Reset
    waitFor("BL15J-PS-SHTR-01:STA",3,timeOut=60)
    print "EH3 shutter now closed"
alias eh3close

def pneumaticMove(device,moveIn=True):
    ###IN PROGRESS!!!!!!!!!!!!!!
    """Checks whether a pneumatic is currently in position, and if not tries to move it.
    
    A val of 1 corresponds to Open (out of beam), 3 to Closed (in beam). 
    Returns True if the pneumatic is already in position, and False if not."""
    if moveIn == True:
        sta = 3
        con = 1
    else:
        sta = 1
        con = 0
    if device not in pneumaticPVs.keys():
        print "Device %s not recognised." % device
        return False
    
    if caget(pneumaticPVs[device]+"STA") != sta:
        caput(pneumaticPVs[device]+"CON",con)
        try:
            waitFor(pneumaticPVs[device]+"STA",sta)
        except NameError:
            #Try a reset
            caput(pneumaticPVs[device]+"CON","2") #RESET
            waitFor(pneumaticPVs[device]+"CON","2")
            caput(pneumaticPVs[device]+"CON",con)
            waitFor(pneumaticPVs[device]+"STA",sta)
            return True
        return True
    else:
        return True

def d2in():
    pneumaticMove("d2",True)
alias d2in

def d2out():
    pneumaticMove("d2",False)
alias d2out

def d1in():
    pneumaticMove("d1",True)
alias d1in

def d1out():
    pneumaticMove("d1",False)
alias d1out

def waitFor(pv,value,checkTime=0.5,timeOut=30):
    i = 0
    timeOut = int(float(timeOut) / float(checkTime))
    sleep(float(checkTime))
    while str(caget(pv)) != str(value):
        sleep(float(checkTime))
        i += 1
        if i > timeOut:
            raise NameError("waitFor timed out while waiting for "+ str(pv) + " to change to " + str(value)) 

def waitForTol(pv,value,tol=1,checkTime=0.5,timeOut=30):
    i = 0
    timeOut = int(float(timeOut) / float(checkTime))
    sleep(float(checkTime))
    while float(caget(pv)) < value+tol and  float(caget(pv)) > value-tol:
        sleep(float(checkTime))
        i += 1
        if i > timeOut:
            raise NameError("waitFor timed out while waiting for "+ str(pv) + " to change to " + str(value)) 

def caputS(pv,string):
    ustring = map(ord,string+u"\u0000")
    caput(pv,ustring)

def inPosition(motor,setPosn,tolerance="",toleranceMultiplier=1.):
    """Returns true if a motor is at the setPosn, within the tolerance given.
    
    If no tolerance value is given, the getDemandPositionTolerance is used.
    A toleranceMultiplier can be used to increase the getDemandPositionTolerance."""
    if tolerance == "":
        tolerance = motor.getDemandPositionTolerance()*toleranceMultiplier
    if abs(motor.getPosition()-setPosn) < (tolerance):
        return True
    else:
        raise NameError("Scannable "+str(motor.name)+" has not reached its set position. Current "+str(motor.getPosition())+", Set: "+str(setPosn)+" +/- "+str(tolerance))
        #raise NameError("Scannable error")
        return False

def patienceIsAVirtue():
    print "sleeping"
    sleep(1200)
    spinOn
    eh3open
    peCollectData(600,'0204_CFSPOx_60x10s')
    spinOff
    print "done. Enjoy Rick."

def overnightMOFFun():
    f2Set('1%')
    i = 20
    sleep(60*5)
    samples = (('EmptyXPDF',19),('empty2p5QGC',91.25),('ZIF-8',74.3),('MAF-6',52.8),('Nickel',33.916))
    for filename, samXposn in samples:
        pos samX samXposn
        sleep(1)
        ############### DO THE DARK ##############
        eh3close
        dark_string =  "_d0"+str(i)+"_dark_300s"
        print dark_string
        detCollectDark(dark_string,300)
        ############### DO THE DATA COLLECTION ##############
        eh3open
        if filename == "MAF-6":
            pos samY -82
        else:
            pos samY -85
        fn_string =  "_0"+str(i)+"_"+filename+"_1pcf2_300s"
        print fn_string
        detCollectSample(fn_string,300)
        eh3close
        ################## WAIT FOR IT ########################
        sleep(60*20)
        i += 1
        
    print "All done.... Morning Phil! "


print "Commissioning scripts loaded"