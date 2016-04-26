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

