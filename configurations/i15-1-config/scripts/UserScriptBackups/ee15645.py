#Chater/Rosseinsky
#All samples loaded in 1 mm OD / 0.78 mm ID borosilicate capillaries
#(311) crystal, focused with bender at 1.365 mm
#Slit settings: h x v (mm^2)
#    S1 = 3.5 x 0.5
#    S2 = 3.0 x 0.6
#    S3 = 1.2 x 0.6
#    S4 = 0.2 x 0.2
#    S5 = 0.25 x 0.25


from time import sleep

#peSetDetector(10)

def ee15645_calibration():
    peSetPath("ee15645")
    peCollectDark(120,"000_dark_120s")
    peCollectData(120,"001_Si_NIST_SRM640c_120s_Spinner")

def ee15645_collection_01():
    peSetPath("ee15645")
    spinOn()
    peCollectDark(1200,"002_dark_1200s")
    samSelect("empty")
    peCollectData(1200,"003_EmptyXPDF_1200s_Spinner")
    sleep(120)
    peCollectDark(1200,"004_dark_1200s")
    samSelect("spin")
    peCollectData(1200,"005_EmptyCapillary_1200s_Spinner")
    spinOff()
    
def ee15645_collection_02():
    peSetPath("ee15645")
    spinOn()
    peCollectDark(1200,"006_dark_1200s")
    samSelect("spin")
    peCollectData(1200,"007_DS-370-C3_CAF-1_1200s_Spinner")
    spinOff()
    
def ee15645_collection_03():
    peSetPath("ee15645")
    spinOn()
    samSelect("spin")
    peCollectData(1200,"008_DS-370-B3_CAF-1_1200s_Spinner")
    spinOff()

def ee15645_collection_04():
    peSetPath("ee15645")
    spinOn()
    peCollectDark(1200,"009_dark_1200s")
    samSelect("spin")
    peCollectData(1200,"010_DS-360C_CAF-2_1200s_Spinner")
    spinOff()
    
def ee15645_RT_Sample(sample_name,start_n):
    peSetPath("x:\\2016\\ee15645-1\\")
    ## start_n should end in 1
    spinOn
    d1in
    eh3close
    sleep(20) # wait one frame
    tempName = 'd'+str(start_n).zfill(5)+'_dark_30x20s'
    peCollectDark(600,tempName)
    ## do the collection
    eh3open
    sleep(20) # wait one frame
    tempName = str(start_n).zfill(5)+'_'+sample_name+'_30x20s'
    peCollectData(600,tempName)
    eh3close
    spinOff
    print 'Completed.'
    
print "ee15645 scripts loaded"