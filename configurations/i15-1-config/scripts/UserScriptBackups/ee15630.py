from time import sleep
#peSetDetector(20) #Done

def ee15630_test():
    print "Description of methodology only"
    
def ee15630_setPath():
    peSetPath("x:\\2016\\ee15630-1\\")
    
def ee15630_SiCalibration():
    f2Set("1%")
    spinOn
    d1in
    eh3close
    peCollectDark(200,"00001_dark_10x20s")
    eh3open
    sleep(20)
    peCollectData(200,"00002_Si_NIST_SRM640c_10x20s")
    eh3close
    f2Set("100%")

def ee15630_emptyCap():
    spinOn
    eh3close
    peCollectDark(600,"00003_dark_30x20s")
    d1in
    eh3open
    sleep(20)
    peCollectData(600,"00004_EmptyBS_1mm_30x20s")
    eh3close

def ee15630_emptyXPDF():
    spinOn
    eh3close
    peCollectDark(600,"00005_dark_30x20s")
    d1in
    eh3open
    sleep(20)
    peCollectData(600,"00006_EmptyXPDF_30x20s") 
    eh3close
    spinOff

def ee15630_emptyXPDF_version2():
    spinOn
    d1in
    eh3open
    sleep(20)
    peCollectData(600,"00007_EmptyXPDF_30x20s") 
    eh3close
    spinOff
    
#setCryoTemp(temp=303)

def ee15630_VT(sample_name,start_n):
    # start_n should end in 1
    spinOn
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
    spinOff

def ee15630_RT_Sample(sample_name,start_n):
    # start_n should end in 1
    # setup
    spinOn
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
    spinOff
    print 'Completed.'

def ee15630_RT_Sample_noSpin(sample_name,start_n):
    # setup
    d1in
    
    # do the collection
    eh3open
    sleep(20) # wait one frame
    tempName = str(start_n).zfill(5)+'_'+sample_name+'_30x20s'
    peCollectData(20,tempName)
    eh3close
    print 'Completed.'


def ee15630_VT_finish(sample_name):
    spinOn
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
    spinOff

def ee15630_SiCalibration_2():
    f2Set("1%")
    spinOn
    d1in
    eh3close
    peCollectDark(200,"d01001_dark_10x20s")
    eh3open
    sleep(20)
    peCollectData(200,"01001_Si_NIST_SRM640c_10x20s")
    eh3close
    f2Set("100%")

    
print "ee15630 scripts loaded"