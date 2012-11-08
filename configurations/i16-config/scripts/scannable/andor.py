from gdascripts.utils import caput, caget

OPEN_DELAY = 0 #ms
CLOSE_DELAY = 0 #ms

def andor_trigger_output_enable():
    caput('BL16I-EA-ANDOR-01:ShutterControl', 'Open')
    caput('BL16I-EA-ANDOR-01:AndorShutterMode', 'Auto')
    caput('BL16I-EA-ANDOR-01:ShutterOpenDelay', OPEN_DELAY)
    caput('BL16I-EA-ANDOR-01:ShutterCloseDelay', CLOSE_DELAY)
    caput('BL16I-EA-ANDOR-01:ShutterMode', 2)

    
    print "andor shutter output *enabled*:"
    print "   open delay = %.1f ms" % float(caget('BL16I-EA-ANDOR-01:ShutterOpenDelay'))
    print "   close delay = %.1f ms" % float(caget('BL16I-EA-ANDOR-01:ShutterCloseDelay'))
    print "   (configure delays in "+ __file__ + ")"
    print "Use the 'shutter' output from the Andor detector to trigger a shutter"
        
    
def andor_trigger_output_disable():
    caput('BL16I-EA-ANDOR-01:ShutterControl', 'Close')
    caput('BL16I-EA-ANDOR-01:AndorShutterMode', 'Open')
    print "andor shutter output *disabled*"
