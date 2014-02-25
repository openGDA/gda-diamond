from gda.device.scannable import ScannableMotionBase
from gda.jython.commands import ScannableCommands
from gda.jython.commands.ScannableCommands import pos 
from gda.jython.commands.GeneralCommands import alias, vararg_alias
from gdascripts.utils import caput, caget
from time import sleep
from gda.factory import Finder

finder = Finder.getInstance()

s2=finder.find("s2")
s3=finder.find("s3")
t3=finder.find("t3")
eh1shtr=finder.find("eh1shtr")



########### INPUT PARAMETERS, CHANGE AS NEEDED #######################

def masterPositions():
    detector_table = t3.t3_m2z
    detector_diffzposition=1200
    return detector_table, detector_diffzposition
    
def monodiffractionPositions():
     # detector positions
    detector_diffxposition=755
    detector_diffyposition=48.991
    
    #slitpositions
    s2_diffxcentre=0
    s2_diffycentre=50
    s2_diffxsize=0.3
    s2_diffysize=0.3
    
    s3_diffxcentre=0
    s3_diffycentre=0
    s3_diffxsize=1.1
    s3_diffysize=1.1
    
    #beamstop positions for diffraction
    beamstopInBeam_x = 102.897
    beamstopInBeam_y = 14.85
    
    #calculated values
    beamstopInBeam_lowLimit = beamstopInBeam_x-15
    
    return detector_diffxposition, detector_diffyposition, s2_diffxcentre, s2_diffycentre, s2_diffxsize, s2_diffysize, s3_diffxcentre, s3_diffycentre, s3_diffxsize, s3_diffysize, beamstopInBeam_x, beamstopInBeam_y, beamstopInBeam_lowLimit 
    
    
def monoimagingPositions():
    # detector positions
    detector_imagingxposition=1352.14
    
    #slitpositions
    s2_imagingxcentre=0
    s2_imagingycentre=50
    s2_imagingxsize=4
    s2_imagingysize=3
    
    s3_yheight=50
    s3_imagingxcentre=0
    s3_imagingycentre=0
    s3_imagingxsize=1
    s3_imagingysize=1
    
    #beamstop positions during imaging
    beamstopOutofBeam_x = 149
    beamstopOutofBeam_y = 10
    
    #calculated values
    detector_imagingxposition_lowLimit = detector_imagingxposition-15   ## to restrict movement of pixium into beam when imaging
    beamstopOutofBeamx_lowLimit = beamstopOutofBeam_x-15
    
    return detector_imagingxposition, s2_imagingxcentre, s2_imagingycentre, s2_imagingxsize, s2_imagingysize, s3_imagingxcentre, s3_imagingycentre, s3_imagingxsize, s3_imagingysize, beamstopOutofBeam_x, beamstopOutofBeam_y, detector_imagingxposition_lowLimit, beamstopOutofBeamx_lowLimit


def endOfHutchDiagnosticPositions():
    detector_diagnostic_xposition = 300
    
    return detector_diagnostic_xposition  


################################################################

## Only change for sequence of motor moves

#################################################################
def monodiffractionMode():
    
    detector_table, detector_diffzposition = masterPositions()
    detector_diffxposition, detector_diffyposition, s2_diffxcentre, s2_diffycentre, s2_diffxsize, s2_diffysize, s3_diffxcentre, s3_diffycentre, s3_diffxsize, s3_diffysize, beamstopInBeam_x, beamstopInBeam_y, beamstopInBeam_lowLimit = monodiffractionPositions()
    
    print "\n *** Moving to monodiffractionMode. \n"
    
    print "***** Closing EH1 shutter."
    pos(eh1shtr, "Close")
    print "******* Shutter now closed. "
    
    print "***** Moving slits. "
    pos(s2.xc, s2_diffxcentre, s2.xs, s2_diffxsize)
    pos(s2.yc, s2_diffycentre, s2.ys, s2_diffysize)
 #   pos s3.y s3_yheight
    #pos(s3.xc, s3_diffxcentre, s3.xs, s3_diffxsize)
    #pos(s3.yc, s3_diffycentre, s3.ys, s3_diffysize)
    print "******* Slits now in position. "
    
    print "***** Moving large detector table. " 
    #caput("BL12I-MO-TAB-03:X.LLM", 0) ## setting low limit on t3.x to allow pixium travel into beam
    #sleep(3)
    pos(detector_table, detector_diffzposition)     
    pos(t3.x, detector_diffxposition)
    #caput("BL12I-MO-TAB-03:MOD4:X.LLM", beamstopInBeam_lowLimit) ## setting low limit on t3.m4x to allow beam stop travel into beam
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
    pos(eh1shtr, "Close")
    print "******* Shutter now closed. "
    
    print "***** Moving slits."
    pos(s2.xc, s2_imagingxcentre, s2.yc, s2_imagingycentre)
    pos(s2.xs, s2_imagingxsize, s2.ys, s2_imagingysize)

    #pos(s3.xc, s3_imagingxcentre, s3.yc, s3_imagingycentre)
    #pos(s3.xs, s3_imagingxsize, s3.ys, s3_imagingysize)
    print "******* Slits now in position."
    
    print "***** Moving large detector table."
    pos(t3.m4x, beamstopOutofBeam_x)       ## move module 4 out of beam
    #caput("BL12I-MO-TAB-03:MOD4:X.LLM", beamstopOutofBeamx_lowLimit) ## setting low limit on t3.m4x to restrict beam stop hitting camera
    if t3.m2z < 1150:
        pos(detector_table, 1150) ## moving module 2 to save position
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
    print "\n *** Moving to end-of-hutch diagnostic camera\n"
    
    print "***** Closing EH1 shutter."    # 1 is closed. 0 is open\par
    pos(eh1shtr, "Close")
    print "******* Shutter now closed."
    
    print "******* Moving detector table in position"
    pos(t3.x, detector_diagnostic_xposition)
    
    print "*** Move complete! Moved to end-of-hutch diagnostic camera! Shutter is CLOSED. \n"
alias("moveToEndOfHutchDiagnostic")


print "finished loading 'moveToImagingMode', 'moveToDiffractionMode', 'moveToEndofHutchDiagnostic' "