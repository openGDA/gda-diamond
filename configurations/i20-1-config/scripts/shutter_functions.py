# Some convenience functions for opening and closing shutters. imh 24/2/2016
print "shutter_functions.py"

def openEHShutter():
    print "Opening EH shutter"
    shutter2.moveTo("Reset")
    shutter2.moveTo("Open")
    print shutter2.getPosition()

def closeEHShutter():
    print "Closing EH shutter"
    shutter2.moveTo("Close")
    print shutter2.getPosition()

def openFastShutter():
    print "Opening fast shutter"
    fast_shutter.moveTo("Open")
    java.lang.Thread.sleep(4000)
    print fast_shutter.getPosition()

def closeFastShutter():
    print "Closing fast shutter"
    fast_shutter.moveTo("Close")
    java.lang.Thread.sleep(4000)
    print fast_shutter.getPosition()


def setTurboSlitShutterPositions(openPos, closePos) :
    # turbo_slit_shutter.setPositions({})
    turbo_slit_shutter.setValues( {"Open":str(openPos), "Close":str(closePos), "Reset":str(closePos) } )
    print turbo_slit_shutter.getName()," positions ",turbo_slit_shutter.getValues()


from gda.epics import CAClient
def configureFastShutter() :
    # format of the readback position from epics
    posRbvFormat = "%.5f"
    upperDemandPv="BL20J-EA-FSHTR-01:P3201"
    lowerDemandPv="BL20J-EA-FSHTR-01:P3202"
    # make sure upper and lower positions match format of readback value 
    # or position lookup in EpicsSimplePostioner will fail.... 19/2/2019
    upperPos = posRbvFormat%float(CAClient.get(upperDemandPv))
    lowerPos = posRbvFormat%float(CAClient.get(lowerDemandPv))

    # fast_shutter.setPositions({})
    fast_shutter.setValues( { "Open":upperPos, "Close":lowerPos} )
    print fast_shutter.getName()," positions :",fast_shutter.getValues()

shopen = openEHShutter
alias shopen

shclose = closeEHShutter
alias shclose

fso = openFastShutter
alias fso

fsc = closeFastShutter
alias fsc
