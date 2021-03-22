from gda.device.scannable import ScannableMotionBase
from gda.jython.commands import ScannableCommands
from gda.jython.commands.ScannableCommands import pos 
from gda.jython.commands.GeneralCommands import alias, vararg_alias
from gdascripts.utils import caput, caget
from time import sleep
from gda.factory import Finder

try:
    s2=Finder.find("s2")
    s3=Finder.find("s3")
    t3=Finder.find("t3")
    eh1shtr=Finder.find("eh1shtr")
except:
    print("Motors could not be created, maybe already installed. Continuing ....")

########### INPUT PARAMETERS, CHANGE AS NEEDED #######################

def masterPositions():
    print "in masterPositions"
    detector_table = t3.m2z
    detector_diffzposition= 650
    detector_SAFEdiffzposition= 1300 # MUST be above 1300 - SAFE position to avoid collision with Granite block
    return detector_table , detector_diffzposition , detector_SAFEdiffzposition
    
def monodiffractionPositions():
     # detector positions
    detector_diffxposition= 753
    detector_diffyposition= 51
    #slitpositions
    s2_diffxcentre= 0.0
    s2_diffycentre=50.0
    s2_diffxsize=0.5 # BEAM SIZE for diffraction
    s2_diffysize=0.5 # BEAM SIZE for diffraction
    
    s3_yheight=50 # for MONO-beam: s3_yheight = 50 always
    s3_diffxcentre=0
    s3_diffycentre=0
    s3_diffxsize=3 # s3_diffxsize > s2_diffxsize
    s3_diffysize=3 # s3_diffysize > s2_diffysize
    
    #beamstop positions for diffraction
    beamstopInBeam_x = 116.5
    beamstopInBeam_y = 9.2
    
    #calculated values
    beamstopInBeam_lowLimit = beamstopInBeam_x-10
    
    return detector_diffxposition, detector_diffyposition, s2_diffxcentre, s2_diffycentre, s2_diffxsize, s2_diffysize, s3_diffxcentre, s3_diffycentre, s3_diffxsize, s3_diffysize, s3_yheight, beamstopInBeam_x, beamstopInBeam_y, beamstopInBeam_lowLimit 
    
    
def monoimagingPositions():
    # detector positions
    detector_imagingxposition=1348.75
    
    #slitpositions
    s2_imagingxcentre= 0
    s2_imagingycentre=50.0
    s2_imagingxsize=15
    s2_imagingysize=10
    
    s3_yheight= -150 # ' For MONO-beam: s3_yheight = 50 for M4 & M3; s3_yheight = -150 for M2 & M1
    s3_imagingxcentre=0
    s3_imagingycentre=0
    s3_imagingxsize=3 # s3_imagingxsize > s2_imagingxsize for M4 &M3, and they are out at s3_yheight=-150 for M2 & M1
    s3_imagingysize=3 # s3_imagingysize > s2_imagingysize for M4 &M3, and they are out at s3_yheight=-150 for M2 & M1
    
    beamstopOutofBeam_x = 126.5
    beamstopOutofBeam_y = 9.2
    
    #calculated values
    detector_imagingxposition_lowLimit = detector_imagingxposition-15   ## to restrict movement of pilatus into beam when imaging
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
    
    detector_table, detector_diffzposition, detector_SAFEdiffzposition = masterPositions()
    detector_diffxposition, detector_diffyposition, s2_diffxcentre, s2_diffycentre, s2_diffxsize, s2_diffysize, s3_diffxcentre, s3_diffycentre, s3_diffxsize, s3_diffysize, s3_yheight, beamstopInBeam_x, beamstopInBeam_y, beamstopInBeam_lowLimit = monodiffractionPositions()
    
    print "\n *** Moving to monodiffractionMode. \n"
    
    print "***** Closing EH1 shutter."
    pos(eh1shtr, "Close")
    print "******* Shutter now closed. "
    print "Closing External shutter"
    caput("BL12I-PS-SHTR-03:CON", 1) # 1 is closed. 0 is open
    print "******* External Shutter Closed"
    
    print "***** Moving slits. "
    pos(s2.xc, s2_diffxcentre, s2.yc, s2_diffycentre,)
    pos(s2.xs, s2_diffxsize, s2.ys, s2_diffysize)
    
    pos(s3.y, s3_yheight)
    pos(s3.xc, s3_diffxcentre, s3.xs, s3_diffxsize)
    pos(s3.yc, s3_diffycentre, s3.ys, s3_diffysize)
    print "******* Slits in diffraction position. "
    
    print "******* Moving beamstop into beam"
    pos(t3.m4x, beamstopInBeam_x)
    #pos(t3.m4rx,-64.2422)# workaround if beamstop x stops working
    #pos(t3.m4y, beamstopInBeam_y)

    print "***** Moving large detector table. "     
    curr_pos = t3.m2z.getPosition()
    if curr_pos < detector_SAFEdiffzposition:
        print "***** Moving large detector table to SAFE position to avoid collision with BEAMSTOP module. "     
        pos(t3.m2z, detector_SAFEdiffzposition) ## moving module 2 to save position   PUT IN IF THERE IS NO ANTI-COLLISION PROTECTION
    print "***** Moving large detector table to diffraction position. "     
    pos(t3.x, detector_diffxposition)
    print "***** Moving large detector table to requested position. "     
    pos(t3.m2z, detector_diffzposition)
    #pos(detector_table) do not understand meaning of this command
    #pos(detector_diffzposition) do not understand meaning of this command
    

    print "******* Large detector table in diffraction position. \n "
    
    print "*** Move complete! Diffraction mode! Shutter is CLOSED. \n"
    
alias("monodiffractionMode")

def moveToDiffractionMode():
    
    monodiffractionMode()
    
alias("moveToDiffractionMode")

def monoimagingMode():
    
    detector_table, detector_diffzposition, detector_SAFEdiffzposition = masterPositions()
    detector_imagingxposition, s2_imagingxcentre, s2_imagingycentre, s2_imagingxsize, s2_imagingysize, s3_imagingxcentre, s3_imagingycentre, s3_imagingxsize, s3_imagingysize, s3_yheight, beamstopOutofBeam_x, beamstopOutofBeam_y, detector_imagingxposition_lowLimit, beamstopOutofBeamx_lowLimit = monoimagingPositions()
        
    print "\n *** Moving to monoimagingMode \n"
    
    print "***** Closing EH1 shutter."    # 1 is closed. 0 is open\par
    pos(eh1shtr, "Close")
    print "******* Shutter now closed. "
    print "Closing External shutter"
    caput("BL12I-PS-SHTR-03:CON", 1) # 1 is closed. 0 is open
    print "******* External Shutter Closed"
    
    #print "******* Moving tilts of Sample table for imaging mode"
    #Sample Table 1 tilts
    #pos(ss1_rx, 0.0194)
    #pos(ss1_rz, 0.0067)
    #print "******* Finished moving tilts of Sample table for imaging mode"

    print "***** Moving slits."
    pos(s2.xc, s2_imagingxcentre, s2.yc, s2_imagingycentre)
    pos(s2.xs, s2_imagingxsize, s2.ys, s2_imagingysize)

    pos(s3.y, s3_yheight)
    pos(s3.xc, s3_imagingxcentre, s3.xs, s3_imagingxsize)
    pos(s3.yc, s3_imagingycentre, s3.ys, s3_imagingysize)
    print "******* Slits now in position."
    
    print "***** Moving beam stop."
    pos(t3.m4x, beamstopOutofBeam_x)       ## move module 4 out of beam
    #pos(t3.m4rx,-74)# workaround if beamstop x stops working
    print "***** Moving large detector table."

    curr_pos = t3.m2z.getPosition()
    if curr_pos < detector_SAFEdiffzposition:
        pos(t3.m2z, detector_SAFEdiffzposition) ## moving module 2 to save position   PUT IN IF THERE IS NO ANTI-COLLISION PROTECTION
    pos(t3.x, detector_imagingxposition)     ## move main x stage
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
print "..."
print "..."
