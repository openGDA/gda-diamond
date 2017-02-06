from time import sleep

##Old script before the cage was re-built by FMB
#def run_tests():
#    for i in range(1200,1350,10): #range in um
#        bendPos = float(i) / 1000
#        #print bendPos
#        pos xtalBend bendPos
#        alignXtal(False)
#        print str(xtalBend)+" "+str(bpm1statMean)+" "+str(bpm1pySizeX)+" "+str(bpm2pySizeX)+" "+str(bpm2statMean)+" "+str(eyepySizeX)+" "+str(eyestatMean)

##New script for newly re-built cage, 07/12/2016
def runBenderTest():
    #for i in range(1650,1775,5): #range in um, for (111), 07/12/2016
    #for i in range(1575,1700,5): #range in um, for (311), 07/12/2016
    #for i in range(1530,1665,5): #range in um, for (220), 08/12/2016
    #points = range(1570,1725,5) #range in um, for (111), 08/12/2016 PM

    #points = range(1570,1725,5) #range in um, for (311), 09/12/2016 Overnight
    #camSetupStream("eye","311_bendTest_3mmHx2mmV_01",repeats=len(points)) #for (311), 09/12/2016 Overnight
    
    #points = range(1650,1805,5) #range in um, for (111), 10/12/2016 Morning
    #camSetupStream("eye","111_bendTest_3mmHx2mmV_02",repeats=len(points)) #for (111), 10/12/2016 Morning
    
    #points = range(1565,1755,10) #range in um, for (220), 10/12/2016 Overnight
    #camSetupStream("eye","220_bendTest_3mmHx2mmV_03",repeats=len(points)) #for (220), 10/12/2016 Overnight
    
    #points = range(1660,1720,10) #range in um, for (220), 11/12/2016 morning
    #print len(points)
    #camSetupStream("eye","220_bendTest_3mmHx2mmV_03_part2",repeats=len(points)) #for (220), 11/12/2016 morning
    #points = range(1580,1790,10) #range in um, for (220), 11/12/2016 morning, then repeated afternoon
    #camSetupStream("eye","311_bendTest_3mmHx2mmV_04",repeats=len(points)) #for (220), 11/12/2016 morning, then repeated afternoon
    #points = range(1780,1800,10) #range in um, for (220), 12/12/2016 morning
    #camSetupStream("eye","311_bendTest_3mmHx2mmV_04_cont",repeats=len(points)) #for (220), 12/12/2016 morning
    #points = range(1660,1840,10) #range in um, for (111), 12/12/2016 morning
    #points = range(1770,1840,10) #range in um, for (111), 12/12/2016 afternoon, continue
    #camSetupStream("eye","111_bendTest_3mmHx2mmV_05",repeats=len(points)) #for (111), 21/12/2016 morning
    points = range(1810,1840,10) #range in um, for (111), 14/12/2016 afternoon, continue after beam-off
    #camSetupStream("eye","111_bendTest_3mmHx2mmV_05_cont",repeats=len(points)) #for (111), continue after beam-off
    print len(points)
    print points
    bendPos = float(points[0]) / 1000.
    pos xtalBend bendPos
    #xtalAlign("bpm1",False)
    #sleep(2)
    for i in points:
        bendPos = float(i) / 1000.
        pos xtalBend bendPos
        for j in range(0,20): #i.e. wait 20 mins, but re-align after each minute
            camOptimise("eye")
            sleep(2)
            xtalAlign("eye",False)
            sleep(60)
        xtalAlign("eye",False)
        camOptimise("eye")
        sleep(2)
        exposureTime = caget("BL15J-DI-EYE-01:CAM:AcquireTime_RBV")
        print str(xtalBend)+" "+str(xtalBragg)+" "+str(eyepySizeX)+" "+str(eyestatMean)+" "+str(exposureTime)
        camGrabFrameToStream("eye")
    print "runBenderTest complete!"

def runBenderTestdetZ():
    detZpoints = (270,520,770)
    #points = range(1600,1800,10) #range in um, for (311), 14/12/2016
    #camSetupStream("eye","311_bendTestdetZ_3mmHx2mmV_01_cont",repeats=len(points)*3)
    #points = range(1670,1840,10) #range in um, for (111), 15/12/2016
    #camSetupStream("eye","111_bendTestdetZ_3mmHx2mmV_02",repeats=len(points)*3)
    points = range(1560,1710,10) #range in um, for (220), 15/12/2016 overnight
    camSetupStream("eye","220_bendTestdetZ_3mmHx2mmV_03",repeats=len(points)*3)
    print len(points)
    print points
    for i in points:
        bendPos = float(i) / 1000.
        pos xtalBend bendPos
        for j in range(0,19): #i.e. wait 19 mins, but re-align after each minute
            camOptimise("eye")
            sleep(2)
            xtalAlign("eye",False)
            sleep(60)
        for j in detZpoints:
            pos det1Z j
            sleep(60) #wait 1 minutes for det1Z to stop swinging
            xtalAlign("eye",False)
            camOptimise("eye")
            sleep(2)
            exposureTime = caget("BL15J-DI-EYE-01:CAM:AcquireTime_RBV")
            print "det1Z "+str(det1Z.getPosition())+" xtalBend "+str(xtalBend.getPosition())+" xtalBragg "+str(xtalBragg.getPosition())+" "+str(eyepySizeX)+" "+str(eyestatMean)+" "+str(exposureTime)
            camGrabFrameToStream("eye")

def runCheckFocusasfunctionofS1(filename):
    pos s1gapY 1.5
    points = dnp.arange(6.,0.,-0.5)
    camSetupStream("eye",filename,repeats=len(points))
    for i in points:
        pos s1gapX i
        sleep(10)
        camOptimise("eye")
        xtalAlign("eye",False)
        sleep(2)
        exposureTime = caget("BL15J-DI-EYE-01:CAM:AcquireTime_RBV")
        print "s1gapX "+str(s1gapX.getPosition())+" "+str(eyepySizeX)+" "+str(eyestatMean)+" "+str(exposureTime)
        camGrabFrameToStream("eye")
    pos s1gapX points[0]
    print "runCheckFocusasfunctionofS1 complete!"

def runCheckFocusasfunctionofS2(filename):
    points = dnp.arange(5.0,0.,-0.25)
    camSetupStream("eye",filename,repeats=len(points))
    pos s2gapX 10
    camOptimise("bpm2")
    xtalAlign("bpm2",False)
    for i in points:
        pos s2gapX i
        sleep(1)
        camOptimise("eye")
        sleep(1)
        exposureTime = caget("BL15J-DI-EYE-01:CAM:AcquireTime_RBV")
        print "s2gapX "+str(s2gapX.getPosition())+" "+str(eyepySizeX)+" "+str(eyestatMean)+" "+str(exposureTime)
        camGrabFrameToStream("eye")
    pos s2gapX 10
    print "runCheckFocusasfunctionofS2 complete!"

def runCheckFocusasfunctionofS3(filename):
    points = dnp.arange(3.0,0.,-0.1)
    camSetupStream("eye",filename,repeats=len(points))
    pos s3gapX 7
    camOptimise("bpm2")
    xtalAlign("bpm2",False)
    for i in points:
        pos s3gapX i
        sleep(1)
        camOptimise("eye")
        sleep(1)
        exposureTime = caget("BL15J-DI-EYE-01:CAM:AcquireTime_RBV")
        print "s3gapX "+str(s3gapX.getPosition())+" "+str(eyepySizeX)+" "+str(eyestatMean)+" "+str(exposureTime)
        camGrabFrameToStream("eye")
    pos s3gapX 7
    print "runCheckFocusasfunctionofS3 complete!"

def runCheckFocusasfunctionofS4(filename):
    points = dnp.arange(2.0,0.,-0.1)
    camSetupStream("eye",filename,repeats=len(points))
    pos s4gapX 7
    camOptimise("bpm2")
    xtalAlign("bpm2",False)
    for i in points:
        pos s4gapX i
        sleep(1)
        camOptimise("eye")
        sleep(1)
        exposureTime = caget("BL15J-DI-EYE-01:CAM:AcquireTime_RBV")
        print "s4gapX "+str(s4gapX.getPosition())+" "+str(eyepySizeX)+" "+str(eyestatMean)+" "+str(exposureTime)
        camGrabFrameToStream("eye")
    pos s4gapX 7
    print "runCheckFocusasfunctionofS4 complete!"

def runCheckFocusasfunctionofS5(filename):
    points = dnp.arange(2.0,0.,-0.1)
    camSetupStream("eye",filename,repeats=len(points))
    pos s5gapX 7
    camOptimise("bpm2")
    xtalAlign("bpm2",False)
    for i in points:
        pos s5gapX i
        sleep(1)
        camOptimise("eye")
        sleep(1)
        exposureTime = caget("BL15J-DI-EYE-01:CAM:AcquireTime_RBV")
        print "s5gapX "+str(s5gapX.getPosition())+" "+str(eyepySizeX)+" "+str(eyestatMean)+" "+str(exposureTime)
        camGrabFrameToStream("eye")
    pos s5gapX 7
    print "runCheckFocusasfunctionofS5 complete!"

def runCheckFocusasfunctionofS1S2S3S4S5(filename):
    tempname = filename+"_S1"
    runCheckFocusasfunctionofS1(tempname)
    tempname = filename+"_S2"
    runCheckFocusasfunctionofS2(tempname)
    tempname = filename+"_S3"
    runCheckFocusasfunctionofS3(tempname)
    tempname = filename+"_S4"
    runCheckFocusasfunctionofS4(tempname)
    tempname = filename+"_S5"
    runCheckFocusasfunctionofS5(tempname)
    print "runCheckFocusasfunctionofS1S2S3S4S5 complete!!!"

def runCheckBeamSizeasfunctionofS1S2(filename):
    sleep(600)
    pointsS1 = dnp.arange(6.,0.,-0.5)
    pointsS2 = dnp.arange(5.0,0.,-0.25)
    noPoints = len(pointsS1)*len(pointsS2)
    #camSetupStream("eye",filename,repeats=noPoints)
    pos s1gapX 6
    pos s2gapX 10
    camOptimise("bpm2")
    xtalAlign("bpm2",False)
    for i in pointsS1:
        pos s1gapX i
        for j in pointsS2:
            pos s2gapX j
            sleep(1)
            camOptimise("eye")
            sleep(1)
            exposureTime = caget("BL15J-DI-EYE-01:CAM:AcquireTime_RBV")
            sleep(exposureTime)
            print "s1gapX "+str(s1gapX.getPosition())+" "+"s2gapX "+str(s2gapX.getPosition())+" "+str(eyepySizeX)+" "+str(eyestatMean)+" "+str(exposureTime)
            #camGrabFrameToStream("eye")
    pos s1gapX 6
    pos s2gapX 10
    print "runCheckBeamSizeasfunctionofS1S2 complete!"

#eyestatI = DisplayEpicsPVClass("eyestatI", "BL15J-EA-CALC-01.H", "counts", "%.0f")
def runCheckBeamSizeasfunctionofS5S4S3(filename):
    pos s1gapX 6
    pos s2gapX 10
    pos s3gapX 7
    pos s4gapX 7
    pos s5gapX 7
    pointsS3 = dnp.arange(3.0,0.,-0.1)
    pointsS4 = dnp.arange(2.0,0.,-0.05)
    camOptimise("bpm2")
    xtalAlign("bpm2",False)
    for i in pointsS4:
        pos s4gapX i
        posS5 = float(i) + 0.1
        pos s5gapX posS5
        for j in pointsS3:
            pos s3gapX j
            sleep(1)
            camOptimise("eye")
            sleep(1)
            exposureTime = caget("BL15J-DI-EYE-01:CAM:AcquireTime_RBV")
            sleep(float(exposureTime))
            print "s4gapX "+str(s4gapX.getPosition())+" "+"s3gapX "+str(s3gapX.getPosition())+" "+str(eyepySizeX)+" "+str(eyestatMean)+" "+str(exposureTime)
    pos s3gapX 7
    pos s4gapX 7
    pos s5gapX 7
    print "runCheckBeamSizeasfunctionofS1S2 complete!"

def runCheckFocusasfunctionofAllSlits(filename):
    pos s1gapX 6.0
    pos s1gapY 1.5
    pos s2gapX 10
    pos s3gapX 7
    pos s4gapX 7
    pos s5gapX 7
    points = dnp.arange(1.5,0.,-0.1)
    camSetupStream("eye",filename,repeats=len(points))
    camOptimise("bpm2")
    xtalAlign("bpm2",False)
    for i in points:
        poss2 = i*4.907
        poss3 = i*1.865
        pos s3gapX poss3
        pos s4gapX i
        pos s5gapX i
        sleep(2)
        camOptimise("eye")
        sleep(2)
        exposureTime = caget("BL15J-DI-EYE-01:CAM:AcquireTime_RBV")
        print "s5gapX "+str(s5gapX.getPosition())+" "+str(eyepySizeX)+" "+str(eyestatMean)+" "+str(exposureTime)
        camGrabFrameToStream("eye")
    print "runCheckFocusasfunctionofS5 complete!"

def runBenderTestAtMultiplePoints():
    pos xtalBend 1.575
    pos xtalBragg 6.629
    pos s1gapX 1.0
    pos s1gapY 1.0
    pos s1cenX 0.0
    print "=== at s1cenX = 0.0 mm ==="
    runBenderTest()
    pos s1cenX 1.5
    pos xtalBend 1.575
    pos xtalBragg 6.629
    print "=== at s1cenX = 1.5 mm ==="
    runBenderTest()
    pos s1cenX -1.5
    pos xtalBend 1.575
    pos xtalBragg 6.629
    print "=== at s1cenX = -1.5 mm ==="
    runBenderTest()
    s1close
    

def focus_collection(filename):
    points = range(12600,13920,20) #311
    #points = range(12300,13220,20) #220
    camSetupStream("bpm1","bpm1_"+str(filename),len(points))
    camSetupStream("bpm2","bpm2_"+str(filename),len(points))
    camSetupStream("eye","eye_"+str(filename),len(points))
    for i in points: #range in um
        bendPos = float(i) / 10000
        runupBendPos = bendPos - 0.02
        resetBendPos = bendPos - 0.05
        for j in range(3):
            try:
                pos xtalBend runupBendPos
                sleep(1.0)
            except gda.device.DeviceException:
                caput("BL15J-OP-LAUE-01:BENDER.VAL",resetBendPos)
                sleep(1.0)
        for j in range(5):
            try:
                pos xtalBend bendPos
                sleep(1.0)
            except gda.device.DeviceException:
                caput("BL15J-OP-LAUE-01:BENDER.VAL",bendPos)
                sleep(1.0)
        sleep(5.0)
        alignXtal(False)
        sleep(5.0)
        print str(xtalBend)+" "+str(bpm1statMean)+" "+str(bpm1pySizeX)+" "+str(bpm2statMean)+" "+str(bpm2pySizeX)+" "+str(eyestatMean)+" "+str(eyepySizeX)+" "+str(xtalBragg)
        camGrabFrameToStream("bpm1")
        camGrabFrameToStream("bpm2")
        camGrabFrameToStream("eye")
    print "focus_collection finished!!"

def focus_collection_slits():
    s1sizes = [1.5,1.0,0.5]
    for s1size in s1sizes:
        print "s1 size = "+str(s1size)
        pos s1gapX s1size
        tempfilename = "220_focus_s1size_"+str(s1size)+"mm"
        print tempfilename
        focus_collection(tempfilename)
    #Repeat a collection at the end
    s1size = 3.0
    print "s1 size = "+str(s1size)+" REPEAT"
    pos s1gapX s1size
    tempfilename = "220_focus_s1size_"+str(s1size)+"mm_REPEAT01"
    print tempfilename
    focus_collection(tempfilename)

def focus_collection_repeats():
    focus_collection("311_focus_s1size3mm__REPEAT02")
    focus_collection("311_focus_s1size3mm__REPEAT03")

def focus_collection_continue():
    points = range(13340,13720,20)
    for i in points: #range in um
        bendPos = float(i) / 10000
        runupBendPos = bendPos - 0.02
        resetBendPos = bendPos - 0.05
        for j in range(3):
            try:
                pos xtalBend runupBendPos
                sleep(1.0)
            except gda.device.DeviceException:
                caput("BL15J-OP-LAUE-01:BENDER.VAL",resetBendPos)
                sleep(1.0)
        for j in range(5):
            try:
                pos xtalBend bendPos
                sleep(1.0)
            except gda.device.DeviceException:
                caput("BL15J-OP-LAUE-01:BENDER.VAL",bendPos)
                sleep(1.0)
        sleep(5.0)
        alignXtal(False)
        sleep(5.0)
        print str(xtalBend)+" "+str(bpm1statMean)+" "+str(bpm1pySizeX)+" "+str(bpm2statMean)+" "+str(bpm2pySizeX)+" "+str(eyestatMean)+" "+str(eyepySizeX)+" "+str(xtalBragg)
        camGrabFrameToStream("bpm1")
        camGrabFrameToStream("bpm2")
        camGrabFrameToStream("eye")
    print "focus_collection finished!!"

def yaw_collection(filename):
    points = range(-15,16,1)
    camSetupStream("eye","eye_"+str(filename),len(points))
    for i in points:
        yawPos = float(i)
        pos xtalYaw yawPos
        print str(xtalYaw)+" "+str(eyestatMean)+" "+str(eyepySizeX)+" "+str(eyepySizeY)+" "+str(eyepyCenX)+" "+str(eyepyCenY)
        camGrabFrameToStream("eye")
    print "yaw_collection finished"
        
def roll_collection(filename):
    #points = range(-111,331,10) #220
    points = range(-800,-350,10) #311
    camSetupStream("eye","eye_"+str(filename),len(points))
    for i in points:
        rollPos = float(i) / 100
        pos xtalRoll rollPos
        print str(xtalRoll)+" "+str(eyestatMean)+" "+str(eyepySizeX)+" "+str(eyepySizeY)+" "+str(eyepyCenX)+" "+str(eyepyCenY)
        camGrabFrameToStream("eye")
    print "roll_collection finished"
    
def stability_collection(filename):
    points = range (0,60,1)
    camSetupStream("eye","eye_"+str(filename),len(points))
    for i in points:
        print str(xtalBend)+" "+str(eyestatMean)+" "+str(eyepySizeX)+" "+str(eyepySizeY)+" "+str(eyepyCenX)+" "+str(eyepyCenY)
        camGrabFrameToStream("eye")
        sleep(600)

def s1_scan_at_focus(filename):
    pos s1gapX 0.2
    points = range(-15,16,1)
    camSetupStream("bpm1","bpm1_"+str(filename),len(points))
    camSetupStream("bpm2","bpm2_"+str(filename),len(points))
    camSetupStream("eye","eye_"+str(filename),len(points))
    for i in points:
        s1XPos = float(i) / 10
        pos s1cenX s1XPos
        sleep(10)
        print str(s1cenX)+" "+str(bpm1statMean)+" "+str(bpm1pySizeX)+" "+str(bpm1pyCenX)+" "+str(bpm2statMean)+" "+str(bpm2pySizeX)+" "+str(bpm2pyCenX)+" "+str(eyestatMean)+" "+str(eyepySizeX)+" "+str(eyepyCenX)
        camGrabFrameToStream("bpm1")
        camGrabFrameToStream("bpm2")
        camGrabFrameToStream("eye")
    print "s1_scan_at_focus finished"

def pitch_collection(filename):
    #points = range(2200,5400,20) #311
    points = range(640,3700,200) #220
    camSetupStream("bpm1","bpm1_"+str(filename),len(points))
    for i in points:
        sleep(0.5)
        braggPos = float(i) / 1000
        pos xtalBragg braggPos
        print str(xtalBragg)+" "+str(bpm1stat6Mean)+" "+str(bpm1pySizeX)
        camGrabFrameToStream("bpm1")
    print "pitch_collection finished"

print "bender_tests loaded"