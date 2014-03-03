from gda.device.scannable import ScannableMotionBase
from gda.jython.commands import ScannableCommands
from gda.jython.commands.ScannableCommands import pos 
from gda.jython.commands import GeneralCommands
from gda.jython.commands.GeneralCommands import alias, vararg_alias
from gdascripts.utils import caput, caget
from time import sleep
from gda.device.scannable import PseudoDevice
from gda.factory import Finder

print "Setting up detector mode switching"

finder = Finder.getInstance()

s2=finder.find("s2")
s3=finder.find("s3")
t3=finder.find("t3")

########### INPUT PARAMETERS, CHANGE AS NEEDED #######################

##### for monodiffractionMode

try:
    t3
except:
    "Failed to find t3"

#t3_m2z_mycopy=finder.find('t3_m2z')
def masterPositions():
    detector_table = t3.t3_m2z
    detector_diffzposition=2000
    return detector_table, detector_diffzposition
    
def monodiffractionPositions():
     # detector positions
    detector_diffxposition=755
    detector_diffyposition=48.991
    #detector_diffzposition=1200
    
    #slitpositions
    s2_diffxcentre=0
    s2_diffycentre=50
    s2_diffxsize=0.3
    s2_diffysize=0.3
    
    s3_diffxcentre=0
    s3_diffycentre=0
    s3_diffxsize=1
    s3_diffysize=1
    
    #beamstop positions for diffraction
    beamstopInBeam_x = 94.4
    beamstopInBeam_y = 11.35
    
    #calculated values
    beamstopInBeam_lowLimit = beamstopInBeam_x-15
    return detector_diffxposition, detector_diffyposition, s2_diffxcentre, s2_diffycentre, s2_diffxsize, s2_diffysize, s3_diffxcentre, s3_diffycentre, s3_diffxsize, s3_diffysize, beamstopInBeam_x, beamstopInBeam_y, beamstopInBeam_lowLimit 
    
    
def monoimagingPositions():
    # detector positions
    detector_imagingxposition=1353.42
    
    #slitpositions
    s2_imagingxcentre=0
    s2_imagingycentre=50
    s2_imagingxsize=15
    s2_imagingysize=12
    
    #s3_yheight=50
    s3_imagingxcentre=0
    s3_imagingycentre=0
    s3_imagingxsize=13.0
    s3_imagingysize=11.5
    
    #beamstop positions during imaging
    beamstopOutofBeam_x = 149
    beamstopOutofBeam_y = 10
    
    #calculated values
    detector_imagingxposition_lowLimit = detector_imagingxposition-15   ## to restrict movement of pixium into beam when imaging
    beamstopOutofBeamx_lowLimit = beamstopOutofBeam_x-15
    return detector_imagingxposition, s2_imagingxcentre, s2_imagingycentre, s2_imagingxsize, s2_imagingysize, s3_imagingxcentre, s3_imagingycentre, s3_imagingxsize, s3_imagingysize, beamstopOutofBeam_x, beamstopOutofBeam_y, detector_imagingxposition_lowLimit, beamstopOutofBeamx_lowLimit
#try:
#    print "in try"
#    detector_table_master = t3.m2z
#    print "in try: detector_table_master = " + detector_table_master.getName()
#except:
#    print "in except"
#    print "detector_table_master = " + detector_table_master.getName()

def monodiffractionMode():
    
    detector_table, detector_diffzposition = masterPositions()
    detector_diffxposition, detector_diffyposition, s2_diffxcentre, s2_diffycentre, s2_diffxsize, s2_diffysize, s3_diffxcentre, s3_diffycentre, s3_diffxsize, s3_diffysize, beamstopInBeam_x, beamstopInBeam_y, beamstopInBeam_lowLimit = monodiffractionPositions()
    
    print "\n *** Moving to monodiffractionMode. \n"
    
    print "***** Closing EH1 shutter."
    caput("BL12I-PS-SHTR-02:CON", 1) # 1 is closed. 0 is open
    sleep(1)
    shstat=int(caget("BL12I-PS-SHTR-02:CON"))
    ntries=0
    while (shstat != 1): #poll the shutter to be sure it is actually closed
        print "Shutter status:", shstat
        shstat=int(caget("BL12I-PS-SHTR-02:CON"))
        ntries+=1
        sleep(1)
        if (ntries >10):
            print "ERROR: Shutter is not closed"
            return
    print "******* Shutter now closed. "
    
    print "***** Moving slits. "
    pos(s2.xc, s2_diffxcentre)
    
    pos(s2.xs, s2_diffxsize)
    pos(s2.yc, s2_diffycentre)
    pos(s2.ys, s2_diffysize)
 #   pos s3.y s3_yheight
    pos(s3.xc, s3_diffxcentre)
    pos(s3.xs, s3_diffxsize)
    pos(s3.yc, s3_diffycentre)
    pos(s3.ys, s3_diffysize)
    print "******* Slits now in position. "
    
    print "***** Moving large detector table. " 
    caput("BL12I-MO-TAB-03:X.LLM", 0) ## setting low limit on t3.x to allow pixium travel into beam
    sleep(3)
    pos(detector_table, detector_diffzposition)     
    pos(t3.x, detector_diffxposition)
    caput("BL12I-MO-TAB-03:MOD4:X.LLM", beamstopInBeam_lowLimit) ## setting low limit on t3.m4x to allow beam stop travel into beam
    pos(t3.m4x, beamstopInBeam_x)
    pos(t3.m4y, beamstopInBeam_y)
    print "******* Large detector table now in position. \n "
    

    
    print "*** Move complete! Diffraction mode! Shutter is CLOSED. \n"
    
alias("monodiffractionMode")


def moveToDiffractionMode():
    monodiffractionMode()
alias("moveToDiffractionMode")

def monoimagingMode():
    
    detector_table, detector_diffzposition = masterPositions()
    detector_imagingxposition, s2_imagingxcentre, s2_imagingycentre, s2_imagingxsize, s2_imagingysize, s3_imagingxcentre, s3_imagingycentre, s3_imagingxsize, s3_imagingysize, beamstopOutofBeam_x, beamstopOutofBeam_y, detector_imagingxposition_lowLimit, beamstopOutofBeamx_lowLimit = monoimagingPositions()
        
    print "\n *** Moving to monoimagingMode \n"
    
    print "***** Closing EH1 shutter."    # 1 is closed. 0 is open\par
    caput("BL12I-PS-SHTR-02:CON", 1)
    sleep(1)
    shstat=int(caget("BL12I-PS-SHTR-02:CON"))
    ntries=0
    while (shstat != 1): #poll the shutter to be sure it is actually closed
        print "Shutter status:", shstat
        shstat=int(caget("BL12I-PS-SHTR-02:CON"))
        ntries+=1
        sleep(1)
        if (ntries >10):
            print "ERROR: Shutter is not closed"
            return
    print "******* Shutter now closed. "
    
    print "***** Moving slits."
    pos(s2.xc, s2_imagingxcentre)
    pos(s2.xs, s2_imagingxsize)
    pos(s2.yc, s2_imagingycentre)
    pos(s2.ys, s2_imagingysize)
    pos(s3.xc, s3_imagingxcentre)
    pos(s3.xs, s3_imagingxsize)
    pos(s3.yc, s3_imagingycentre)
    pos(s3.ys, s3_imagingysize)
    print "******* Slits now in position."
    
    print "***** Moving large detector table."
    pos(t3.m4x, beamstopOutofBeam_x)       ## move module 4 out of beam
    caput("BL12I-MO-TAB-03:MOD4:X.LLM", beamstopOutofBeamx_lowLimit) ## setting low limit on t3.m4x to restrict beam stop hitting camera
    if t3.m2z < 1150:
        pos(detector_table, 1150) ## moving module 2 to save position
    pos(t3.x, detector_imagingxposition)     ## move main x stage
    #tomoAlignment.moveT3M1yAndT3XgivenT3M1zPos(tomoAlignment.getModule())  ## sets t3.x to specific position for current camera module
    caput("BL12I-MO-TAB-03:X.LLM", detector_imagingxposition_lowLimit) ## setting low limit on t3.x to restrict pixium travel into beam
    print "******* Large detector table in position. \n"
    
    print "*** Move complete! Imaging mode! Shutter is CLOSED. \n"
    
alias("monoimagingMode")

def moveToImagingMode():
    monoimagingMode()
alias("moveToImagingMode")

def moveToEndOfHutchDiagnostic():
    print "\n *** Moving to end-of-hutch diagnostic camera\n"
    
    print "***** Closing EH1 shutter."    # 1 is closed. 0 is open\par
    caput("BL12I-PS-SHTR-02:CON", 1)
    sleep(1)
    shstat=int(caget("BL12I-PS-SHTR-02:CON"))
    ntries=0
    while (shstat != 1): #poll the shutter to be sure it is actually closed
        print "Shutter status:", shstat
        shstat=int(caget("BL12I-PS-SHTR-02:CON"))
        ntries+=1
        sleep(1)
        if (ntries >10):
            print "ERROR: Shutter is not closed"
            return
    print "******* Shutter now closed."
    
    print "******* Moving detector table to safe positon"
    pos(t3.x, 300)
    
    print "*** Move complete! Moved to end-of-hutch diagnostic camera! Shutter is CLOSED. \n"
alias("moveToEndOfHutchDiagnostic")


print "\n The commands are now available: \n -moveToImagingMode \n -moveToDiffractionMode \n -moveToEndofHutchDiagnostic "