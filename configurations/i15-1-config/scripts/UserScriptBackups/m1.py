from gda.jython.commands.InputCommands import requestInput as raw_input
from time import sleep

#Values are a,b,c in V = aq^2 + bq + c. It take a q value calculated by JS. Now depricated by m1PRFsamZ.
m1PRFs = {"CH0": [130.8410,-1687.18,5356.20],
          "CH1": [93.2386 ,-1238.21,4405.44],
          "CH2": [111.4230,-1457.76,4609.96],
          "CH3": [112.3190,-1461.81,4199.03],
          "CH4": [135.4870,-1747.69,4840.90],
          "CH5": [151.7130,-1944.39,5352.55],
          "CH6": [141.5100,-1802.38,4680.99],
          "CH7": [149.5430,-1886.10,4732.70],
          "CH8": [170.7330,-2138.85,5264.08],
          "CH9": [197.2700,-2458.16,6158.51],
          "CH10":[182.4970,-2256.74,5771.38],
          "CH11":[206.1550,-2528.73,6751.38],
          "CH12":[215.2540,-2621.57,7275.23],
          "CH13":[226.2660,-2735.24,7743.47],
          "CH14":[250.4790,-3003.14,8749.04],
          "CH15":[240.3350,-2880.27,8574.47]}

#Values are a,b,c in V = az^2 + bz + c, where z is the desired focal distance from the centre of SAM (samZ = 0).
m1PRFsamZ = {"CH0": [0.00039701,-1.0693, 853.732],
             "CH1": [0.00029303,-0.8193,1061.800],
             "CH2": [0.00034400,-0.9441, 696.771],
             "CH3": [0.00034461,-0.9394, 283.248],
             "CH4": [0.00041128,-1.1083, 176.296],
             "CH5": [0.00045698,-1.2209, 176.745],
            "CH6": [0.00042308,-1.1208,-104.410],
             "CH7": [0.00044186,-1.1548,-254.372],
             "CH8": [0.00050038,-1.2953,-375.056],
             "CH9": [0.00057446,-1.4757,-307.699],
             "CH10":[0.00052656,-1.3376,-145.354],
             "CH11":[0.00058902,-1.4782, 145.014],
             "CH12":[0.00060973,-1.5135, 447.918],
             "CH13":[0.00063517,-1.5583, 643.825],
             "CH14":[0.00069615,-1.6856, 982.990],
             "CH15":[0.00066761,-1.6153,1127.630]}

m1valsSESO = {"CH0":1108,
        "CH1":1415,
        "CH2":961.5,
        "CH3":499.0,
        "CH4":221.0,
        "CH5":51.5,
        "CH6":-85.2,
        "CH7":-205.2,
        "CH8":-265.6,
        "CH9":-200.0,
        "CH10":20.0,
        "CH11":362.0,
        "CH12":734.2,
        "CH13":1032,
        "CH14":1236,
        "CH15":1574}

m1valsDLS = {"CH0":1500,
        "CH1":1026.3,
        "CH2":668.9,
        "CH3":277.9,
        "CH4":76.5,
        "CH5":2.4,
        "CH6":-221.7,
        "CH7":-319.7,
        "CH8":-435.7,
        "CH9":-387.4,
        "CH10":-84.2,
        "CH11":-3.1,
        "CH12":257.7,
        "CH13":750.,
        "CH14":700.,
        "CH15":1150.}

#Vs from SA, modified by +Vs from JS in I15-1_MlVFM_XRAYINSP_SEP16  
m1valsDLS_plus311ReflOffset = {"CH0":1500.,
                               "CH1":1201.6,
                               "CH2":868.4,
                               "CH3":445.,
                               "CH4":312.2,
                               "CH5":196.6,
                               "CH6":-19.6,
                               "CH7":-123.8,
                               "CH8":-244.8,
                               "CH9":-153.5,
                               "CH10":102.6,
                               "CH11":193.2,
                               "CH12":464.8,
                               "CH13":928.7,
                               "CH14":887.6,
                               "CH15":1387.}

#Vs from SA, modified by -Vs from JS in I15-1_MlVFM_XRAYINSP_SEP16
m1valsDLS_minus311ReflOffset = {"CH0":1274,
                                "CH1":851,
                                "CH2":469.4,
                                "CH3":110.8,
                                "CH4":-159.2,
                                "CH5":-191.8,
                                "CH6":-423.8,
                                "CH7":-515.6,
                                "CH8":-626.6,
                                "CH9":-621.3,
                                "CH10":-271,
                                "CH11":-199.4,
                                "CH12":61,
                                "CH13":560,
                                "CH14":512.4,
                                "CH15":896.1}

#Vs from SA, modified by -Vs from JS in \\diamproject01\diamond$\Science\I15-1_XPDF\Beamline components\Mirror\Optic Commissioning\September2016\MLM_scale_factor_for_John_Sutters_Voltage_corrections_311.xlsx
m1valsDLS_minus311ReflOffset_Times1p33 = {"CH0":1199.4,
                                "CH1":793.2,
                                "CH2":403.6,
                                "CH3":55.7,
                                "CH4":-237,
                                "CH5":-255.9,
                                "CH6":-490.5,
                                "CH7":-580.2,
                                "CH8":-689.6,
                                "CH9":-698.5,
                                "CH10":-332.6,
                                "CH11":-264.2,
                                "CH12":-2.2,
                                "CH13":496.8,
                                "CH14":450.5,
                                "CH15":812.3}

m1valsJSq3p867 = {"CH0":788.2,
                  "CH1":1011.4,
                  "CH2":638.8,
                  "CH3":225.6,
                  "CH4":108.4,
                  "CH5":102.0,
                  "CH6":-173.0,
                  "CH7":-324.9,
                  "CH8":-454.1,
                  "CH9":-397.7,
                  "CH10":-226.8,
                  "CH11":-55.1,
                  "CH12":356.0,
                  "CH13":549.3,
                  "CH14":880.9,
                  "CH15":1029.8}

m1valsTest = {"CH0":3,
        "CH1":6,
        "CH2":9,
        "CH3":12,
        "CH4":15,
        "CH5":18,
        "CH6":21,
        "CH7":24,
        "CH8":27,
        "CH9":30,
        "CH10":33,
        "CH11":36,
        "CH12":39,
        "CH13":42,
        "CH14":45,
        "CH15":48}

m1valsOff = {"CH0":0,
        "CH1":0,
        "CH2":0,
        "CH3":0,
        "CH4":0,
        "CH5":0,
        "CH6":0,
        "CH7":0,
        "CH8":0,
        "CH9":0,
        "CH10":0,
        "CH11":0,
        "CH12":0,
        "CH13":0,
        "CH14":0,
        "CH15":0}

m1valsZero = m1valsOff

#X, Pitch, Roll, Yaw
m1stripes = {"311":[  0.0,-4.222,5.502,0.],
             "220":[ 11.0,-4.222,5.502,0.],
             "111":[-11.0,-4.222,5.502,0.]}

def m1Initialise():
    """Initialises the HV-ADAPTOS power supply for the bimorph mirror, m1.
    
    All 16 channels will be set to 0 V and enabled (Status = ON)."""
    print "This will initialise the m1 bimorph and allow the piezos to operate at voltage."
    print "All of the voltages will initially be set to zero."
    print "Make sure that the mirror is in a safe state to do so (at vacuum, etc.)."
    yes = raw_input("Are you sure you want to continue?")
    if yes not in ("y","Y","yes","Yes","YES","yep","of course"):
        print "Stopping m1Initialise, as per your request."
        return
    print "Continuing m1Initialise, as per your request."
    #caput("BL15J-OP-MIRR-01:PSU:GROUP0:MODE","NORMAL") #Old firmware version
    caput("BL15J-OP-MIRR-01:PSU:GROUP0:MODE","FAST") #After firmware update, 26/09/2016
    waitFor("BL15J-OP-MIRR-01:PSU:BUSY",0,checkTime=.1,timeOut=20)
    m1SetTarget(m1valsZero)
    caput("BL15J-OP-MIRR-01:PSU:GROUP0:VOUT",0)
    waitFor("BL15J-OP-MIRR-01:PSU:BUSY",0,checkTime=1,timeOut=30)
    for ch in m1prfs.keys(): #Check that all channels are at zero V
        setV = caget("BL15J-OP-MIRR-01:PSU:GROUP0:"+ch+":VTRGT")
        if float(setV) != 0:
            print "Channel "+str(ch)+" was found at a non-zero voltage. Aborting m1Initialise! Check m1!"
            return
    if caget("BL15J-OP-MIRR-01:PSU:GROUP0:LASTERROR") == "0":
        print "No errors detected. Enabling m1..."
    caput("BL15J-OP-MIRR-01:PSU:GROUP0:ALLON",1)
    waitFor("BL15J-OP-MIRR-01:PSU:BUSY",0,checkTime=1,timeOut=60)
    for ch in m1prfs.keys(): #Check that all channels have a status of ON
        if caget("BL15J-OP-MIRR-01:PSU:GROUP0:"+ch+":STATUS") != "1":
            print "Channel "+str(ch)+" was found with a non-ON status. Aborting m1Initialise! Check m1!"
            return # this should be an exception! 
        
    if caget("BL15J-OP-MIRR-01:PSU:GROUP0:LASTERROR") == "0":
        print "m1Initialise complete!"
    else:
        print "An error was seen on completion of m1Initialise. Check m1!"
alias m1Initialise

def m1Off():
    """Turns off the HV-ADAPTOS power supply for the bimorph mirror, m1."""
    print "Turning off the m1 bimorph..."
    caput("BL15J-OP-MIRR-01:PSU:GROUP0:ALLOFF",1)
    waitFor("BL15J-OP-MIRR-01:PSU:BUSY",0,checkTime=1,timeOut=60)
    m1SetTarget(m1valsZero)
    for ch in m1prfs.keys(): #Check that all channels have a status of OFF
        if caget("BL15J-OP-MIRR-01:PSU:GROUP0:"+ch+":STATUS") != "0":
            print "Channel "+str(ch)+" was found with a non-OFF status. Check m1!"
            return
    if caget("BL15J-OP-MIRR-01:PSU:GROUP0:LASTERROR") == "0":
        print "m1Off complete!"
    else:
        print "An error was seen on completion of m1Off. Check m1!"
alias m1Off

def m1SetTarget(vals):
    """Sets target voltages for each channel of the bimorph mirror, m1.
    
    This function either takes a pre-defined parameter set (e.g. m1valsOff)
    or a numeric value equal to the desired focus value of the mirror (relative to centre of sam)."""
    if vals >= 0.0 and vals <= 1500.0: #Sample-to-focus distance in mm (samZ)
        print "Setting m1 to focus at samZ of "+str(vals)+" mm"
        valsSet = {}
        for ch in m1PRFsamZ:
            v = m1PRFsamZ[ch][0] * float(vals)**2 + m1PRFsamZ[ch][1] * float(vals) + m1PRFsamZ[ch][2]
            valsSet[ch] = v
            caput("BL15J-OP-MIRR-01:PSU:GROUP0:"+ch+":VTRGT",v)
            waitFor("BL15J-OP-MIRR-01:PSU:BUSY",0,checkTime=.1,timeOut=20)
            #print str(ch) + ": "+str(v)
        print "...m1 target voltages set; " + str(valsSet)
    else:
        try:
            print "Setting m1 target voltages to preset values..."
            for ch in vals:
                #print str(ch) + ": "+str(vals[ch])
                caput("BL15J-OP-MIRR-01:PSU:GROUP0:"+ch+":VTRGT",vals[ch])
                waitFor("BL15J-OP-MIRR-01:PSU:BUSY",0,checkTime=.1,timeOut=20)
            print "...m1 target voltages set; " + str(vals)
        except:
            print "m1SetTarget only accepts samZ values in the range of 0.0 to 1500 m"
            print "   or a value dictionary like m1valsOff or m1valsTest"

def m1ApplyTarget():
    """Applies the target voltages to each channel of the bimorph mirror, m1."""
    print str(time.strftime("%Y-%m-%d %H:%M"))+" Applying m1 target voltages. This takes about 15 mins, so go get a cuppa."
    caput("BL15J-OP-MIRR-01:PSU:GROUP0:TARGET",1)
    waitFor("BL15J-OP-MIRR-01:PSU:BUSY",0,checkTime=10,timeOut=1200)
    print str(time.strftime("%Y-%m-%d %H:%M"))+" m1ApplyTarget complete!"
alias m1ApplyTarget

def m1RecoverFromTrip():
    """Used to recover in case of an E-Trip"""
    caput("BL15J-OP-MIRR-01:PSU:GROUP0:RESETERROR",1)
    waitFor("BL15J-OP-MIRR-01:PSU:BUSY",0,checkTime=1,timeOut=60)
    caput("BL15J-OP-MIRR-01:PSU:GROUP0:ALLON",1)
    waitFor("BL15J-OP-MIRR-01:PSU:BUSY",0,checkTime=1,timeOut=60)
    m1ApplyTarget

def m1Out():
    """Moves m1 downwards to its out-of-beam position."""
    outPosition = -6.5
    print "Moving m1 out"
    pos m1Y outPosition
    if abs(m1Y.getPosition()-outPosition) < (m1Y.getDemandPositionTolerance()*1.01):
        print "m1Out complete!"
    else:
        raise NameError("m1 has not reached its out position ("+str(outPosition)+" mm). Check m1!")
alias m1Out

def m1In(stripe=""):
    print "Moving m1 in"
    pos m1Y 0
    if stripe != "":
        try:
            print "Selecting stripe %s" %stripe
            print "   X: "+str(m1stripes[stripe][0])+", Pitch: "+str(m1stripes[stripe][1])+", Roll: "+str(m1stripes[stripe][2])+", Yaw: "+str(m1stripes[stripe][3])
            pos m1X m1stripes[stripe][0]
            pos m1Pitch m1stripes[stripe][1]
            pos m1Roll m1stripes[stripe][2]
            pos m1Yaw m1stripes[stripe][3] 
        except:
            print "Stripe not recognised! Only 311, 220 or 111 available"
            return
    print "m1In complete!"

def m1MeasurePRFs():
    #m1Initialise
    print "Measuring PRF with all CHs set to 0 V..."
    m1MeasureSlopeError
    for i in range(16):
        print "Setting CH"+str(i)+" to 400 V..."
        caput("BL15J-OP-MIRR-01:PSU:GROUP0:CH"+str(i)+":VOUT",400)
        waitFor("BL15J-OP-MIRR-01:PSU:BUSY",0,checkTime=10,timeOut=1200)
        print "Waiting to settle for 20 mins..."
        sleep(1200)
        print "Measuring PRF with CH"+str(i)+" set to 400 V..."
        m1MeasureSlopeError
    print "m1MeasurePRFs complete!"
alias m1MeasurePRFs

def m1MeasureQuadruplePRFs():
    #m1Initialise #DONE
    #m1SetTarget(m1valsOff) #DONE
    #m1ApplyTarget #DONE
    print "Waiting to settle for 30 mins..."
    sleep(1800)
    print "Measuring with all CHs set to 0 V..."
    m1MeasureSlopeError
    for i in range(4):
        m1SetTarget(m1valsOff)
        print "Setting CH"+str(i)+", CH"+str(i+4)+", CH"+str(i+8)+" and CH"+str(i+12)+" to 400 V..."
        caput("BL15J-OP-MIRR-01:PSU:GROUP0:CH"+str(i)+":VTRGT",400)
        waitFor("BL15J-OP-MIRR-01:PSU:BUSY",0,checkTime=.1,timeOut=20)
        caput("BL15J-OP-MIRR-01:PSU:GROUP0:CH"+str(i+4)+":VTRGT",400)
        waitFor("BL15J-OP-MIRR-01:PSU:BUSY",0,checkTime=.1,timeOut=20)
        caput("BL15J-OP-MIRR-01:PSU:GROUP0:CH"+str(i+8)+":VTRGT",400)
        waitFor("BL15J-OP-MIRR-01:PSU:BUSY",0,checkTime=.1,timeOut=20)
        caput("BL15J-OP-MIRR-01:PSU:GROUP0:CH"+str(i+12)+":VTRGT",400)
        waitFor("BL15J-OP-MIRR-01:PSU:BUSY",0,checkTime=.1,timeOut=20)
        m1ApplyTarget
        print "Waiting to settle for 30 mins..."
        sleep(1800)
        print "Measuring PRF with CH"+str(i)+", CH"+str(i+4)+", CH"+str(i+8)+" and CH"+str(i+12)+" set to 400 V..."
        m1MeasureSlopeError
    print "Turning off bimorph..."
    m1SetTarget(m1valsOff)
    m1ApplyTarget
    print "m1MeasureQuadruplePRFs complete!"
alias m1MeasureQuadruplePRFs

def m1MeasureSlopeError():
    pos s2gapY 0.020
    #scan s2cenY -2.275 2.075 0.025 eyepyCenY #Eye placed at focal spot
    scan s2cenY -2.375 2.175 0.025 eyepyCenY
alias m1MeasureSlopeError

def m1MeasureSlopeOverMirror():
    #print str(time.strftime("%Y-%m-%d %H:%M"))+" Waiting 30 mins, then starting measurement..."
    #sleep(1800)
    print "Measuring centre of stripe..."
    m1MeasureSlopeError
    inc m1X 2
    print "Measuring 2 mm inboard of stripe centre..."
    m1MeasureSlopeError
    inc m1X -4
    print "Measuring 2 mm outboard of stripe centre..."
    m1MeasureSlopeError
    print "m1MeasureSlopeOverMirror complete!"
alias m1MeasureSlopeOverMirror

def m1MeasureReflectivity():
    # define the calibrated diode
    # d4 = DisplayEpicsPVClass("d4", "BL15J-EA-ADC-01:STAT8:MeanValue_RBV", "volts", "%.5f")
    
    #pos railPitch 0
    #scan s2cenY -2.375 2.175 0.025
    #pos railPitch 0.48380
    
    # useful part of the mirror is from -2.25 in s2cenY to 2.05. This gives a range of 4.3
    # if we want 21 steps, we need steps of 0.215 (exactly). 
    
    # these were measured using "scan s2cenY -2.25 2.05 0.215 w .1 d2 d4 d4_over_ringCurrent" 
    #direct_beams = [6.27667,6.67596,7.00366,7.4229,7.69447,7.99504,8.19912,8.40787,8.5249,8.60699,8.64449,8.62396,8.53074,8.34944,8.1782,7.92735,7.6793,7.26296,6.98057,6.56815,6.11697]
    
    # set the slit position array
    s2cenY_array = dnp.linspace(-2.25,2.05,21)
    
    # set the slit size
    pos s2gapY 0.2
     
    for i,s2cenY_value in enumerate(s2cenY_array):
        pos s2cenY s2cenY_value
        # this was the original scan:::      cscan m1Pitch 0.1 0.01 w 0.1 d2
        # do a pitch scan
        print "THE FOLLOWING SCAN IS FOR s2gapY %1.4f" % s2cenY_value
        scan m1Pitch -4.0 -4.45 0.002 w .1 d2 d4 d4_over_ringCurrent
        
def m1MeasureReflectivityOvernight():
    m1MeasureReflectivity()
    m1Initialise
    m1SetTarget('m1valsDLS')
    m1ApplyTarget
    sleep(60*30)
    print "THE FOLLOWINGF SCANS AR£E WITH THE MIRROR TURNED ON"
    
    m1MeasureReflectivity()
    pos m1X -13
    m1MeasureReflectivity()
    pos m1X -9
    m1MeasureReflectivity()
    
#     s1close
#     m1SetTarget('m1valsOff')
#     m1ApplyTarget

    
    
    
def measureReflectivityVertical(mirror_x, y_min=-2.25, y_max=2.05, y_num=21, p_min=-4.45, p_max=-4.0, p_step=0.002):
    # measures rocking curves for reflectivity as a function of Y.
    # Performs a rocking curve (defined by the inputs p_min/max/step) at various points
    # along Y (defined by y_min/max/num) at a single point in mirror_x and stores the result.
    from gda.data import NumTracker
    
    #position the mirror
    pos m1X mirror_x
    
    # position the slits
    #pos s2gapY 0.20 #or something else small
    
    # Generate the points
    s2cenY_array = dnp.linspace(y_min,y_max,y_num)
    
    # drop the anchor    
    print "This is the start of a Vertical rocking curve scan. Boomerang."
    f = open('/dls/i15-1/data/2016/cm14470-4/refl_scans_311_opimised.txt','a+')
    f.write('This is the start of a Vertical rocking curve scan'+'\n')
    f.close()
    
    # Do the loop
    for i,s2cenY_value in enumerate(s2cenY_array):
        pos s2cenY s2cenY_value
        scan m1Pitch p_min p_max p_step w .1 d2 d4 d4_over_ringCurrent
        text_string = 'Scan # %i, s2cenY = %1.5f, m1X of %3.5f . The peak (%2.3f) was at a pitch of %2.5f . Boomerang.' % (NumTracker("i15-1").getCurrentFileNumber(), s2cenY.getPosition(), m1X.getPosition(), maxval.result.maxval, peak.result.pos) 
        print text_string
        f = open('/dls/i15-1/data/2016/cm14470-4/refl_scans_311_opimised.txt','a+')
        f.write(text_string+'\n')
        f.close()
    
def measureReflectivityHorizontal(s2cenY_val, x_min=-16, x_max=-6, x_num=21, p_min=-4.45, p_max=-4.0, p_step=0.002):
    # measures rocking curves for reflectivity as a function of X.
    # Performs a rocking curve (defined by the inputs p_min/max/step) at various points
    # along X (defined by x_min/max/num) (by moving the mirror) at a single point in s2cenY 
    # and stores the result.
    from gda.data import NumTracker
    
    #position the slits
    pos s2cenY s2cenY_val
    
    # position the slits
    #pos s2gapY 0.20 #or something else small
    
    # Generate the points
    m1X_array = dnp.linspace(x_min,x_max,x_num)
    
    # drop the anchor    
    print "This is the start of a Horizontal rocking curve scan. Boomerang."
    f = open('/dls/i15-1/data/2016/cm14470-3/refl_scans_311.txt','a+')
    f.write('This is the start of a Horizontal rocking curve scan'+'\n')
    f.close()
    
    # Do the loop
    for i,m1X_value in enumerate(m1X_array):
        pos m1X m1X_value
        scan m1Pitch p_min p_max p_step w .1 d2 d4 d4_over_ringCurrent
        text_string = 'Scan # %i, s2cenY = %1.5f, m1X of %3.5f . The peak (%2.3f) was at a pitch of %2.5f . Boomerang.' % (NumTracker("i15-1").getCurrentFileNumber(), s2cenY.getPosition(), m1X.getPosition(), maxval.result.maxval, peak.result.pos) 
        print text_string
        f = open('/dls/i15-1/data/2016/cm14470-3/refl_scans_311.txt','a+')
        f.write(text_string+'\n')
        f.close()

def measureMirrorSurface(stripe): #'111','220' or '311'
    #d4_over_ringCurrent = DisplayEpicsPVClass("d4_over_ringCurrent", "BL15J-EA-CALC-01.C", "volts", "%.5f")
    #d4 = DisplayEpicsPVClass("d4", "BL15J-EA-ADC-01:STAT8:MeanValue_RBV", "volts", "%.5f")
    #pos s1gapY 3.8
    #pos s1gapX 1.0
    #pos s2gapY 0.06 #111
    #pos s2gapX 0.30 #111
    #pos s2gapY 0.08 #311
    #pos s2gapX 0.40 #311
    #pos s2gapY 0.15 #220
    #pos s2gapX 0.5 #220
    #print "Moving mirror out..."
    #pos m1Y -8 railPitch 0
    #print "Scanning source intensity..."
    #ascan s2cenY -2.25 2.05 21 w .1 d2 d4 d4_over_ringCurrent # Scan1975 for 111, Scan2191 for 311
    #ascan s2cenY -2.25 2.05 21 w 1 d2 d4 d4_over_ringCurrent # Scan2192 for 311
    #ascan s2cenY -2.25 2.05 21 w 2 d2 d4 d4_over_ringCurrent # Scan2193 for 311
    #ascan s2cenY -2.25 2.05 21 w 4 d2 d4 d4_over_ringCurrent # Scan2194 for 311
    
    #ascan s2cenY -2.25 2.05 21 w 2 d2 d4 d4_over_ringCurrent # Scan2415 for 311
    #ascan s2cenY -2.25 2.05 21 w 2 d2 d4 d4_over_ringCurrent # Scan2416 for 311
    
    
    print "Moving mirror in..."
    pos m1Y 0 railPitch 0.48380
    for xpos in [m1stripes[stripe][0]-3,m1stripes[stripe][0],m1stripes[stripe][0]+3]:
        #measureReflectivityVertical(xpos, y_min=-2.25, y_max=2.05, y_num=21, p_min=-4.45, p_max=-4.0, p_step=0.003) #111
        #measureReflectivityVertical(xpos, y_min=-2.25, y_max=2.05, y_num=21, p_min=-4.35, p_max=-4.1, p_step=0.002) #311
        measureReflectivityVertical(xpos, y_min=-2.25, y_max=2.05, y_num=21, p_min=-4.4, p_max=-4.08, p_step=0.003) #220
    ypos_array = dnp.linspace(-2,2,7)
    for ypos in ypos_array:
        #measureReflectivityHorizontal(ypos, x_min=m1stripes[stripe][0]-5.5, x_max=m1stripes[stripe][0]+5.5, x_num=21, p_min=-4.45, p_max=-4.0, p_step=0.003) #111
        #measureReflectivityHorizontal(ypos, x_min=m1stripes[stripe][0]-5.5, x_max=m1stripes[stripe][0]+5.5, x_num=21, p_min=-4.35, p_max=-4.1, p_step=0.002) #311
        measureReflectivityHorizontal(ypos, x_min=m1stripes[stripe][0]-5.5, x_max=m1stripes[stripe][0]+5.5, x_num=21, p_min=-4.06, p_max=-4.08, p_step=0.003) #220
    print "measureMirrorSurface complete!!!!!"

def measureMirrorSurfaceRepeat(stripe):
    ypos_array = dnp.linspace(-2,2,7)
    for ypos in ypos_array:
        #measureReflectivityHorizontal(ypos, x_min=m1stripes[stripe][0]-5.5, x_max=m1stripes[stripe][0]+5.5, x_num=21, p_min=-4.45, p_max=-4.0, p_step=0.003) #111
        #measureReflectivityHorizontal(ypos, x_min=m1stripes[stripe][0]-5.5, x_max=m1stripes[stripe][0]+5.5, x_num=21, p_min=-4.35, p_max=-4.1, p_step=0.002) #311
        measureReflectivityHorizontal(ypos, x_min=m1stripes[stripe][0]-5.5, x_max=m1stripes[stripe][0]+5.5, x_num=21, p_min=-4.4, p_max=-4.08, p_step=0.003) #220

def measureMirrorSurfaceRepeatRestart(stripe):
    f = open('/dls/i15-1/data/2016/cm14470-3/refl_scans_311.txt','a+')
    f.write('This is the point that we restarted for I15 to change a crate'+'\n')
    f.close()
    
    # 2630 was the first one this morning
    # 2665 was the last complete point which is the 15th point of the second y position. 
    # want to start with the 16th point of the 2nd position.  
    # fingers crossed there won't be a gap in the scan number.... 
    
    ypos_array = dnp.linspace(-2,2,7)
    
    ypos = ypos_array[1]
    measureReflectivityHorizontal(ypos, x_min=m1stripes[stripe][0]+2.75, x_max=m1stripes[stripe][0]+5.5, x_num=6, p_min=-4.4, p_max=-4.08, p_step=0.003) #220
    for ypos in ypos_array[2:]:
        measureReflectivityHorizontal(ypos, x_min=m1stripes[stripe][0]-5.5, x_max=m1stripes[stripe][0]+5.5, x_num=21, p_min=-4.4, p_max=-4.08, p_step=0.003) #220

def measureMirrorSurfaceRepeatRestartAgain(stripe):
    f = open('/dls/i15-1/data/2016/cm14470-3/refl_scans_311.txt','a+')
    f.write('This is the point that we restarted for a beam dump'+'\n')
    f.close()
    
    ypos_array = dnp.linspace(-2,2,7)
    
    for ypos in ypos_array[2:]:
        measureReflectivityHorizontal(ypos, x_min=m1stripes[stripe][0]-5.5, x_max=m1stripes[stripe][0]+5.5, x_num=21, p_min=-4.4, p_max=-4.08, p_step=0.003) #220

def m1MeasureReflectivity_wholeOptic():
    scan m1Pitch -4.1 -4.35 0.002 w .1 d2 d4 d4_over_ringCurrent

def railPitchTests():
    # not technically a mirror test
    # &2q21 = 230
    # &2q22 = -2136.5
    
    #starts with the slits aligned, centred, and zeroed, rail pitch = 0, rail height = 230, mirrorY = -3
    
    #################################################################################
    ### STARTS WITH SCAN 2965 ### STARTS WITH SCAN 2965 ### STARTS WITH SCAN 2965 ###
    #################################################################################
    pos m1Y -3
    pos railY 230
    pos railPitch 0
    
    checkRailSlitAlignment(rail_position = 'down')
    
    for i in range (10):
        # move it up
        pos railPitch 0.4848 m1Y 0
        pos railY 230
        # do the scan
        checkRailSlitAlignment('up')
        # move it dwon
        pos railPitch 0.0 m1Y -3
        pos railY 230
        # do the scan
        checkRailSlitAlignment('down')
         
    
    
def checkRailSlitAlignment(rail_position = 'up'):
    # prepare for s3 scan
    pos s3gapY 0.01 s4gapY 2
    #scan s3
    cscan s3cenY 0.04 0.001 w .2 d2
    #record the peak position
    s3_peak_pos = peak.result.pos
    
    # prepare for s4 scan
    pos s3gapY 2 s4gapY 0.01
    #scan s4
    cscan s4cenY 0.04 0.001 w .2 d2
    #record the peak position
    s4_peak_pos = peak.result.pos
    
    print "For this go with the rail "+rail_position+", s3cenY was %1.4f and s4cenY was %1.4f" % (s3_peak_pos,s4_peak_pos)
    return

def findAFunctionForSettingDetY(start_z = 200, end_z=400):
    # this runs a scan of detiY at detZ = start_z and at end_z. 
    # returns m and c to form the equation of a straight line to determine
    # det1Y as a function of det1Z: det1Y = m * det1Z + c
    ##################################
    pos s4gapY 1 s4cenY 0 det1Z start_z
    sleep(6)
    scan det1Y -400 -380 1 w .5 d2
    go(peak)
    pos s4gapY 0.1 s4cenY 0
    cscan det1Y 1 0.1 w .5 d2
    start_y = peak.result.pos
    ##################################
    pos s4gapY 1 s4cenY 0 det1Z end_z
    sleep(6)
    scan det1Y -400 -380 1 w .5 d2
    go(peak)
    pos s4gapY 0.1 s4cenY 0
    cscan det1Y 1 0.1 w .5 d2
    end_y = peak.result.pos
    ##################################
    # do the equation
    dz = end_z - start_z
    dy = end_y - start_y
    m = dy/dz
    c = end_y - m*end_z
    
    pos s4gapY 2 s4cenY 0
    
    return m,c

def focalSpotSizeAsAFunctionOfZ(detz_values):
    # a script to measure the focal size as a function of distance.
    scan_processor.processors=[MaxPositionAndValue(), MinPositionAndValue(), CentreOfMass(), GaussianPeakAndBackground(), GaussianEdge(), Lcen(), Rcen(), BeamWidth(),BeamWidthSmooth()]
    
    widths = dnp.zeros_like(detz_values,dtype=float)
    
    # first we find the equation that relates det1Y to det1Z
    m,c = findAFunctionForSettingDetY(detz_values[0],detz_values[-1])
    
    for i,detz in enumerate(detz_values):
        detY_posn = m * detz + c + 1 # the + 1 is for a slit size of 2
        print "moving the detector to %3.1f (detZ) and %3.5f (detY, calculated)" % (detz, detY_posn)
        pos det1Z detz det1Y detY_posn
        print "sleeping"
        sleep(60)
        # the beam should be cut at around s4cenY = 0. 
        scan s4cenY -0.6 0.3 .002 w 0.05 d2 #was scan s4cenY -0.3 0.3 .002 w 0.05 d2
        
        widths[i] = beamwidthsmooth.result.width
    print "done."
    return detz_values, widths

def fullQCharacterisation():
    # this scans the beam size as a function of z for a range of mirror Q values
    #q_array = dnp.arange(215, 716, 25) #First try
    q_array = dnp.arange(290, 716, 25) #Second attempt
    
    min_detz = 200
    max_detz = 700
    
    for q in q_array:
        # change the volatges
        m1SetTarget(q)
        m1ApplyTarget()
        #wait for it to calm down
        sleep(600)
        #define the detz range
        detz_zero_for_this_q = q - 15
        this_min_detz = max(min_detz, detz_zero_for_this_q-100)
        this_max_detz = min(max_detz, detz_zero_for_this_q+100)
        
        detz_range = dnp.arange(this_min_detz, this_max_detz+1,10)
        
        # do the measurement
        print "for a q of %f we get a detz range of %f to %f" % (q, this_min_detz, this_max_detz)
        focalSpotSizeAsAFunctionOfZ(detz_range)
        
def measureBimorphReflectivityOptimisation():
    #Scans to measure the reflectivity of the (311) with, and then without, optimisation with the bimorph
    #05/10/2016
    #pos s1gapY 3.5 s1gapX 0.75
    #pos s2gapY 0.02 s2gapX 2
    #m1SetTarget(m1valsDLS_minus311ReflOffset_Times1p33)
    #m1ApplyTarget
    print "Starting to measure the reflectivity of the reflectivity-optimised mirror"
    measureReflectivityVertical(0, y_min=-2.25, y_max=2.05, y_num=75, p_min=-4.35, p_max=-4.1, p_step=0.002)
    print "Done! Now putting the mirror back to its focus-optimised state..."
    m1SetTarget(m1valsDLS)
    sleep(10)
    m1ApplyTarget
    print "Waiting for mirror to settle for 15 mins"
    sleep(900)
    print "Starting to measure the reflectivity of the focus-optimised mirror"
    measureReflectivityVertical(0, y_min=-2.25, y_max=2.05, y_num=75, p_min=-4.35, p_max=-4.1, p_step=0.002)
    print "measureBimorphReflectivityOptimisation complete!!!"
    
def REmeasureBimorphReflectivityOptimisation():
    #Scans to measure the reflectivity of the (311) with, and then without, optimisation with the bimorph
    #05/10/2016
    #pos s1gapY 3.5 s1gapX 0.75
    #pos s2gapY 0.02 s2gapX 2
    #m1SetTarget(m1valsDLS_minus311ReflOffset_Times1p33)
    #m1ApplyTarget
    
    # we had a beam trip in the above scan, so this recollects the relevant part. 
    original_y_range = dnp.linspace(-2.25,2.05,75)
    y_start = original_y_range[36]
    y_finish = original_y_range[50]
    print "Starting to measure the reflectivity of the reflectivity-optimised mirror"
    measureReflectivityVertical(0, y_min=y_start, y_max=y_finish, y_num=15, p_min=-4.35, p_max=-4.1, p_step=0.002)
    print "done"
    
def wholeOpticRefelctivityAsAFucntionOfFocalDistanceOfTheMirror(q_array = dnp.array([15,115,215,415,515,615,715,815,915,1015])):
    # the numbers in q_array are samZ distances in mm which the m1settarget script takes. 
    # scan m1Pitch -4.35 -4.1 0.002 w .1 d2 d4 d4_over_ringCurrent # it's currwently set to 315 and it hangs if you set it to where it is. 
    for q in q_array:
        # change the volatges
        m1SetTarget(q)
        m1ApplyTarget()
        #wait for it to calm down
        sleep(900)
        # do the reflectivity scan
        scan m1Pitch -4.35 -4.1 0.002 w .1 d2 d4 d4_over_ringCurrent


def lunchtimemirrorthings():
    measureReflectivityVertical(0, y_min=-2.25, y_max=2.05, y_num=21, p_min=-4.28, p_max=-4.17, p_step=0.004)
    m1SetTarget(315)
    m1ApplyTarget()
    sleep(600)
    print "Ready! be sure to change the femto gain down two notches"
    
    
print "m1 (multi-layer mirror) scripts loaded"
