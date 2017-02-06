from time import sleep
#peSetDetector(10) #Done

def ee15682_setPath():
    peSetPath("x:\\2016\\ee15682-1\\")

def ee15682_test():
    print "Description of methodology only"

def samPhiSpinnerGo():
    # check its responding
    a = str(caget("BL15J-MO-TABLE-01:SAMPLE:PHI:CTLR:IDENTIFICATION_RBV"))
    if a == '48':
        # then it's broken
        # spinOfff
        sleep(5)
        # spinOn
        sleep(5)

    # stop the spinner
    caput("BL15J-MO-TABLE-01:SAMPLE:PHI.STOP",1)
    sleep(2)
    
    # rehome
    caput("BL15J-MO-TABLE-01:SAMPLE:PHI.HOMF",1)
    print "homing the phi stage"
    sleep(1)
    while caget("BL15J-MO-TABLE-01:SAMPLE:PHI.MOVN") == "1":
        sleep(0.5)
    
    # make it spin
    print 'starting the spinner. You have 10 minutes of spinning'
    # go to 429496
    caput("BL15J-MO-TABLE-01:SAMPLE:PHI",429495)

def ee15682_emptyCap():
    eh3close
    peCollectDark(600,"d00001_dark_60x10s")
    d1in
    eh3open
    sleep(10)
    samPhiSpinnerGo()
    peCollectData(600,"00001_Empty1mmQGCT_60x10s")
    eh3close

def ee15682_SiCalibration():
    f2Set("10%")
    d1in
    eh3close
    peCollectDark(200,"d00002_dark_20x10s")
    eh3open
    samPhiSpinnerGo()
    sleep(10)
    peCollectData(200,"00002_Si_NIST_SRM640c_20x10s")
    eh3close
    f2Set("100%")

def ee15682_emptyXPDF():
    eh3open
    sleep(10)
    samPhiSpinnerGo()
    peCollectData(600,"00003_EmptyXPDF_60x10s")
    eh3close

def ee15682_RT_Sample(sample_name,n,dark=True,wait_seconds=0):
    # setup
    d1in
    print 'waiting for '+str(wait_seconds)+' s'
    sleep(wait_seconds)
    if dark:
        # do a dark
        eh3close
        sleep(10) # wait one frame
        tempName = 'd'+str(n).zfill(5)+'_dark_60x10s'
        peCollectDark(600,tempName)
    
    # do the collection
    samPhiSpinnerGo()
    eh3open
    sleep(10) # wait one frame
    tempName = str(n).zfill(5)+'_'+sample_name+'_60x10s'
    peCollectData(600,tempName)
    eh3close
    
    print 'Completed.'










######################################################################################################
def eeXXXXX_SiCalibration():
    f2Set("1%")
    # spinOn
    d1in
    eh3close
    peCollectDark(200,"00001_dark_10x20s")
    eh3open
    sleep(20)
    peCollectData(200,"00002_Si_NIST_SRM640c_10x20s")
    eh3close
    f2Set("100%")

def eeXXXXX_emptyCap():
    # spinOn
    eh3close
    peCollectDark(600,"00003_dark_30x20s")
    d1in
    eh3open
    sleep(20)
    peCollectData(600,"00004_EmptyBS_1mm_30x20s")
    eh3close

def eeXXXXX_emptyXPDF():
    # spinOn
    eh3close
    peCollectDark(600,"00005_dark_30x20s")
    d1in
    eh3open
    sleep(20)
    peCollectData(600,"00006_EmptyXPDF_30x20s") 
    eh3close
    # spinOfff

def eeXXXXX_emptyXPDF_version2():
    # spinOn
    d1in
    eh3open
    sleep(20)
    peCollectData(600,"00007_EmptyXPDF_30x20s") 
    eh3close
    # spinOfff
    
#setCryoTemp(temp=303)

def eeXXXXX_VT(sample_name,start_n):
    # start_n should end in 1
    # spinOn
    d1in
    temps = dnp.arange(303,483,10)
    temps = dnp.append(temps,303)
    for i,temp in enumerate(temps):
        if i == len(temps)-1:
            # it's the last point
            setCryoTemp(temp)
            # wait for the temperature to equilibriate 
            print 'waiting for the temperature to get to ' + str(temp) + ' K'
            sleep(1200)
        else:
            # change temperature
            setCryoTemp(temp)
            # wait for the temperature to equilibriate
            print 'waiting for the temperature to get to ' + str(temp) + ' K' 
            sleep(600)
        # take a dark
        eh3close
        temp_obs = caget("BL15I-CG-CJET-01:STEMP")
        tempName = 'd'+str(i+start_n).zfill(5)+'_dark_'+str(temp)+"Kset_"+str(temp_obs)+"Kobs_30x20s"
        peCollectDark(600,tempName)
        # take a data collection
        eh3open
        temp_obs = caget("BL15I-CG-CJET-01:STEMP")
        tempName = str(i+start_n).zfill(5)+'_'+sample_name+'_'+str(temp)+"Kset_"+str(temp_obs)+"Kobs_30x20s"
        peCollectData(600,tempName)
    eh3close
    # spinOfff

def eeXXXXX_RT_Sample(sample_name,start_n):
    # start_n should end in 1
    # setup
    # spinOn
    d1in
    
    # do a dark
    eh3close
    sleep(20) # wait one frame
    tempName = 'd'+str(start_n).zfill(5)+'_dark_30x20s'
    peCollectDark(600,tempName)
    
    # do the collection
    eh3open
    sleep(20) # wait one frame
    tempName = str(start_n).zfill(5)+'_'+sample_name+'_30x20s'
    peCollectData(600,tempName)
    eh3close
    # spinOfff
    print 'Completed.'

def eeXXXXX_RT_Sample_noSpin(sample_name,start_n):
    # setup
    d1in
    
    # do the collection
    eh3open
    sleep(20) # wait one frame
    tempName = str(start_n).zfill(5)+'_'+sample_name+'_30x20s'
    peCollectData(20,tempName)
    eh3close
    print 'Completed.'


def eeXXXXX_VT_finish(sample_name):
    # spinOn
    d1in
    # sample has been at 473 since image 118 was taken
    temps = dnp.arange(473,200,-170)
    for i,temp in enumerate(temps):
        if i == len(temps)-1:
            # then it's the last point
            setCryoTemp(temp)
            # wait for the temperature to equilibriate 
            print 'waiting for the temperature to get to ' + str(temp) + ' K'
            sleep(600)
        # take a dark
        eh3close
        temp_obs = caget("BL15I-CG-CJET-01:STEMP")
        tempName = 'd'+str(i+121).zfill(5)+'_dark_'+str(temp)+"Kset_"+str(temp_obs)+"Kobs_30x20s"
        peCollectDark(600,tempName)
        # take a data collection
        eh3open
        temp_obs = caget("BL15I-CG-CJET-01:STEMP")
        tempName = str(i+121).zfill(5)+'_'+sample_name+'_'+str(temp)+"Kset_"+str(temp_obs)+"Kobs_30x20s"
        peCollectData(600,tempName)
    eh3close
    # spinOfff




print "ee15682 scripts loaded"