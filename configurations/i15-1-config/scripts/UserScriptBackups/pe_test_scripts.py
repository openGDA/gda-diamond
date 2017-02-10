from time import sleep
from gda.data import NumTracker


def weekend060516():
    """a test designed to determine the optimum operating conditions of the PE.  
    Consists of a "meshgrid" scan over zebra times (between 1 and 20) and gains all) 
    """
    # Definition of things
    zebra_times = [0.5,1,2,5,10,20]
    gains = ["0.25 pF","0.5 pF","1 pF","2 pF","4 pF","8 pF"]
    count_times = [20,120,720]
    
    # friendly versions of times and gains for filenames
    zebra_time_names = ["0p5s","__1s","__2s","__5s","_10s","_20s"]
    gain_names = ["0p25pF","_0p5pF","___1pF","___2pF","___4pF","___8pF"]
    
    for i,gain in enumerate(gains):
        for j,zebra_time in enumerate(zebra_times):
            
            # set the detector up
            print "Attempting to alter the detector to a zebra time of %f seconds and a gain of %s" % (zebra_time,gain)
            peSetDetector(zebra_time,gain)
            
            # wait for the detector to settle while looking at the settle time
            scan x 0 30*60 1 w 1 pe1Proc5statMean
            lsn = NumTracker("i15-1").getCurrentFileNumber()
            print "scan %d was the settling at a gain of %s and a zebra time of %f seconds" % (lsn,gain,zebra_time)
            
            for count_time in count_times:
                # set the filenames
                filename = "Ni_"+str(count_time)+"s_counttime__"+zebra_time_names[j]+"_zebratime__"+gain_names[i]+"_gain"
                darkname = "Dark_"+str(count_time)+"s_counttime__"+zebra_time_names[j]+"_zebratime__"+gain_names[i]+"_gain"
                
                # do a dark
                peCollectDark(count_time,filename=darkname)
                
                # do the data collection
                peCollectData(count_time,filename=filename) 
    print "done"

def quickDarkTest():
    times = [20,40,60,80,100,200,500]
    for time in times:
        fn = "dark_test_"+str(time)+"s"
        peCollectDark(time,fn)


def overnight090516():
    """a test designed to determine the optimum operating conditions of the PE.  
    Consists of a "meshgrid" scan over zebra times (between 1 and 20) and gains all) 
    The I15 rather inconsiderately tripped an interlock and so the above test needs to be partially redone. 
    """
    # Definition of things
    zebra_times = [0.5,1,2,5,10,20]
    gains = ["0.5 pF","1 pF","2 pF"]
    count_times = [20,120,720]
    
    # friendly versions of times and gains for filenames
    zebra_time_names = ["0p5s","__1s","__2s","__5s","_10s","_20s"]
    gain_names = ["_0p5pF","___1pF","___2pF"]
    
    for i,gain in enumerate(gains):
        for j,zebra_time in enumerate(zebra_times):
            
            # set the detector up
            print "Attempting to alter the detector to a zebra time of %f seconds and a gain of %s" % (zebra_time,gain)
            peSetDetector(zebra_time,gain)
            print "IF YOU DONT TURN THE PREVIOUS DARK OFF THEN WHAT DOES THIS MEAN?????"
            # wait for the detector to settle while looking at the settle time
            scan x 0 30*60 1 w 1 pe1Proc5statMean
            lsn = NumTracker("i15-1").getCurrentFileNumber()
            print "scan %d was the settling at a gain of %s and a zebra time of %f seconds" % (lsn,gain,zebra_time)
            
            for count_time in count_times:
                # set the filenames
                filename = "Ni_"+str(count_time)+"s_counttime__"+zebra_time_names[j]+"_zebratime__"+gain_names[i]+"_gain"
                darkname = "Dark_"+str(count_time)+"s_counttime__"+zebra_time_names[j]+"_zebratime__"+gain_names[i]+"_gain"
                
                # do a dark
                peCollectDark(count_time,filename=darkname)
                
                # do the data collection
                peCollectData(count_time,filename=filename) 
    print "done"

def checkPELegacyExposure():
    """ Do a quick comparable check that the external triggering really is better than internal.
    This script collects some data that should in theory be comparable (in form if not in quality!) to that
    which comes from the above script. 
    """
    pe_internal_times = [1,2,5] # we can't do the longer ones
    
    # set the gain
    # i set the gain to 0.5

    for pe_time in pe_internal_times:
        
        # put the internal time
        caput("BL15J-EA-DET-01:CAM:AcquireTime",pe_time)
        
        peOn()
        
        # wait
        sleep(5*60)
        
        # do the dark and the data collection
        peCollectSampleLegacyPointless(20)
        
        lsn = NumTracker("i15-1").getCurrentFileNumber()
        print "If everything has gone to plan:"
        print "--------------------------------------"
        print "Scan #   | Details "
        print "--------------------------------------"
        print "%d     | 20s dark, internal time = %.1f s" % (lsn-1, pe_time)
        print "%d     | 20s data, internal time = %.1f s" % (lsn, pe_time)
        
        peCollectSampleLegacyPointless(120)
        
        # the last scan was NumTracker("i15-1").getCurrentFileNumber()
        lsn = NumTracker("i15-1").getCurrentFileNumber()
        print "If everything has gone to plan:"
        print "--------------------------------------"
        print "Scan #   | Details "
        print "--------------------------------------"
        print "%d     | 120s dark, internal time = %.1f s" % (lsn-1, pe_time)
        print "%d     | 120s data, internal time = %.1f s" % (lsn, pe_time)
        
    print "done"



def overnight050515():
    #peSetDetector(1)
    #sleep(600) #wait 10 mins
    peCollectDark(20,filename="0_dark_20x1s")
    peCollectData(20,filename="0_Ni_20x1s")
    sleep(60)
    peCollectDark(1,filename="1_dark_1x1s")
    peCollectData(20,filename="1_Ni_20x1s")
    sleep(60)
    peCollectDark(120,filename="2_dark_120x1s")
    peCollectData(120,filename="2_Ni_120x1s")
    sleep(60)
    peCollectDark(20,filename="3_dark_20x1s")
    peCollectData(120,filename="3_Ni_120x1s")
    peSetDetector(2)
    sleep(600) #wait 10 mins
    peCollectDark(20,filename="0_dark_10x2s")
    peCollectData(20,filename="0_Ni_10x2s")
    sleep(60)
    peCollectDark(2,filename="1_dark_1x2s")
    peCollectData(20,filename="1_Ni_10x2s")
    sleep(60)
    peCollectDark(120,filename="2_dark_60x2s")
    peCollectData(120,filename="2_Ni_60x2s")
    sleep(60)
    peCollectDark(20,filename="3_dark_10x2s")
    peCollectData(120,filename="3_Ni_60x2s")
    peSetDetector(5)
    sleep(600) #wait 10 mins
    peCollectDark(20,filename="0_dark_4x5s")
    peCollectData(20,filename="0_Ni_4x5s")
    sleep(60)
    peCollectDark(5,filename="1_dark_1x5s")
    peCollectData(20,filename="1_Ni_4x5s")
    sleep(60)
    peCollectDark(120,filename="2_dark_24x5s")
    peCollectData(120,filename="2_Ni_24x5s")
    sleep(60)
    peCollectDark(20,filename="3_dark_4x5s")
    peCollectData(120,filename="3_Ni_24x5s")
    peSetDetector(10)
    sleep(600) #wait 10 mins
    peCollectDark(20,filename="0_dark_2x10s")
    peCollectData(20,filename="0_Ni_2x10s")
    sleep(60)
    peCollectDark(10,filename="1_dark_1x10s")
    peCollectData(20,filename="1_Ni_2x10s")
    sleep(60)
    peCollectDark(120,filename="2_dark_12x10s")
    peCollectData(120,filename="2_Ni_12x10s")
    sleep(60)
    peCollectDark(20,filename="3_dark_2x10s")
    peCollectData(120,filename="3_Ni_12x10s")
    peSetDetector(20)
    sleep(600) #wait 10 mins
    peCollectDark(20,filename="0_dark_1x20s")
    peCollectData(20,filename="0_Ni_1x20s")
    sleep(60)
    peCollectDark(20,filename="1_dark_1x20s")
    peCollectData(20,filename="1_Ni_1x20s")
    sleep(60)
    peCollectDark(120,filename="2_dark_6x20s")
    peCollectData(120,filename="2_Ni_6x20s")
    sleep(60)
    peCollectDark(20,filename="3_dark_1x20s")
    peCollectData(120,filename="3_Ni_6x20s")
    print "overnight collection finished"

def testDarkNoise():
    #pe1statMean = DisplayEpicsPVClass("pe1statMean", "BL15J-EA-DET-01:STAT:MeanValue_RBV", "counts", "%1.4f")
    zebraTime = DisplayEpicsPVClass("zebraTime", "BL15J-EA-ZEBRA-01:DIV1_DIV", "ms", "%1.4f")
    print "without fans, 3 h each"
    print "1 s exposures"
    scan x 1 10800 1 w 1 pe1statMean zebraTime
    print "5 s exposures"
    peSetDetector(5)
    scan x 1 2160 1 w 5 pe1statMean zebraTime
    print "10 s exposures"
    peSetDetector(10)
    scan x 1 1080 1 w 10 pe1statMean zebraTime
    print "with fans, 3 h each"
    caput("BL15J-NT-POWER-01:3:CONTROL","On")
    print "10 s exposures"
    scan x 1 1080 1 w 10 pe1statMean zebraTime
    print "5 s exposures"
    peSetDetector(5)
    scan x 1 2160 1 w 5 pe1statMean zebraTime
    print "1 s exposures"
    peSetDetector(1)
    scan x 1 10800 1 w 1 pe1statMean zebraTime

def testDarkNoise2():
    zebraTime = DisplayEpicsPVClass("zebraTime", "BL15J-EA-ZEBRA-01:DIV1_DIV", "ms", "%1.4f")
    print "10 s exposures"
    peSetDetector(10)
    scan x 1 1080 1 w 10 pe1statMean zebraTime
    
def testDarkNoise3():
    zebraTime = DisplayEpicsPVClass("zebraTime", "BL15J-EA-ZEBRA-01:DIV1_DIV", "ms", "%1.4f")
    print "5 s exposures"
    print "Gain 0.25 pF"
    peSetDetector(5,"0.25 pF")
    scan x 1 720 1 w 5 pe1statMean zebraTime
    print "Gain 0.5 pF"
    peSetDetector(5,"0.5 pF")
    scan x 1 720 1 w 5 pe1statMean zebraTime
    print "Gain 1 pF"
    peSetDetector(5,"1 pF")
    scan x 1 720 1 w 5 pe1statMean zebraTime
    print "Gain 2 pF"
    peSetDetector(5,"2 pF")
    scan x 1 720 1 w 5 pe1statMean zebraTime
    print "Gain 4 pF"
    peSetDetector(5,"4 pF")
    scan x 1 720 1 w 5 pe1statMean zebraTime
    print "Gain 8 pF"
    peSetDetector(5,"8 pF")
    scan x 1 720 1 w 5 pe1statMean zebraTime
    
def collectRadialCells():
    pos samX -172
    pos samY -51
    peCollectData(120,filename="radialcell2_C_6x20s_0p25pF_Vsize0p6mm_repeat")
    sleep(120)
    pos samX -216
    pos samY -50.8
    peCollectData(120,filename="radialcell1_noC_6x20s_0p25pF_Vsize0p6mm_repeat")
    sleep(120)
    pos samX -195
    pos samY -51.2
    peCollectData(120,filename="radialcell__emptyXPDF_6x20s_0p25pF_Vsize0p6mm_repeat")
    
def collectPhil():
    """
    #Sample 1
    pos samX -71.2
    peCollectDark(900,"pe_dark_900s_03")
    peCollectData(900,filename="Empty_XPDF_samChanger_900s")
    #Sample 2
    pos samX -78.15
    sleep(120)
    peCollectDark(900,"pe_dark_900s_04")
    peCollectData(900,filename="Empty_4mm_cap_samChanger_900s")
    #Sample 3
    pos samX -64.25
    sleep(120)
    peCollectDark(900,"pe_dark_900s_05")
    peCollectData(900,filename="H2O_4mm_cap_samChanger_900s")
    #Sample 4
    pos samX -95.9
    sleep(120)
    peCollectDark(900,"pe_dark_900s_06")
    peCollectData(900,filename="CeO2_nanoSol_4mm_cap_samChanger_900s")
    #Sample 5
    pos samX -49
    sleep(120)
    peCollectDark(900,"pe_dark_900s_07")
    peCollectData(900,filename="Anthracene_4mm_cap_samChanger_900s")
    #Sample 6
    pos samX -113.25
    sleep(120)
    peCollectDark(900,"pe_dark_900s_08")
    peCollectData(900,filename="C60_4mm_cap_samChanger_900s")
    #Sample 7
    pos samX -42
    sleep(120)
    peCollectDark(900,"pe_dark_900s_09")
    peCollectData(900,filename="FusedQuartzRod_2mm_samChanger_900s")
    
    peCollectDark(900,"pe_dark_900s_01")
    peCollectData(900,filename="CeO2_NIST_1mm_cap_spinner_900s")
    
    peCollectDark(900,"pe_dark_900s_02")
    peCollectData(900,filename="Si_NIST_1mm_cap_spinner_900s")
    """
    
    posCeO2NIST = -56.5
    posCeO2nano = -68.3
    posNi = -82.7
    posEmptyCap = -94.3
    posEmptyXPDF = -88.0
    
    print "Sample-to-detector at 192 mm"
    wideSlits()
    peCollectDark(900,"pe_dark_900s_03")
    pos samX posEmptyXPDF
    peCollectData(900,filename="Empty_XPDF_Changer_stod192_wide_900s")
    sleep(60)
    pos samX posEmptyCap
    peCollectData(900,filename="Empty_1mmCap_Changer_stod192_wide_900s")
    sleep(60)
    pos samX posNi
    peCollectData(900,filename="Ni_1mmCap_Changer_stod192_wide_900s")
    sleep(120)
    pos samX posCeO2NIST
    peCollectData(900,filename="CeO2_NIST_1mmCap_Changer_stod192_wide_900s")
    sleep(120)
    pos samX posCeO2nano
    peCollectData(900,filename="CeO2_nano_1mmCap_Changer_stod192_wide_900s")
    
    narrowSlits()
    peCollectDark(900,"pe_dark_900s_04")
    pos samX posEmptyXPDF
    peCollectData(900,filename="Empty_XPDF_Changer_stod192_narrow_900s")
    sleep(60)
    pos samX posEmptyCap
    peCollectData(900,filename="Empty_1mmCap_Changer_stod192_narrow_900s")
    sleep(60)
    pos samX posNi
    peCollectData(900,filename="Ni_1mmCap_Changer_stod192_narrow_900s")
    sleep(120)
    pos samX posCeO2NIST
    peCollectData(900,filename="CeO2_NIST_1mmCap_Changer_stod192_narrow_900s")
    sleep(120)
    pos samX posCeO2nano
    peCollectData(900,filename="CeO2_nano_1mmCap_Changer_stod192_narrow_900s")
    
    print "Sample-to-detector at 242 mm"
    pos det1Z 240
    sleep(60)
    wideSlits()
    peCollectDark(900,"pe_dark_900s_05")
    pos samX posEmptyXPDF
    peCollectData(900,filename="Empty_XPDF_Changer_stod242_wide_900s")
    sleep(60)
    pos samX posEmptyCap
    peCollectData(900,filename="Empty_1mmCap_Changer_stod242_wide_900s")
    sleep(60)
    pos samX posNi
    peCollectData(900,filename="Ni_1mmCap_Changer_stod242_wide_900s")
    sleep(120)
    pos samX posCeO2NIST
    peCollectData(900,filename="CeO2_NIST_1mmCap_Changer_stod242_wide_900s")
    sleep(120)
    pos samX posCeO2nano
    peCollectData(900,filename="CeO2_nano_1mmCap_Changer_stod242_wide_900s")
    
    narrowSlits()
    peCollectDark(900,"pe_dark_900s_06")
    pos samX posEmptyXPDF
    peCollectData(900,filename="Empty_XPDF_Changer_stod242_narrow_900s")
    sleep(60)
    pos samX posEmptyCap
    peCollectData(900,filename="Empty_1mmCap_Changer_stod242_narrow_900s")
    sleep(60)
    pos samX posNi
    peCollectData(900,filename="Ni_1mmCap_Changer_stod242_narrow_900s")
    sleep(120)
    pos samX posCeO2NIST
    peCollectData(900,filename="CeO2_NIST_1mmCap_Changer_stod242_narrow_900s")
    sleep(120)
    pos samX posCeO2nano
    peCollectData(900,filename="CeO2_nano_1mmCap_Changer_stod242_narrow_900s")
    
    print "Sample-to-detector at 292 mm"
    pos det1Z 290
    sleep(60)
    wideSlits()
    peCollectDark(900,"pe_dark_900s_07")
    pos samX posEmptyXPDF
    peCollectData(900,filename="Empty_XPDF_Changer_stod292_wide_900s")
    sleep(60)
    pos samX posEmptyCap
    peCollectData(900,filename="Empty_1mmCap_Changer_stod292_wide_900s")
    sleep(60)
    pos samX posNi
    peCollectData(900,filename="Ni_1mmCap_Changer_stod292_wide_900s")
    sleep(120)
    pos samX posCeO2NIST
    peCollectData(900,filename="CeO2_NIST_1mmCap_Changer_stod292_wide_900s")
    sleep(120)
    pos samX posCeO2nano
    peCollectData(900,filename="CeO2_nano_1mmCap_Changer_stod292_wide_900s")
    
    narrowSlits()
    peCollectDark(900,"pe_dark_900s_08")
    pos samX posEmptyXPDF
    peCollectData(900,filename="Empty_XPDF_Changer_stod292_narrow_900s")
    sleep(60)
    pos samX posEmptyCap
    peCollectData(900,filename="Empty_1mmCap_Changer_stod292_narrow_900s")
    sleep(60)
    pos samX posNi
    peCollectData(900,filename="Ni_1mmCap_Changer_stod292_narrow_900s")
    sleep(120)
    pos samX posCeO2NIST
    peCollectData(900,filename="CeO2_NIST_1mmCap_Changer_stod292_narrow_900s")
    sleep(120)
    pos samX posCeO2nano
    peCollectData(900,filename="CeO2_nano_1mmCap_Changer_stod292_narrow_900s")
    
    print "collectPhil() finished!"

def collectStefan():
    posSam1 = -40.25
    posSam2 = -51
    posSam3 = -60.25
    posSam4 = -68.75
    posSam5 = -77.75
    posSam6 = -86.5
    posSam7 = -94.5
    posSam8 = -105.0
    posSam9 = -112.75
    posSam10 = --120.0
    posSam11 = -128.0
    #posSam12 = 0
    
    collectTime = 300
    waitTime = 180
    
    pos samX posSam1
    pos samY -49.35
    peCollectData(collectTime,filename="Gd25Dy20Ho20Al20Co15")
    sleep(waitTime)
    
    pos samX posSam2
    pos samY -49.85
    peCollectData(collectTime,filename="Gd20Dy20Ho20Al10Si10Co20")
    sleep(waitTime)
    
    pos samX posSam3
    peCollectData(collectTime,filename="Gd20Dy20Ho20Al20Co10Fe10")
    sleep(waitTime)
    
    pos samX posSam4
    peCollectData(collectTime,filename="Gd30Dy20Ho20Al15Co15")
    sleep(waitTime)
    
    pos samX posSam5
    peCollectData(collectTime,filename="Gd20Dy20Ho20Al20Co20")
    sleep(waitTime)
    
    pos samX posSam6
    peCollectData(collectTime,filename="Fe57Ta43")
    sleep(waitTime)
    
    pos samX posSam7
    peCollectData(collectTime,filename="Ni62Ta38")
    sleep(waitTime)
    
    pos samX posSam8
    peCollectData(collectTime,filename="Fe34Hf66")
    sleep(waitTime)
    
    pos samX posSam9
    peCollectData(collectTime,filename="Cu64Hf36_ribbon")
    sleep(waitTime)
    
    pos samX posSam10
    peCollectData(collectTime,filename="Cu59Hf41_ribbon")
    sleep(waitTime)
    
    pos samX posSam11
    peCollectData(collectTime,filename="Cu60Hf30ti10_ribbon")
    sleep(waitTime) 

def collectStefan2():
    pos samX -53
    peCollectData(300,filename="Empty_samChanger_300s")
    sleep(60)
    pos samX -46
    pos samY -50.6
    peCollectData(300,filename="Ni-Nb-Ta")
    sleep(120)
    pos samX -70
    peCollectData(300,filename="CeO2_NIST_300s")

def collectPhoebe():
    collectTime = 3600
    collectDarkTime = 1200
    waitTime = 600
    
    posSam0X = -133.0 #Empty XPDF
    posSam1X = -127.5 #Empty 2mm cap
    posSam2X = -122.25 #Pristine
    posSam3X = -116.25 #300
    posSam4X = -110.5 #180
    posSam5X = -105.0 #5
    posSam6X = -100.0 #CeO2 2mm Cap
    posSam7X = -78.5 #C in cell
    posSam8X = -64.25 #Empty cell
    posSam9X = -49.25 #CeO2 in cell
    
    peCollectDark(collectDarkTime,filename="pe_Dark_00_"+str(collectTime)+"s")
    pos samX posSam0X 
    peCollectData(collectTime,filename="Empty_XPDF_samChanger_"+str(collectTime)+"s")
    sleep(waitTime)
    
    peCollectDark(collectDarkTime,filename="pe_Dark_01_"+str(collectTime)+"s")
    pos samX posSam1X 
    peCollectData(collectTime,filename="Empty_2mmCap_samChanger_"+str(collectTime)+"s")
    sleep(waitTime)
    
    peCollectDark(collectDarkTime,filename="pe_Dark_02_"+str(collectTime)+"s")
    pos samX posSam2X 
    peCollectData(collectTime,filename="Pristine_hardC_2mmCap_samChanger_"+str(collectTime)+"s")
    sleep(waitTime)
    
    peCollectDark(collectDarkTime,filename="pe_Dark_03_"+str(collectTime)+"s")
    pos samX posSam3X 
    peCollectData(collectTime,filename="HardC_300mV_2mmCap_samChanger_"+str(collectTime)+"s")
    sleep(waitTime)
    
    peCollectDark(collectDarkTime,filename="pe_Dark_04_"+str(collectTime)+"s")
    pos samX posSam4X 
    peCollectData(collectTime,filename="HardC_180mV_2mmCap_samChanger_"+str(collectTime)+"s")
    sleep(waitTime)
    
    peCollectDark(collectDarkTime,filename="pe_Dark_05_"+str(collectTime)+"s")
    pos samX posSam5X 
    peCollectData(collectTime,filename="HardC_5mV_2mmCap_samChanger_"+str(collectTime)+"s")
    sleep(waitTime)
    
    peCollectDark(collectDarkTime,filename="pe_Dark_07_"+str(collectTime)+"s")
    pos samX posSam7X 
    peCollectData(collectTime,filename="HardC_inPFAHourglassCell_samChanger_"+str(collectTime)+"s")
    sleep(waitTime)
    
    peCollectDark(collectDarkTime,filename="pe_Dark_08_"+str(collectTime)+"s")
    pos samX posSam8X 
    peCollectData(collectTime,filename="Empty_PFAHourglassCell_samChanger_"+str(collectTime)+"s")
    sleep(waitTime)
    
    peCollectDark(collectDarkTime,filename="pe_Dark_09_"+str(collectTime)+"s")
    pos samX posSam9X 
    peCollectData(collectTime,filename="CeO2_NIST_inPFAHourglassCell_samChanger_"+str(collectTime)+"s")
    sleep(1200)
    
    peCollectDark(collectDarkTime,filename="pe_Dark_06_"+str(collectTime)+"s")
    pos samX posSam6X 
    peCollectData(collectTime,filename="CeO2_2mmCap_samChanger_"+str(collectTime)+"s")

def collect190515():
    collectTime = 3600
    collectDarkTime = 2400
    waitTime = 600
    
    posSam0X = -91.75 #Empty XPDF
    posSam1X = -43.0 #Empty capillary
    
    posSam2X = -82.5 #dolomite
    posSam3X = -72.0 #Aspirin Sainsbury's
    posSam4X = -61.5 #Aspirin Pure
    posSam5X = -52.0 #Anthracene
    
    
    peCollectDark(collectDarkTime,filename="pe_Dark_00_"+str(collectTime)+"s")
    pos samX posSam0X 
    peCollectData(collectTime,filename="Empty_XPDF_samChanger_"+str(collectTime)+"s")
    sleep(waitTime)
    
    peCollectDark(collectDarkTime,filename="pe_Dark_01_"+str(collectTime)+"s")
    pos samX posSam1X 
    peCollectData(collectTime,filename="Empty_4mmCap_samChanger_"+str(collectTime)+"s")
    sleep(waitTime)
    
    peCollectDark(collectDarkTime,filename="pe_Dark_02_"+str(collectTime)+"s")
    pos samX posSam2X 
    peCollectData(collectTime,filename="Dolomite_4mmCap_samChanger_"+str(collectTime)+"s")
    sleep(waitTime)
    
    peCollectDark(collectDarkTime,filename="pe_Dark_03_"+str(collectTime)+"s")
    pos samX posSam3X 
    peCollectData(collectTime,filename="Aspirin_Tablet_4mmCap_samChanger_"+str(collectTime)+"s")
    sleep(waitTime)
    
    peCollectDark(collectDarkTime,filename="pe_Dark_04_"+str(collectTime)+"s")
    pos samX posSam4X 
    peCollectData(collectTime,filename="Aspirin_Pure_4mmCap_samChanger_"+str(collectTime)+"s")
    sleep(waitTime)
    
    peCollectDark(collectDarkTime,filename="pe_Dark_05_"+str(collectTime)+"s")
    pos samX posSam5X 
    peCollectData(collectTime,filename="Anthracene_4mmCap_samChanger_"+str(collectTime)+"s")
    #sleep(waitTime)

def collect200515():
    #pos samX -94.75 
    #peCollectData(180,filename="Si_NIST_4mmCap_samChanger_StoD240mm_180s")
    peCollectDark(600,filename="pe_Dark_StoD240mm_01_600s")
    pos samX -77.25
    peCollectData(600,filename="Empty_XPDF_samChanger_StoD240mm_720s")
    pos samX -43.0
    peCollectData(600,filename="Empty_4mmCap_samChanger_StoD240mm_720s")
    pos samX -61.5
    peCollectData(600,filename="Aspirin_Pure_4mmCap_samChanger_StoD240mm_720s")
    pos samX -72.0
    peCollectData(600,filename="Aspirin_Tablet_4mmCap_samChanger_StoD240mm_720s")
    sleep(600)
    peCollectDark(600,filename="pe_Dark_StoD240mm_02_600s")

def wideSlits():
    print "opening slits to wide beam"
    pos s3gapX 0.5 s3gapY 0.5
    pos s4gapX 0.7 s4gapY 0.7
    pos s5gapX 0.7 s5gapY 0.7
    
def narrowSlits():
    print "narrowing slits to narrow beam"
    pos s3gapX 0.2 s3gapY 0.2
    pos s4gapX 0.4 s4gapY 0.4
    pos s5gapX 0.4 s5gapY 0.4
    
    
def lunchtime(fn):
#     sleep(10*60)
    peCollectDark(25*60)
    peCollectData(25*60,fn)
    
def pzt():
    sleep(60*60)
    spinOn
    eh3open
    peCollectDark(2*60*60)
    peCollectData(2*60*60,"PZT93to7_360x20s")
    eh3close
    spinOff
    scan x 1 100000 1 w 20 pe1Proc5statMean
    
def twoHourMegaCollection():
    peCollectDark(360*20,"Dark_2hours",repeats=360)
    peCollectData(360*20,"K2PdCl6(Alfa)_framebyframe_2h",repeats=360)
    
def collectDarkStabilityTests():
    #peSetDetector(10)
    caput("BL15J-NT-POWER-01:3:CONTROL","1") #Turn on PE fans just before starting this
    for i in range(0,1000):
        peCollectData(60,filename="Dark_60s_"+str(i))
        sleep(520)
    
def collect010816_01():
    peCollectData(300,"002_CrystalMazeCrystal_75x4s")
    peMonitorStability(preWait=8)
    
print "pe_test_script loaded"