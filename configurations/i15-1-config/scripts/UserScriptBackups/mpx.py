from gda.jython.commands.InputCommands import requestInput as raw_input
from time import sleep


def setMpxCollectionTime(time=1.):
    """Sets the medipix collection time. 
    This is necessary since when GDA sets the collection time it also
    unintentionally sets the bit mode to 2x12, which is fine so long as that's what you want. 
    
    """
    caput("BL15I-EA-DET-18:Merlin1:AcquireTime",time)
    sleep(.1)
    caput("BL15I-EA-DET-18:Merlin1:QuadMerlinMode",1)
    print "done. time set to %2.4f seconds" % time

def overnightNickelGhostMonitoring():
    setMpxCollectionTime(10)
    while True:
        eh3open
        scan x 1 1 1 pil3 1 mpx 10
        eh3close
        print "shutter closed... sleeping"
        sleep(60*30)

def quickShotPilMpx():
    eh3open
    scan x 1 1 1 pil3 10 mpx 10
    eh3close

def quickShotMpx(exposure):
    setMpxCollectionTime(exposure)
    d1out
    scan x 1 1 1 mpx 1
    d1in
    
def quickShotPil(exposure,repeats=1):
    d1out
    scan x 1 repeats 1 pil3 exposure
    d1in

def exposeMpxToFlat():
    setMpxCollectionTime(10)
    eh3open
    scan x 1 20 1 w 50 mpx 10 
    eh3close

def doseMpxCheckFlat():
    d1in
    eh3open
    posFlat = -30.875
    posBragg = -39.525
    f2vals = ["0.1%","1%","10%","50%","100%"]
    for val in f2vals:
        f2Set(val)
        pos samY posBragg
        quickShotMpx(1)
        print "Moving samY and f2..."
        pos samY posFlat
        f2Set("10%")
        print "Collecting flat now"
        quickShotMpx(10)
        sleep(30)
        print "Dean says you should have made up your mind by now... You have 10 more seconds..."
        sleep(10)
    
    
def whyHelloThereMrBurnsCouldYouSpareMeANickel():
    posFlat = -30.875
    posBragg = -39.525
    pos samY posBragg
    quickShotMpx(60)
    pos samY posFlat
    quickShotMpx(60)
    
def barneyGlassOvernightStabilityTest():
    # move it 52 mm away from the direct beam
    pos samY -77.6
    eh3open
    d1out
    setMpxCollectionTime(10)
    scan x 1 720 1 w 50 mpx 10 bpm2statMean
    d1in
    eh3close
    print "done!"
    
def optimisticDutyCycleSynchronisation(onTime = 2500, offTime = 1000, voltsPerStepUp = 5, voltsPerStepDown = 5):
    step1 = float(onTime)/1000
    step2 = 500./(voltsPerStepDown*20)
    step3 = float(offTime)/1000
    step4 = 500./(voltsPerStepUp*20)
    total = step1 + step2 + step3 + step4 
    print str(total)+" seconds per loop"
    t0 = time.time()
    while True:
        t0 = time.time()
        quickShotMpx(1)
        sleep( total -time.time() + t0 + 0.6)
    
def collectHDFfilesIntoFolder(startNumber=4305, endNumber=4411):
    from shutil import copyfile
    from os import mkdir,path
    visit = "cm16757-1"
    newfolder = "/dls/i15-1/data/2017/cm16757-1/"+str(startNumber)+"-"+str(endNumber)+"-files"
    if not path.exists(newfolder):
        mkdir(newfolder)
    for i in range(startNumber,endNumber+1):
        filename = "/dls/i15-1/data/2017/cm16757-1/"+str(i)+"-mpx-files/00001.tif"
        copyfile(filename,newfolder+"/"+str(i)+"-mpx.tif")
    

def MPXovernightNickelGhostMonitoring():
    # FEEL THE BURN
    whyHelloThereMrBurnsCouldYouSpareMeANickel()
    # FEEL THE COLLECTIONS
    i = 0
    gogogo = True
    setMpxCollectionTime(10)
    while gogogo:
        d1out
        try:
            scan x 1 1 1 mpx 10
        except:
            d1in
            sleep(10)
            print "what happened there then?"
            i += 1
        d1in
        print "shutter closed... sleeping"
        if i == 5:
            gogogo = False
        sleep(60*30)
    eh3close

def PILovernightNickelGhostMonitoring():
    d1in
    eh3open
    i = 0
    gogogo = True
    while gogogo:
        d1out
        try:
            scan x 1 1 1 pil3 10
        except:
            d1in
            sleep(10)
            print "what happened there then?"
            i += 1
        d1in
        print "shutter closed... sleeping"
        if i == 5:
            gogogo = False
        sleep(60*30)
    eh3close
    
def doseMpxCheckFlat2():
    d1in
    eh3open
    posFlat = -30.875
    posBragg = -39.525
    tvals = [1,5,10,60]
    for val in tvals:
        pos samY posBragg
        quickShotMpx(val)
        print "Moving samY and f2..."
        pos samY posFlat
        print "Collecting flat now"
        quickShotMpx(1)
        sleep(30)
        print "Dean says you should have made up your mind by now... You have 10 more seconds..."
        sleep(10)
    
def scanNickelPeak():
    posBragg = -39.525
    posFlat = -30.875
    posBraggTop = posBragg + 5.39
    posBraggBot =  posBragg - 8.63
    setMpxCollectionTime(10)
    # 10 seconds per image
    # 20 minutes total = 1200 seconds
    # 120 points
    step_size = (posBraggTop - posBraggBot)/120
    d1out
    scan samY posBraggTop posBraggBot step_size mpx 10
    d1in
    pos samY posFlat
    print "TYPE THIS >>>>> optimisticDutyCycleSynchronisation(10000,20000)"
    
    
def TungstenFlatCheck():
    posBragg = -39.525+5
    otherPos = posBragg + 2
    d1in
    eh3open
    f2Set("100%")
    while True:
        pos samY posBragg
        quickShotMpx(10)
        pos samY otherPos
        quickShotMpx(10)
        
print "medipix scripts loaded"
