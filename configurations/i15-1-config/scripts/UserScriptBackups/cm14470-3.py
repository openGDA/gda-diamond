from time import sleep


# some cryojet commands

def collectRTCalibration():
    peCollectData(60,"000_Si_SRM640c_60s")

def testCryojetCal():
    points = [300]
    for i,temp in enumerate(points):
        setCryoTemp(temp)
        #eh3close
        #sleep(540)
        #tempName = str(i).zfill(3)+"_dark_60s"
        #peCollectDark(60,"dark_60s")
        d1in
        eh3open
        sleep(10)
        tempName = str(i).zfill(3)+"_Si-3Al2O3_calibration_Set_"+str(temp)+"K_Obs_"+str(caget("BL15I-CG-CJET-01:STEMP"))+"K"
        peCollectData(60,tempName)
        
def collectCryojetCal():
    points = [81,85] + range(90,530,10)
    sleep(900)
    for i,temp in enumerate(points):
        setCryoTemp(temp)
        eh3close
        sleep(540)
        tempName = str(i).zfill(3)+"_dark_60s"
        peCollectDark(60,"dark_60s")
        d1in
        eh3open
        sleep(10)
        tempName = str(i).zfill(3)+"_Si-3Al2O3_calibration_Set_"+str(temp)+"K_Obs_"+str(caget("BL15I-CG-CJET-01:STEMP"))+"K"
        peCollectData(60,tempName)

def collectFinalCryojetCalPoint():
    """This to semi-complete the above. Temperature did not reach lwoest values so reset to 90 and waited.
    Temperature seemed to converge to ~93 for this flow. More flow seems to mess with the shield flow..."""
    i = 46
    temp = 90
#     eh3close
#     tempName = str(i).zfill(3)+"_dark_60s"
#     peCollectDark(60,tempName)
#     eh3open
    tempName = str(i).zfill(3)+"_Si-3Al2O3_calibration_Set_"+str(temp)+"K_Obs_"+str(caget("BL15I-CG-CJET-01:STEMP"))+"K"
    peCollectData(60,tempName)
    
    
    
def michael_000000001():
#     eh3close
#     peCollectDark(60,"MW_00001_dark_60s")
    eh3open
    peCollectData(60,"MW_00002_Si_SRM640C_60s")
    
    
def michael_000000001b():
    d1in
    eh3open
    peCollectData(60,"MW_00002_Zr-CDC-H2O_60s")
    eh3close

def michael_000000001c():
    d1in
    eh3close
    peCollectDark(60*10,"MW_00003_dark_60x10s")
    eh3open
    # the empty is at samX = -107.9973
    peCollectData(60*10,"MW_00004_emptyCapillary_60x10s")
    eh3close

def michael_000000001d():
    pos samX -90
    d1in
    eh3open
    peCollectData(60*10,"MW_00005_emptyBeamline_60x10ss")
    eh3close
    
def michael_000000001e():
    sample='ZrCDC'
    for i in range(100000):
        if i % 8 == 0:                                          # maybe not 8
            eh3close
            fn = 'MW_'+str(i+10).zfill(6)+'_dark_6x10s'
            peCollectDark(60,fn)
            eh3open
        else:
            fn = 'MW_'+str(i+1000).zfill(6)+'_'+sample+'_6x10s'
            peCollectData(60,fn)
            print "SCREAM IF YOU WANT TO STOP!!!"
            sleep(60*3)                                          # maybe not 3
            print '...TOO LATE SUCKERS. WAIT A MINUTE!'
    eh3close

def scanBlower(start,stop,step,diode=d2):
    import scisoftpy as dnp
    d2in
    d1out
    for val in dnp.arange(start, stop+step, step):
        caput("BL15J-EA-BLOWR-01:TLATE.VAL",val)
        sleep(5)
        print 'Blower Stage: %2.3f mm, diode: %2.4f Volts' % (float(caget("BL15J-EA-BLOWR-01:TLATE.RBV")),diode.getPosition())
    d1in

def collectRTBlowerEmpty():
    eh3close
    peCollectDark(60,"0000_Dark_60s")
    eh3open
    peCollectData(60,"0001_Empty_Beamline")

def collectRTBlowerCalibration():
    eh3open
    peCollectData(60,"0003_Si_NIST_SRM640C_6x10s")
    eh3close

def collectRTBlowerTemperatureCalibrationSampleTestShot():
    eh3open
    spinOn
    peCollectData(60,"0004_Si-3Al2O3_calibration_RT_6x10s")
    spinOff
    eh3close

def collectBlowerCal():
    points = range(50,1000,10)
    print "that's %i points, at roughly 10 minutes per point is %2.2f hours" % (len(points),10.*len(points)/60)
    print "The blower stage should be at 55 mm. "
    spinOn
    for i,temp in enumerate(points):
        setBlowerTemp(temp)
        eh3close
        sleep(540)                                                                # check this
        tempName = str(i+11).zfill(4)+"_dark_60s"
        peCollectDark(60,"dark_60s")
        d1in
        eh3open
        sleep(10)
        tempName = str(i+101).zfill(4)+"_Si-3Al2O3_calibration_Set_"+str(temp)+"C_Obs_"+str(blowerT.getPosition())+"C"
        peCollectData(60,tempName)
    spinOff
    eh3close
    
def collectBlowerCalContinue():
    points = range(290,1000,10)
    print "that's %i points, at roughly 10 minutes per point is %2.2f hours" % (len(points),10.*len(points)/60)
    print "The blower stage should be at 55 mm. "
    spinOn
    for i,temp in enumerate(points):
        setBlowerTemp(temp)
        eh3close
        sleep(540)                                                                # check this
        tempName = str(i+24).zfill(4)+"_dark_60s"
        peCollectDark(60,tempName)
        d1in
        eh3open
        sleep(10)
        tempName = str(i+124).zfill(4)+"_Si-3Al2O3_calibration_Set_"+str(temp)+"C_Obs_"+str(blowerT.getPosition())+"C"
        peCollectData(60,tempName)
    spinOff
    eh3close
    

def collectBlowerCalContinue2():
    points = range(700,1000,25)
    print "that's %i points, at roughly 10 minutes per point is %2.2f hours" % (len(points),10.*len(points)/60)
    print "The blower stage should be at 55 mm. "
    spinOn
    for i,temp in enumerate(points):
        setBlowerTemp(temp)
        eh3close
        sleep(540)                                                                # check this
        tempName = str(i+65).zfill(4)+"_dark_60s"
        peCollectDark(60,tempName)
        d1in
        eh3open
        sleep(10)
        tempName = str(i+164).zfill(4)+"_Si-3Al2O3_calibration_Set_"+str(temp)+"C_Obs_"+str(blowerT.getPosition())+"C"
        peCollectData(60,tempName)
    spinOff
    eh3close
    
def collectBlowerCalFinal():
    temp = 999
    setBlowerTemp(temp)
    #eh3close
    #sleep(540)                                                                # check this
    #tempName = str(77).zfill(4)+"_dark_60s"
    #peCollectDark(60,tempName)
    d1in
    eh3open
    sleep(10)
    tempName = str(176).zfill(4)+"_Si-3Al2O3_calibration_Set_"+str(temp)+"C_Obs_"+str(blowerT.getPosition())+"C"
    peCollectData(60,tempName)
    #spinOff
    eh3close
    
def frivolousDataCollection(filename,number):
    peSetPath('frivolous')
    eh3close
    d1in
    peCollectDark(600,'d'+str(number).zfill(4)+'_dark_30x20s')
    eh3open
    sleep(20)
    peCollectData(1200,str(number).zfill(4)+'_'+filename+'_60x20s')
    eh3close
    
def finalDataCollections(filename,number):
    #peSetPath("x:\\2016\\cm14470-3\\processing\\finalPDFs120816\\")
    #eh3close
    #d1in
    #peCollectDark(600,'d'+str(number).zfill(4)+'_dark_30x20s')
    eh3open
    sleep(20)
    peCollectData(600,str(number).zfill(4)+'_'+filename+'_30x20s')
    eh3close

print "cm14470-3 scripts loaded"