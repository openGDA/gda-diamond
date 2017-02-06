
#samX, samY
samXYposns = {"spin":[-6.,144.785],
              "empty":[-6.,141.785],
              "eyeBLM":[-163.83,94.00],
              "eyeMLM":[-163.83,125.65]}

def samSelect(position):
    pos samX samXYposns[position][0] samY samXYposns[position][1]

def samAlign(position="",capSize=1.0):
    if position !="":
        samSelect(position)
    d2in
    scanRange = capSize*1.5
    scanStep = capSize/10.
    
    cscan samY scanRange scanStep w 0.1 d2
    print peak.result.pos
    cscan samY -scanRange scanStep w 0.1 d2
    print peak.result.pos
    #peak

def samSpin(on=True):
    if on == True:
        caput("BL15J-NT-POWER-01:1:CONTROL","On")
        waitFor("BL15J-NT-POWER-01:1:STATUS_RBV",1)
    else:
        caput("BL15J-NT-POWER-01:1:CONTROL","Off")
        waitFor("BL15J-NT-POWER-01:1:STATUS_RBV",0)

def spinOn():
    samSpin(True)
    print "Spinner on"
alias spinOn

def spinOff():
    samSpin(False)
    print "Spinner off"
alias spinOff

print "sam (sample stage) scripts loaded"