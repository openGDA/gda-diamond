def troughReset():
    global trough, troughArea, troughSpeed, troughPressure
    if 'trough' in globals():
        del trough
        print "trough deleted"
    if 'troughArea' in globals():
        del troughArea
        print "troughArea deleted"
    if 'troughSpeed' in globals():
        del troughSpeed
        print "troughSpeed deleted"
    if 'troughPressure' in globals():
        del troughPressure
        print "troughPressure deleted"

    print "Re-initialising trough..."
    try_execfile("BeamlineI07/useTrough.py")
    trough.stop()

    print "\nPlease remember to set the desired barrier speed again!"

alias("troughReset")
