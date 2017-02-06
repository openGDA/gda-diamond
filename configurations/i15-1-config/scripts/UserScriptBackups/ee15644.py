from time import sleep
from gda.data import NumTracker

def ee15644_collection():
    print "Description of methodology only"
    #NOTE: These will burn in! On I15 it was 1 hr between collections.
    #Test "detector monitoring script", and filtering as options.
    #On I15 a relatively short (EE11665) acquire time was used; definitely look at using f2..
    #Collections were done after 1 hr at each temperature (i.e. both a dwell, and letting the burn-in subside
    
    #COLLECTION OUTLINE:
    #1: RT
    #[1b: IF we can increase the rate, collections in 100C steps on the way up to 400C in particular, or all the way up to 900C would be good.] 
    #2: Ramp to 900C (any rate), then collection
    #3: Hold for 1hr, then collect
    #4: Hold for a further 1hr, then collect
    #5: Cool to 620C (any rate), then collection
    #6: Hold for 1hr, then collect
    #7: Hold for a further 1hr, then collect
    #8: Cool in 20C steps from 600-500C, each with 1hr dwell, collect, 1hr dwell, collect
    #9: Cool in 10C steps from 490-400C, each with 1hr dwell, collect, 1hr dwell, collect
    #10: Hold at 400C, (1hr dwell, collect) x n repeats. Superlattice peaks should start to form within 1hr.
    #    Do this for a total of at least 3 repeats.
    
def ee15644_collection_01():
    #Testing different collection strategies
    #10s acquireTime, 1% filter.
    #Use the calibration from ee15645
    peSetPath("ee15644")
    spinOn()
    samSelect("spin")
    peCollectData(1200,"001_Cu3Au_10x120s_1pcFlux_Spinner")
    #There was some beam instability during this measurement - feedback failed for a a few mins
    peMonitorStability()
    #Detector was declared stable after 280.66574 seconds, although some small features remained.
    
def ee15644_collection_02():
    newAcquireTime = 5
    peSetDetector(newAcquireTime)
    peMonitorStability(preWait=newAcquireTime*2)
    peCollectDark(600,"002_dark_120x5s")
    #Detector was saturating, so no data was taken.
    #Detector was declared stable after 692.13273 seconds.
    
def ee15644_collection_03():
    newAcquireTime = 4
    peSetDetector(newAcquireTime)
    peMonitorStability(preWait=newAcquireTime*2)
    peCollectDark(600,"003_dark_150x4s")
    #Images monitored in GDA with arr
    sleep(1200)
    peCollectDark(1200,"004_dark_300x4s")
    spinOn()
    samSelect("spin")
    peCollectData(1200,"005_Cu3Au_300x4s_10pcFlux_Spinner")
    spinOff()
    peMonitorStability(preWait=newAcquireTime*2)
    
#06/08/2016
#peSetPath("x:\\2016\\ee15644-1\\")
#peSetDetector(10)
def ee15644_emptyCap_01():
    eh3close
    spinOn()
    d1in
    peCollectDark(600,"d0001_dark_60x10s")
    eh3open
    sleep(10)
    tempName = "0001_Empty_0p5QGCT_Obs_"+str(blowerT.getPosition())+"C"
    peCollectData(600,tempName)
    
def ee15644_emptyCap_02():
    points = [400,450,550,620,900]
    print "that's %i points, at roughly 35 minutes per point is %2.2f hours" % (len(points),35.*len(points)/60)
    print "The blower stage should be at 55 mm. "
    spinOn
    for i,temp in enumerate(points):
        setBlowerTemp(temp)
        eh3close
        sleep(540)                                                                # check this
        tempName = "d"+str(i+2).zfill(4)+"_dark_30x10s"
        peCollectDark(300,tempName)
        print(tempName)
        d1in
        eh3open
        sleep(10)
        tempName = str(i+2).zfill(4)+"_Empty_0p5QGCT_Set_"+str(temp)+"C_Obs_"+str(blowerT.getPosition())+"C_60x10s"
        peCollectData(600,tempName)
        print(tempName)
    eh3close
    
def ee15644_emptyXPDF():
    blowerIn
    spinOn
    eh3close
    peCollectDark(600,"d0007_dark_60x10s")
    d1in
    eh3open
    sleep(10)
    peCollectData(600,"0007_Empty_0p5QGCT_60x10s") #SHOULD HAVE BEEN 0007_Empty_XPDF_60x10s 
    eh3close
    
def ee15644_emptyCap_03():
    blowerIn
    spinOn
    eh3close
    peCollectDark(600,"d0008_dark_60x10s")
    d1in
    eh3open
    sleep(10)
    peCollectData(600,"0008_Empty_0p5QGCT_60x10s")
    eh3close
    
def ee15644_SiCalibration():
    blowerIn
    spinOn
    d1in
    eh3open
    sleep(10)
    peCollectData(600,"0009_Si_NIST_SRM640c_60x10s")
    eh3close
    
#FLUX NOTES
#Previous measurements have shown that we need 10pc flux and 5 s data collections.
#D2 measurements were performed to determine the actuation flux attenuation for normalisation.
#Note that empty collections were with a detector time of 10 s.
#d2 at 100pc flux = 4.54(2) (1 uA range)
#d2 at 10pc flux = 0.75(1) (1 uA range) or 7.45(4) (100 nA range)

#scan x 1 10000 1 w 5 pe1Proc5statMean #Used to look at image burn-in, started at 16:37, see 1721.dat
#Burn-in was down to noise level at 16:50, so 15 mins is plenty
    
def ee15644_part01_RT():
    print "=== First phase ==="
    #peSetDetector(5) #Done
    #f2Set("10%") #Done
    #blowerIn #Done
    #spinOn #Done
    eh3close
    peCollectDark(600,"d1001_dark_120x5s")
    d1in
    eh3open
    sleep(10)
    peCollectData(600,"1001_Cu3Au_RT_120x5s")
    eh3close
    
def ee15644_part02():
    print "=== Second phase ==="
    eh3close
    temp = 900
    setBlowerTemp(temp)
    points = [900,900,900]
    firstPoint = True
    for i,temp in enumerate(points):
        setBlowerTemp(temp)
        eh3close
        if firstPoint == True:
            sleep(1) #Immediately do collection (after dark and 10 mins dwell)
            firstPoint = False
        else:
            print "Sleeping for 2400 seconds"
            sleep(2400) #Sleep 40 mins
        tempName = "d"+str(i+2000).zfill(4)+"_dark_120x5s"
        peCollectDark(600,tempName) #10 mins dark
        d1in
        eh3open
        sleep(10)
        tempName = str(i+2000).zfill(4)+"_Cu3Au_Set_"+str(temp)+"C_Obs_"+str(blowerT.getPosition())+"C_120x5s"
        peCollectData(600,tempName) #10 mins collection
    print "=== Third phase ==="
    points = [620,620,620]
    firstPoint = True
    for i,temp in enumerate(points):
        setBlowerTemp(temp)
        eh3close
        if firstPoint == True:
            print "Sleeping for 2800 seconds"
            sleep(2800) #Ramp will take 47 mins at 0.1 C per second
            firstPoint = False
        else:
            print "Sleeping for 2400 seconds"
            sleep(2400) #Sleep 40 mins
        tempName = "d"+str(i+3000).zfill(4)+"_dark_120x5s"
        peCollectDark(600,tempName) #10 mins dark
        d1in
        eh3open
        sleep(10)
        tempName = str(i+3000).zfill(4)+"_Cu3Au_Set_"+str(temp)+"C_Obs_"+str(blowerT.getPosition())+"C_120x5s"
        peCollectData(600,tempName) #10 mins collection
    print "=== Fourth phase ===" #Cool in 20C steps from 600-500C, each with 1hr dwell, collect, 1hr dwell, collect
    points = [600,580,560,540,520,500]
    for i,temp in enumerate(points):
        setBlowerTemp(temp)
        eh3close
        sleep(200) #Ramp will take 3.3 mins at 0.1 C per second
        tempName = "d"+str(i+4000).zfill(4)+"a_dark_120x5s"
        peCollectDark(600,tempName) #10 mins dark
        d1in
        eh3open
        sleep(10)
        tempName = str(i+4000).zfill(4)+"a_Cu3Au_Set_"+str(temp)+"C_Obs_"+str(blowerT.getPosition())+"C_120x5s"
        peCollectData(600,tempName) #10 mins collection
        print "Sleeping for 2400 seconds"
        sleep(2400) #Sleep 40 mins
        tempName = "d"+str(i+4000).zfill(4)+"b_dark_120x5s"
        peCollectDark(600,tempName) #10 mins dark
        d1in
        eh3open
        sleep(10)
        tempName = str(i+4000).zfill(4)+"b_Cu3Au_Set_"+str(temp)+"C_Obs_"+str(blowerT.getPosition())+"C_120x5s"
        peCollectData(600,tempName) #10 mins collection
        print "Sleeping for 2400 seconds"
        sleep(2400) #Sleep 40 mins
        tempName = "d"+str(i+4000).zfill(4)+"c_dark_120x5s"
        peCollectDark(600,tempName) #10 mins dark
        d1in
        eh3open
        sleep(10)
        tempName = str(i+4000).zfill(4)+"c_Cu3Au_Set_"+str(temp)+"C_Obs_"+str(blowerT.getPosition())+"C_120x5s"
        peCollectData(600,tempName) #10 mins collection
        sleep(660) #Additional 11 mins for burn-in to fade
    print "===Fifth phase===" #9: Cool in 10C steps from 490-400C, each with 1hr dwell, collect, 1hr dwell, collect
    points = [490,480,470,460,450,440,430,420,410,400]
    for i,temp in enumerate(points):
        setBlowerTemp(temp)
        eh3close
        sleep(100) #Ramp will take 2 mins at 0.1 C per second
        tempName = "d"+str(i+5000).zfill(4)+"a_dark_120x5s"
        peCollectDark(600,tempName) #10 mins dark
        d1in
        eh3open
        sleep(10)
        tempName = str(i+5000).zfill(4)+"a_Cu3Au_Set_"+str(temp)+"C_Obs_"+str(blowerT.getPosition())+"C_120x5s"
        peCollectData(600,tempName) #10 mins collection
        print "Sleeping for 2400 seconds"
        sleep(2400) #Sleep 40 mins
        tempName = "d"+str(i+5000).zfill(4)+"b_dark_120x5s"
        peCollectDark(600,tempName) #10 mins dark
        d1in
        eh3open
        sleep(10)
        tempName = str(i+5000).zfill(4)+"b_Cu3Au_Set_"+str(temp)+"C_Obs_"+str(blowerT.getPosition())+"C_120x5s"
        peCollectData(600,tempName) #10 mins collection
        print "Sleeping for 2400 seconds"
        sleep(2400) #Sleep 40 mins
        tempName = "d"+str(i+5000).zfill(4)+"c_dark_120x5s"
        peCollectDark(600,tempName) #10 mins dark
        d1in
        eh3open
        sleep(10)
        tempName = str(i+5000).zfill(4)+"c_Cu3Au_Set_"+str(temp)+"C_Obs_"+str(blowerT.getPosition())+"C_120x5s"
        peCollectData(600,tempName) #10 mins collection
        sleep(660) #Additional 11 mins for burn-in to fade
    print "===Final phase===" #10: Hold at 400C, (1hr dwell, collect) x n repeats. Superlattice peaks should start to form within 1hr.
    points = [400,400,400,400]
    for i,temp in enumerate(points):
        eh3close
        print "Sleeping for 2400 seconds"
        sleep(2400) #Sleep 40 mins
        tempName = "d"+str(i+6000).zfill(4)+"_dark_120x5s"
        peCollectDark(600,tempName) #10 mins dark
        d1in
        eh3open
        sleep(10)
        tempName = str(i+6000).zfill(4)+"_Cu3Au_Set_"+str(temp)+"C_Obs_"+str(blowerT.getPosition())+"C_120x5s"
        peCollectData(600,tempName) #10 mins collection
    
def ee15644_part02_test():
    print "=== Second phase ==="
    #eh3close
    temp = 900
    #setBlowerTemp(temp)
    points = [900,900,900]
    firstPoint = True
    for i,temp in enumerate(points):
        #setBlowerTemp(temp)
        #eh3close
        if firstPoint == True:
            #sleep(1) #Immediately do collection (after dark and 10 mins dwell)
            print "sleep 1 sec"
            firstPoint = False
        else:
            #sleep(2400) #Sleep 40 mins
            print "sleep 40 mins"
        tempName = "d"+str(i+2000).zfill(4)+"_dark_120x5s"
        print tempName
        #peCollectDark(600,tempName) #10 mins dark
        #d1in
        #eh3open
        #sleep(10)
        tempName = str(i+2000).zfill(4)+"_Cu3Au_Set_"+str(temp)+"C_Obs_"+str(blowerT.getPosition())+"C_120x5s"
        print tempName
        #peCollectData(600,tempName) #10 mins collection
    print "=== Third phase ==="
    points = [620,620,620]
    firstPoint = True
    for i,temp in enumerate(points):
        #setBlowerTemp(temp)
        #eh3close
        if firstPoint == True:
            #sleep(2800) #Ramp will take 47 mins at 0.1 C per second
            print "sleeping for 2800 s"
            firstPoint = False
        else:
            print "sleeping for 2400 seconds"
            #sleep(2400) #Sleep 40 mins
        tempName = "d"+str(i+3000).zfill(4)+"_dark_120x5s"
        print tempName
        #peCollectDark(600,tempName) #10 mins dark
        #d1in
        #eh3open
        #sleep(10)
        print "sleeping for 10 s"
        tempName = str(i+3000).zfill(4)+"_Cu3Au_Set_"+str(temp)+"C_Obs_"+str(blowerT.getPosition())+"C_120x5s"
        print tempName
        #peCollectData(600,tempName) #10 mins collection
    print "=== Fourth phase ===" #Cool in 20C steps from 600-500C, each with 1hr dwell, collect, 1hr dwell, collect
    points = [600,580,560,540,520,500]
    for i,temp in enumerate(points):
        #setBlowerTemp(temp)
        #eh3close
        print "sleeping for 200 s"
        #sleep(200) #Ramp will take 3.3 mins at 0.1 C per second
        tempName = "d"+str(i+4000).zfill(4)+"a_dark_120x5s"
        print tempName
        #peCollectDark(600,tempName) #10 mins dark
        #d1in
        #eh3open
        #sleep(10)
        tempName = str(i+4000).zfill(4)+"a_Cu3Au_Set_"+str(temp)+"C_Obs_"+str(blowerT.getPosition())+"C_120x5s"
        print tempName
        #peCollectData(600,tempName) #10 mins collection
        print "sleeping for 2400 s"
        #sleep(2400) #Sleep 40 mins
        tempName = "d"+str(i+4000).zfill(4)+"b_dark_120x5s"
        print tempName
        #peCollectDark(600,tempName) #10 mins dark
        #d1in
        #eh3open
        #sleep(10)
        tempName = str(i+4000).zfill(4)+"b_Cu3Au_Set_"+str(temp)+"C_Obs_"+str(blowerT.getPosition())+"C_120x5s"
        print tempName
        #peCollectData(600,tempName) #10 mins collection
        #sleep(2400) #Sleep 40 mins
        print "sleeping for 2400 s"
        tempName = "d"+str(i+4000).zfill(4)+"c_dark_120x5s"
        print tempName
        #peCollectDark(600,tempName) #10 mins dark
        #d1in
        #eh3open
        #sleep(10)
        tempName = str(i+4000).zfill(4)+"c_Cu3Au_Set_"+str(temp)+"C_Obs_"+str(blowerT.getPosition())+"C_120x5s"
        print tempName
        #peCollectData(600,tempName) #10 mins collection
        #sleep(660) #Additional 11 mins for burn-in to fade
        print "sleeping for 660 s"
    print "===Fifth phase===" #9: Cool in 10C steps from 490-400C, each with 1hr dwell, collect, 1hr dwell, collect
    points = [490,480,470,460,450,440,430,420,410,400]
    for i,temp in enumerate(points):
        #setBlowerTemp(temp)
        #eh3close
        #sleep(100) #Ramp will take 2 mins at 0.1 C per second
        print "sleeping for 100 s"
        tempName = "d"+str(i+5000).zfill(4)+"a_dark_120x5s"
        print tempName
        #peCollectDark(600,tempName) #10 mins dark
        #d1in
        #eh3open
        #sleep(10)
        tempName = str(i+5000).zfill(4)+"a_Cu3Au_Set_"+str(temp)+"C_Obs_"+str(blowerT.getPosition())+"C_120x5s"
        print tempName
        #peCollectData(600,tempName) #10 mins collection
        #sleep(2400) #Sleep 40 mins
        print "sleeping for 2400 s"
        tempName = "d"+str(i+5000).zfill(4)+"b_dark_120x5s"
        print tempName
        #peCollectDark(600,tempName) #10 mins dark
        #d1in
        #eh3open
        #sleep(10)
        tempName = str(i+5000).zfill(4)+"b_Cu3Au_Set_"+str(temp)+"C_Obs_"+str(blowerT.getPosition())+"C_120x5s"
        print tempName
        #peCollectData(600,tempName) #10 mins collection
        print "sleeping for 2400s"
        #sleep(2400) #Sleep 40 mins
        tempName = "d"+str(i+5000).zfill(4)+"c_dark_120x5s"
        print tempName
        #peCollectDark(600,tempName) #10 mins dark
        #d1in
        #eh3open
        #sleep(10)
        tempName = str(i+5000).zfill(4)+"c_Cu3Au_Set_"+str(temp)+"C_Obs_"+str(blowerT.getPosition())+"C_120x5s"
        print tempName
        #peCollectData(600,tempName) #10 mins collection
        #sleep(660) #Additional 11 mins for burn-in to fade
        print "sleeping for 660s"
    print "===Final phase===" #10: Hold at 400C, (1hr dwell, collect) x n repeats. Superlattice peaks should start to form within 1hr.
    points = [400,400,400,400]
    for i,temp in enumerate(points):
        #eh3close
        #sleep(2400) #Sleep 40 mins
        print "sleeping for 2400 s"
        tempName = "d"+str(i+6000).zfill(4)+"_dark_120x5s"
        print tempName
        #peCollectDark(600,tempName) #10 mins dark
        #d1in
        #eh3open
        #sleep(10)
        tempName = str(i+6000).zfill(4)+"_Cu3Au_Set_"+str(temp)+"C_Obs_"+str(blowerT.getPosition())+"C_120x5s"
        print tempName
        #peCollectData(600,tempName) #10 mins collection

def ee15644_part03():
    print "=== Fourth phase ===" #Cool in 20C steps from 600-500C, each with 1hr dwell, collect, 1hr dwell, collect
    temp = 580
    tempName = "d4001b_dark_120x5s"
    peCollectDark(600,tempName) #10 mins dark
    d1in
    eh3open
    sleep(10)
    tempName = "4001b_Cu3Au_Set_"+str(temp)+"C_Obs_"+str(blowerT.getPosition())+"C_120x5s"
    peCollectData(600,tempName) #10 mins collection
    print "Sleeping for 2400 seconds"
    sleep(2400) #Sleep 40 mins
    tempName = "d4001c_dark_120x5s"
    peCollectDark(600,tempName) #10 mins dark
    d1in
    eh3open
    sleep(10)
    tempName = "4001c_Cu3Au_Set_"+str(temp)+"C_Obs_"+str(blowerT.getPosition())+"C_120x5s"
    peCollectData(600,tempName) #10 mins collection
    sleep(660) #Additional 11 mins for burn-in to fade
    points = [560,540,520,500]
    for i,temp in enumerate(points):
        setBlowerTemp(temp)
        eh3close
        sleep(200) #Ramp will take 3.3 mins at 0.1 C per second
        tempName = "d"+str(i+4002).zfill(4)+"a_dark_120x5s"
        peCollectDark(600,tempName) #10 mins dark
        d1in
        eh3open
        sleep(10)
        tempName = str(i+4002).zfill(4)+"a_Cu3Au_Set_"+str(temp)+"C_Obs_"+str(blowerT.getPosition())+"C_120x5s"
        peCollectData(600,tempName) #10 mins collection
        print "Sleeping for 2400 seconds"
        sleep(2400) #Sleep 40 mins
        tempName = "d"+str(i+4002).zfill(4)+"b_dark_120x5s"
        peCollectDark(600,tempName) #10 mins dark
        d1in
        eh3open
        sleep(10)
        tempName = str(i+4002).zfill(4)+"b_Cu3Au_Set_"+str(temp)+"C_Obs_"+str(blowerT.getPosition())+"C_120x5s"
        peCollectData(600,tempName) #10 mins collection
        print "Sleeping for 2400 seconds"
        sleep(2400) #Sleep 40 mins
        tempName = "d"+str(i+4002).zfill(4)+"c_dark_120x5s"
        peCollectDark(600,tempName) #10 mins dark
        d1in
        eh3open
        sleep(10)
        tempName = str(i+4002).zfill(4)+"c_Cu3Au_Set_"+str(temp)+"C_Obs_"+str(blowerT.getPosition())+"C_120x5s"
        peCollectData(600,tempName) #10 mins collection
        sleep(660) #Additional 11 mins for burn-in to fade
    print "===Fifth phase===" #9: Cool in 10C steps from 490-400C, each with 1hr dwell, collect, 1hr dwell, collect
    points = [490,480,470,460,450,440,430,420,410,400]
    for i,temp in enumerate(points):
        setBlowerTemp(temp)
        eh3close
        sleep(100) #Ramp will take 2 mins at 0.1 C per second
        tempName = "d"+str(i+5000).zfill(4)+"a_dark_120x5s"
        peCollectDark(600,tempName) #10 mins dark
        d1in
        eh3open
        sleep(10)
        tempName = str(i+5000).zfill(4)+"a_Cu3Au_Set_"+str(temp)+"C_Obs_"+str(blowerT.getPosition())+"C_120x5s"
        peCollectData(600,tempName) #10 mins collection
        print "Sleeping for 2400 seconds"
        sleep(2400) #Sleep 40 mins
        tempName = "d"+str(i+5000).zfill(4)+"b_dark_120x5s"
        peCollectDark(600,tempName) #10 mins dark
        d1in
        eh3open
        sleep(10)
        tempName = str(i+5000).zfill(4)+"b_Cu3Au_Set_"+str(temp)+"C_Obs_"+str(blowerT.getPosition())+"C_120x5s"
        peCollectData(600,tempName) #10 mins collection
        print "Sleeping for 2400 seconds"
        sleep(2400) #Sleep 40 mins
        tempName = "d"+str(i+5000).zfill(4)+"c_dark_120x5s"
        peCollectDark(600,tempName) #10 mins dark
        d1in
        eh3open
        sleep(10)
        tempName = str(i+5000).zfill(4)+"c_Cu3Au_Set_"+str(temp)+"C_Obs_"+str(blowerT.getPosition())+"C_120x5s"
        peCollectData(600,tempName) #10 mins collection
        sleep(660) #Additional 11 mins for burn-in to fade
    print "===Final phase===" #10: Hold at 400C, (1hr dwell, collect) x n repeats. Superlattice peaks should start to form within 1hr.
    points = [400,400,400,400]
    for i,temp in enumerate(points):
        eh3close
        print "Sleeping for 2400 seconds"
        sleep(2400) #Sleep 40 mins
        tempName = "d"+str(i+6000).zfill(4)+"_dark_120x5s"
        peCollectDark(600,tempName) #10 mins dark
        d1in
        eh3open
        sleep(10)
        tempName = str(i+6000).zfill(4)+"_Cu3Au_Set_"+str(temp)+"C_Obs_"+str(blowerT.getPosition())+"C_120x5s"
        peCollectData(600,tempName) #10 mins collection

def ee15644_part04():
    print "===Fifth phase===" #9: Cool in 10C steps from 490-400C, each with 1hr dwell, collect, 1hr dwell, collect
    temp = 490
    print "Sleeping for 1320 seconds"
    sleep(1320) #Sleep 22 mins
    tempName = "d5000b_dark_120x5s"
    peCollectDark(600,tempName) #10 mins dark
    d1in
    eh3open
    sleep(10)
    tempName = "5000b_Cu3Au_Set_"+str(temp)+"C_Obs_"+str(blowerT.getPosition())+"C_120x5s"
    peCollectData(600,tempName) #10 mins collection
    print "Sleeping for 1320 seconds"
    sleep(1320) #Sleep 22 mins
    tempName = "d5000c_dark_120x5s"
    peCollectDark(600,tempName) #10 mins dark
    d1in
    eh3open
    sleep(10)
    tempName = "5000c_Cu3Au_Set_"+str(temp)+"C_Obs_"+str(blowerT.getPosition())+"C_120x5s"
    peCollectData(600,tempName) #10 mins collection
    sleep(660) #Additional 11 mins for burn-in to fade
    points = [480,470,460,450,440,430,420,410,400]
    for i,temp in enumerate(points):
        setBlowerTemp(temp)
        eh3close
        sleep(100) #Ramp will take 2 mins at 0.1 C per second
        tempName = "d"+str(i+5001).zfill(4)+"a_dark_120x5s"
        peCollectDark(600,tempName) #10 mins dark
        d1in
        eh3open
        sleep(10)
        tempName = str(i+5001).zfill(4)+"a_Cu3Au_Set_"+str(temp)+"C_Obs_"+str(blowerT.getPosition())+"C_120x5s"
        peCollectData(600,tempName) #10 mins collection
        print "Sleeping for 1320 seconds"
        sleep(1320) #Sleep 22 mins
        tempName = "d"+str(i+5001).zfill(4)+"b_dark_120x5s"
        peCollectDark(600,tempName) #10 mins dark
        d1in
        eh3open
        sleep(10)
        tempName = str(i+5001).zfill(4)+"b_Cu3Au_Set_"+str(temp)+"C_Obs_"+str(blowerT.getPosition())+"C_120x5s"
        peCollectData(600,tempName) #10 mins collection
        print "Sleeping for 1320 seconds"
        sleep(1320) #Sleep 22 mins
        tempName = "d"+str(i+5001).zfill(4)+"c_dark_120x5s"
        peCollectDark(600,tempName) #10 mins dark
        d1in
        eh3open
        sleep(10)
        tempName = str(i+5001).zfill(4)+"c_Cu3Au_Set_"+str(temp)+"C_Obs_"+str(blowerT.getPosition())+"C_120x5s"
        peCollectData(600,tempName) #10 mins collection
        sleep(660) #Additional 11 mins for burn-in to fade
    print "===Final phase===" #10: Hold at 400C, (1hr dwell, collect) x n repeats. Superlattice peaks should start to form within 1hr.
    points = [400,400,400,400]
    for i,temp in enumerate(points):
        eh3close
        print "Sleeping for 2400 seconds"
        sleep(2400) #Sleep 40 mins
        tempName = "d"+str(i+6000).zfill(4)+"_dark_120x5s"
        peCollectDark(600,tempName) #10 mins dark
        d1in
        eh3open
        sleep(10)
        tempName = str(i+6000).zfill(4)+"_Cu3Au_Set_"+str(temp)+"C_Obs_"+str(blowerT.getPosition())+"C_120x5s"
        peCollectData(600,tempName) #10 mins collection

def ee15644_part05():
    print "===Final RT measurement==="
    tempName = "d7000_dark_120x5s"
    peCollectDark(600,tempName) #10 mins dark
    d1in
    eh3open
    sleep(10)
    tempName = "7000_Cu3Au_Set_0C_Obs_"+str(blowerT.getPosition())+"C_120x5s"
    peCollectData(600,tempName) #10 mins collection
    eh3close
    print "End of ee15644-1!!"
    
print "ee15644 scripts loaded"