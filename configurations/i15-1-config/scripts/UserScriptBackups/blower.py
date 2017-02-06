from time import sleep

blowerPosns = {"in":50.5,
              "out":0}

# some blower commands
def setBlowerTemp(temp=30,rate=5):
    """ sets the blower temperature and ramprate.
    The APS say: 
    Heats .... from ambient temperature (25 °C) up to ~ 950 °C
    Max ramp rate on heating & cooling is 5 deg C/min (300 C/hour). 
    Below 300 °C a faster ramp rate of ~ 10°C/min may be used. 
    """
    if rate != 5:
        print "the rate should be left at 5 for the moment"
        return
    setpointPV = "BL15J-EA-BLOW-01:SP"
    rampratePV = "BL15J-EA-BLOW-01:RR"
    
    if temp > 999:
        print "the maximum temperature is 999. Setting to that instead."
        temp = 999
    caput(setpointPV,temp)
    
    print 'set point has been changed. You should wait for it to heat up.'

def blowerIn():
    caput("BL15J-EA-BLOWR-01:TLATE",blowerPosns["in"])
    sleep(8)
    print "blower moved in (hopefully)"
alias blowerIn
    
def blowerOut():
    caput("BL15J-EA-BLOWR-01:TLATE",blowerPosns["out"])
    sleep(8)
    print "blower moved out (hopefully)"
alias blowerOut
    
def blowerOff(offTemp=0):
    setBlowerTemp(0,rate=5)
    print "Blower is cooling down... Be patient!"

print 'blower.py scripts loaded'
