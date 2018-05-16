
print "\n Setting up pixium scripts\n" 
from pv_scannable_utils import caget, caput
from gdascripts.parameters import beamline_parameters
from time import sleep

def pixiumAfterIOCStart():
    jms=beamline_parameters.JythonNameSpaceMapping()
    pixium=jms.pixium    
    print "\n Now starting Pixium startup"
    caput("BL12I-EA-DET-05:PIX:DetectorState_RBV.PROC", 1)
    sleep(1)
    caput("BL12I-EA-DET-05:PIX:DetectorState_RBV.PROC", 1)
    sleep(1)
    caput("BL12I-EA-DET-05:PIX:DetectorState_RBV.PROC", 1)
    sleep(1)
    caput("BL12I-EA-DET-05:PIX:DetectorState_RBV.PROC", 1)
    sleep(1)
    caput("BL12I-EA-DET-05:PIX:DetectorState_RBV.PROC", 1)
    sleep(1)
    print "\n *** Setting pixium mode. "
    
    curr_logical_mode_output_as_string = caget("BL12I-EA-DET-05:PIX:LogicalMode_RBV")
    print "\n Complete output from caget for current logical mode: ", curr_logical_mode_output_as_string
    try:
        # just in case, strip any whitespace
        curr_logical_mode_output_as_string.strip()
        # assume the above caget output to be of the form: 'logical mode 0', 'logical mode 1', etc
        curr_logical_mode_output_as_string_array = curr_logical_mode_output_as_string.split()
        curr_logical_mode_as_str = curr_logical_mode_output_as_string_array[2].strip()
        #print "\n Current logical mode as string: ", curr_logical_mode_as_str
    except:
        # assume the above caget output to be of the form: '0', '1', etc
        curr_logical_mode_as_str = curr_logical_mode_output_as_string
    #modeno=int(caget("BL12I-EA-DET-05:PIX:LogicalMode_RBV")) # checks current mode number
    modeno=int(curr_logical_mode_as_str) # checks current mode number
#    print "\n Current logical mode as integer: ", modeno
    offsetno=int(caget("BL12I-EA-DET-05:PIX:OffsetReferenceNumber_RBV")) # checks durrent offset refence
    if offsetno==0:                          # sets the mode depending on offset reference, then changes back to mode(0,1) (80ms exposure)  
        pixium.setMode(modeno, 1)
        sleep(1)
        pixium.setMode(modeno, 0)
    else:
        pixium.setMode(modeno, 0)  
    sleep(2)
#   caput("BL12I-EA-DET-05:PIX:Acquire", 1)
#   sleep(2)
    pixium.resetAll()
    pixiumExp80ms()
    print "\n Pixium startup complete. NB: Exposure time 80ms. Please set appropriate exposure time. Calibration may be required."    

def modechange(logicalMode, offref, timeout):  # this is changing the logical mode and the offset reference, name not the most intuitive
    jms=beamline_parameters.JythonNameSpaceMapping()
    pixium=jms.pixium    
    print "*** Changing pixium mode. \n"
    print "******* Closing EH1 shutter."
    caput("BL12I-PS-SHTR-02:CON", "Close") ### 1 is closed. 0 is open
    sleep(1)
    shstat=caget("BL12I-PS-SHTR-02:CON")
    ntries=0
    while (shstat != "Close"): #poll the shutter to be sure it is actually closed
        print "Shutter status:", shstat
        shstat=caget("BL12I-PS-SHTR-02:CON")
        ntries+=1
        sleep(1)
        if (ntries >10):
            print "ERROR: Shutter is not closed"
            return
    pixium.setCaptureControl(False)
    pixium.stop()
    pixium.setCaptureControl(True)
    pixium.setMode(logicalMode, offref)
    print "******* Doing dark field calibration."	
    pixium.startOffsetCalibration(timeout)
    sleep(2)
    caput("BL12I-EA-DET-05:PIX:Acquire", 1)
###	caput("BL12I-PS-SHTR-02:CON", 0) ### 1 is closed. 0 is open
    print "******* Finished dark field calibration. \n"	
    caput("BL12I-EA-DET-05:PIX:ImageMode", 2)
    caput("BL12I-EA-DET-05:PIX:Acquire", 1)
    print "*** Finished changing pixium mode. \n"

def pixiumExp80ms():
    print "******* Changing pixium exposure time to 80ms"
    modechange(0, 0, 300)
    print " *** Pixium exposure time 80ms"

def pixiumExp500ms():
    print "******* Changing pixium exposure time to 500ms"
    modechange(0, 1, 300)
    print " *** Pixium exposure time 500ms"

def pixiumExp1000ms():
    print "******* Changing pixium exposure time to 1s"
    modechange(0, 2, 300)
    print " *** Pixium exposure time 1s"

def pixiumExp2000ms():	
    print "******* Changing pixium exposure time to 2s"
    modechange(0, 3, 300)
    print " *** Pixium exposure time 2s"

def pixiumExp4000ms():	
    print "******* Changing pixium exposure time to 4s"
    modechange(0, 4, 300)
    print " *** Pixium exposure time 4s"
    


    
#def Exp1ms():	
#   print "******* Changing pixium exposure time to 1ms"
#	modechange(5, 0, 300)
#alias("Exp1ms")


print"\n Available commands are: \n - pixiumAfterIOCStart \n - pixiumExp80ms \n - pixiumExp500ms \n - pixiumExp1000ms \n - pixiumExp2000ms \n - pixiumExp4000ms"