from gda.device.scannable import ScannableMotionBase
from gda.jython.commands import ScannableCommands
from gda.jython.commands.ScannableCommands import pos 
from gda.jython.commands.GeneralCommands import alias, vararg_alias
from gdascripts.utils import caput, caget
from time import sleep
from gda.factory import Finder

finder = Finder.getInstance()
try:
    s2=finder.find("s2")
    s3=finder.find("s3")
    t3=finder.find("t3")
    eh1shtr=finder.find("eh1shtr")
except:
    print("Motors could not be created, maybe already installed. Continuing ....")

########### INPUT PARAMETERS, CHANGE AS NEEDED #######################

def masterPositions():
    print "in masterPositions"
    detector_table = t3.m2z
    detector_diffzposition= 1200
    return detector_table , detector_diffzposition
    
def monodiffractionPositions():
     # detector positions
    detector_diffxposition= 757
    detector_diffyposition= -1
    #slitpositions
    s2_diffxcentre= 0
    s2_diffycentre=50
    s2_diffxsize=0.5
    s2_diffysize=0.5
    
    s3_yheight=50
    s3_diffxcentre=0
    s3_diffycentre=0
    s3_diffxsize=1
    s3_diffysize=1
    
    #beamstop positions for diffraction
    beamstopInBeam_x = 97.1
    beamstopInBeam_y = 10.1
    
    #calculated values
    beamstopInBeam_lowLimit = beamstopInBeam_x-10
    
    return detector_diffxposition, detector_diffyposition, s2_diffxcentre, s2_diffycentre, s2_diffxsize, s2_diffysize, s3_diffxcentre, s3_diffycentre, s3_diffxsize, s3_diffysize, s3_yheight, beamstopInBeam_x, beamstopInBeam_y, beamstopInBeam_lowLimit 
    
    
def monoimagingPositions():
    # detector positions
    detector_imagingxposition=1351.6
    
    #slitpositions
    s2_imagingxcentre= 0
    s2_imagingycentre=50
    s2_imagingxsize=9.5
    s2_imagingysize=8.0
    
    s3_yheight= 50
    s3_imagingxcentre=0
    s3_imagingycentre=0
    s3_imagingxsize=9.6
    s3_imagingysize=8
    
    beamstopOutofBeam_x = 125
    beamstopOutofBeam_y = 10.1
    
    #calculated values
    detector_imagingxposition_lowLimit = detector_imagingxposition-15   ## to restrict movement of pixium into beam when imaging
    beamstopOutofBeamx_lowLimit = beamstopOutofBeam_x-15
    
    return detector_imagingxposition, s2_imagingxcentre, s2_imagingycentre, s2_imagingxsize, s2_imagingysize, s3_imagingxcentre, s3_imagingycentre, s3_imagingxsize, s3_imagingysize, s3_yheight, beamstopOutofBeam_x, beamstopOutofBeam_y, detector_imagingxposition_lowLimit, beamstopOutofBeamx_lowLimit


def endOfHutchDiagnosticPositions():
    #position of t3 to view with end of hutch camera
    detector_diagnostic_xposition = 100
    
    return detector_diagnostic_xposition  


################################################################

## Only change for sequence of motor moves

#################################################################
def monodiffractionMode():
    
    detector_table, detector_diffzposition = masterPositions()
    detector_diffxposition, detector_diffyposition, s2_diffxcentre, s2_diffycentre, s2_diffxsize, s2_diffysize, s3_diffxcentre, s3_diffycentre, s3_diffxsize, s3_diffysize, s3_yheight, beamstopInBeam_x, beamstopInBeam_y, beamstopInBeam_lowLimit = monodiffractionPositions()
    
    print "\n *** Moving to monodiffractionMode. \n"
    
    print "***** Closing EH1 shutter."
    pos(eh1shtr, "Close")
    print "******* Shutter now closed. "
    print "Closing External shutter"
    caput("BL12I-PS-SHTR-03:CON", 1) # 1 is closed. 0 is open
    print "******* External Shutter Closed"
    
    print "***** Moving slits. "
    pos(s2.xc, s2_diffxcentre, s2.xs, s2_diffxsize)
    pos(s2.yc, s2_diffycentre, s2.ys, s2_diffysize)
    
    pos(s3.y, s3_yheight)
    pos(s3.xc, s3_diffxcentre, s3.xs, s3_diffxsize)
    pos(s3.yc, s3_diffycentre, s3.ys, s3_diffysize)
    print "******* Slits in diffraction position. "
    
    print "******* Moving beamstop into beam"
    pos(t3.m4x, beamstopInBeam_x)
    #pos(t3.m4rx,-64.2422)# workaround if beamstop x stops working
    #pos(t3.m4y, beamstopInBeam_y)

    print "***** Moving large detector table. "     
    pos(t3.x, detector_diffxposition)
    pos(detector_table)
    pos(detector_diffzposition)
    

    print "******* Large detector table in diffraction position. \n "
    

    
    print "*** Move complete! Diffraction mode! Shutter is CLOSED. \n"
    
alias("monodiffractionMode")

def moveToDiffractionMode():
    monodiffractionMode()
alias("moveToDiffractionMode")

def monoimagingMode():
    
    detector_table, detector_diffzposition = masterPositions()
    detector_imagingxposition, s2_imagingxcentre, s2_imagingycentre, s2_imagingxsize, s2_imagingysize, s3_imagingxcentre, s3_imagingycentre, s3_imagingxsize, s3_imagingysize, s3_yheight, beamstopOutofBeam_x, beamstopOutofBeam_y, detector_imagingxposition_lowLimit, beamstopOutofBeamx_lowLimit = monoimagingPositions()
        
    print "\n *** Moving to monoimagingMode \n"
    
    print "***** Closing EH1 shutter."    # 1 is closed. 0 is open\par
    pos(eh1shtr, "Close")
    print "******* Shutter now closed. "
    print "Closing External shutter"
    caput("BL12I-PS-SHTR-03:CON", 1) # 1 is closed. 0 is open
    print "******* External Shutter Closed"
    
    print "***** Moving slits."
    pos(s2.xc, s2_imagingxcentre, s2.xs, s2_imagingxsize)
    pos(s2.yc, s2_imagingycentre, s2.ys, s2_imagingysize)

    #pos(s3.y, s3_yheight)
    pos(s3.xc, s3_imagingxcentre, s3.xs, s3_imagingxsize)
    pos(s3.yc, s3_imagingycentre, s3.ys, s3_imagingysize)
    print "******* Slits now in position."
    print "***** Moving beam stop."

    pos(t3.m4x, beamstopOutofBeam_x)       ## move module 4 out of beam
    #pos(t3.m4rx,-74)# workaround if beamstop x stops working
    print "***** Moving large detector table."

    #caput("BL12I-MO-TAB-03:MOD4:X.LLM", beamstopOutofBeamx_lowLimit) ## setting low limit on t3.m4x to restrict beam stop hitting camera
    #checkpos = caget("BL12I-MO-TAB-03:MOD2:Z.RBV")
    #code using if statement that was here to check if module 2 in safe position not working. Needs re-writing. For time being, hard coded move inserted.
    # if t3.m2z < 1250:
    ## possibly needs an else statement before the t3.x move is requested.
    pos(t3.m2z, 1250) ## moving module 2 to save position   PUT IN IF THERE IS NO ANTI-COLLISION PROTECTION
    pos(t3.x, detector_imagingxposition)     ## move main x stage    PUT IN IF THERE IS NO ANTI-COLLISION PROTECTION
    #tomoAlignment.moveT3M1yAndT3XgivenT3M1zPos(tomoAlignment.getModule())  ## sets t3.x to specific position for current camera module
    #caput("BL12I-MO-TAB-03:X.LLM", detector_imagingxposition_lowLimit) ## setting low limit on t3.x to restrict pixium travel into beam
    print "******* Large detector table in position. \n"
    
    print "*** Move complete! Imaging mode! Shutter is CLOSED. \n"
    
alias("monoimagingMode")

def moveToImagingMode():
    monoimagingMode()
alias("moveToImagingMode")

def moveToEndOfHutchDiagnostic():
    
    detector_diagnostic_xposition = endOfHutchDiagnosticPositions()
    detector_imagingxposition, s2_imagingxcentre, s2_imagingycentre, s2_imagingxsize, s2_imagingysize, s3_imagingxcentre, s3_imagingycentre, s3_imagingxsize, s3_imagingysize, s3_yheight, beamstopOutofBeam_x, beamstopOutofBeam_y, detector_imagingxposition_lowLimit, beamstopOutofBeamx_lowLimit = monoimagingPositions()
    print "reached this point"

    print "\n *** Moving to end-of-hutch diagnostic camera\n"
    
    print "***** Closing EH1 shutter."    # 1 is closed. 0 is open\par
    pos(eh1shtr, "Close")
    print "******* Shutter now closed."
    
    print "******* Moving detector table in position"
    pos(t3.x, detector_diagnostic_xposition)
    
    print "******* Moving beamstop out of beam"
    pos(t3.m4x, beamstopOutofBeam_x)
    #pos(t3.m4rx,-74)#workaround if beamstop x stops working
    print "***** Moving slits."
    pos(s2.xc, s2_imagingxcentre)
    pos(s2.yc, s2_imagingycentre)
    pos(s2.xs, s2_imagingxsize)
    pos(s2.ys, s2_imagingysize)

    #pos(s3.xc, s3_imagingxcentre)
    pos(s3.xs, s3_imagingxsize, s3.ys, s3_imagingysize)
    print "******* Slits now in position."
    
    print "*** Move complete! Moved to end-of-hutch diagnostic camera! Shutter is CLOSED. \n"
alias("moveToEndOfHutchDiagnostic")


print "finished loading 'moveToImagingMode', 'moveToDiffractionMode', 'moveToEndOfHutchDiagnostic' "