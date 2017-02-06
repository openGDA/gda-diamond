    
    
    
def getCalibrationOffsets(slits = s3):
    """ Just returns the user calibration offsets for a slit group. 
    """
    if slits not in [s3,s4,s5]:
        print "Those slits (%s) not recognised." % (slits)
        return
    
    gapX = slits.getGroupMember(slits.name+'gapX')
    cenX = slits.getGroupMember(slits.name+'cenX')
    gapY = slits.getGroupMember(slits.name+'gapY')
    cenY = slits.getGroupMember(slits.name+'cenY')
    print ""
    print "*****************************************************"
    print "          Current Slit group %s offsets" % slits.name
    print "*****************************************************"
    print "    gapX    |    cenX    ||    gapY    |    cenY    |"
    print " %10.6f   %10.6f   %10.6f   %10.6f" % (gapX.getUserOffset(),cenX.getUserOffset(),gapY.getUserOffset(),cenY.getUserOffset())
    print "*****************************************************"