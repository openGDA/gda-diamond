from time import sleep

#Y, Bragg, Roll, Yaw, Bend

##OLD POSITIONS BEFORE CAGE MODIFICATIONS
#xtalPosns = {"311":          [  0.600,10.480954,-6.98427,0.0,1.0], #pitch actuated, updated 17/09/2016 twice
#             "311openloop":          [  0.600,10.480954,-23.4,18.0550,1.0], #pitch actuated, updated 17/09/2016 twice
#             #"220unactuated":[-49.000, 8.56136,-1.14,0.0,0.6], #Old
#             #"311unactuated":[  0.600, 8.19121,-7.89,0.0,0.6], #Old
#             #"111unactuated":[ 50.048, 5.80468,-7.80,0.0,0.6], #Old
#             "220":          [-49.000, 9.556076,-0.24,0.0,1.0], #pitch actuated, updated 17/09/2016
#             "111":          [ 50.048,10.371206,-6.9216,0.0,1.0], #pitch actuated, updated 17/09/2016 twice
#             "111openLoop":  [ 50.048,10.371206,-22.8223,18.0550,1.0]} #temp while yaw and roll are in open loop 

xtalPosns = {"311":      [  0.600, 8.1762,-6.341,0.0,1.7199], #TEMP due to problem with Roll encoder 19/01/2017
             #"311":      [  0.600, 8.1762,-6.011,0.0,1.7199], #FINAL 16/12/2016
             "311unbent":[  0.600, 5.6720,-6.011,0.0,1.5],    #FINAL 16/12/2016
             "220":      [-49.000, 6.7675,-5.292,0.0,1.6294], #FINAL 16/12/2016
             "220unbent":[-49.000, 5.5223,-5.292,0.0,1.5],    #FINAL 16/12/2016
             "111":      [ 50.048, 8.7988,-5.786,0.0,1.7938], #FINAL 16/12/2016
             "111unbent":[ 50.048, 5.5054,-5.786,0.0,1.5]}    #FINAL 16/12/2016

#PV for X position, Z distance from BLM in m
xtalAlignPVs = {"bpm1": ["BL15J-DI-BPM-01:PY:Double1_RBV",3.754],
                "bpm2": ["BL15J-DI-BPM-02:PY:Double1_RBV",7.560],
                "eye":  ["BL15J-DI-EYE-01:PY:Double1_RBV",8.960]}

def xtalSelect(xtal):
    xtalBendOut = 1.5 #Retract position for the bender
    try:
        print "Selecting xtal %s" %xtal
        print "   Y: "+str(xtalPosns[xtal][0])+", Bragg: "+str(xtalPosns[xtal][1])+", Roll: "+str(xtalPosns[xtal][2])+", Yaw: "+str(xtalPosns[xtal][3])+", Bend: "+str(xtalPosns[xtal][4])
    except:
        raise NameError("xtal "+str(xtal)+" not recognised! Only "+str(xtalPosns.keys())+" available")
        return
    s1close
    print "   Retracting bender..."
    pos xtalBend xtalBendOut
    if inPosition(xtalBend,xtalBendOut,.01) == True:
        print "      Bender retracted to %s mm" %xtalBend.getPosition()
    print "   Moving xtalY to %s mm and pre-positioning Bragg, Roll, Yaw..." %xtalPosns[xtal][0]
    pos xtalY xtalPosns[xtal][0] xtalBragg xtalPosns[xtal][1] xtalRoll xtalPosns[xtal][2] xtalYaw xtalPosns[xtal][3]
    if inPosition(xtalY,xtalPosns[xtal][0],.05) == True:
        print "      xtalY moved to %s mm" %xtalY.getPosition()
    print "   Moving Bragg, Roll and Yaw..."
    pos xtalBragg xtalPosns[xtal][1] xtalRoll xtalPosns[xtal][2] xtalYaw xtalPosns[xtal][3]
    print "      Move complete. Bragg: %s mrad, Roll: %s mrad, Yaw: %s mad" % (xtalBragg.getPosition(),xtalRoll.getPosition(),xtalYaw.getPosition())
    if xtalPosns[xtal][4] > xtalBendOut:
        print "   Engaging Bender..."
        pos xtalBend xtalPosns[xtal][4]
        print "      Bender moved to %s mm" %xtalBend.getPosition()
    print "xtalSelect complete! xtal %s has been selected. You may now open s1." %xtal

def xtalAlign(device,verbose=True):
    #Requires all BPMs to be in and working
    if device == "bpm1":
        bpm1In
        if checkCam(device) != True:
            print "bpm1 needs to be ready for xtalAlign."
            return
    if device == "bpm2":
        bpm2In
        if checkCam(device) != True:
            print "bpm2 needs to be ready for xtalAlign."
            return
    if caget(camPVs[device]+"PY:EnableCallbacks") == "0":
        revert = True
        camPyOn(device)
        sleep(camGetAcquireTime(device))
    else:
        revert = False
    xPos = float(caget(xtalAlignPVs[device][0])) #in mm
    changeBragg = 0.5 * (xPos / xtalAlignPVs[device][1]) 
    if verbose == True:
        print str(device)+": Beam seen at x = %s mm. Moving xtalBragg by %s mrad" % (xPos, changeBragg)
    inc xtalBragg changeBragg
    if revert == True:
        camPyOff(device)

def xtalResetLimits():
    pvstem = "BL15J-OP-LAUE-01:"
    caput(pvstem+"ROLL.HLM","10.1")
    caput(pvstem+"ROLL.LLM","-10.1")
    caput(pvstem+"YAW.HLM","35.1")
    caput(pvstem+"YAW.LLM","-35.1")
    caput(pvstem+"PITCH.HLM","24.7")  # Actual =  24.764185 mrad on 04/01/2017
    caput(pvstem+"PITCH.LLM","-21.9") # Actual = -21.969596 mrad on 04/01/2017
    caput(pvstem+"Y.HLM","50.1")
    caput(pvstem+"Y.LLM","-49.1")
    caput(pvstem+"BENDER.HLM","1.85") #Safe limit, 04/01/2017
    caput(pvstem+"BENDER.LLM","-0.5")


def quickTest():
    print "      Move complete. Bragg: %s mrad, Roll: %s mrad, Yaw: %s mad" % (xtalBragg.getPosition(),xtalRoll.getPosition(),xtalYaw.getPosition())

print "xtal scripts loaded"