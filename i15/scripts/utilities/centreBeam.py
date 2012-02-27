# I15 routine to center diffractometer to the beam
#
# See BL Trac Ticket #5945
#
# To use, run "run('utilities/centreBeam')"

def centreBeam(pinsize_um, skipx=False, diode=d3, din=d3in, dout=None):
    """e.g.
        centreBeam(50)                     # Centre 50um pinhole
        centreBeam(50, True)               # Only centring y, skipping x
        centreBeam(50, False, d4, d4in)    # Centre both, using d4 rather than d3
        centreBeam(50, diode=d4, din=d4in) # As, above, alternate form
    
    If dout is given then use it to take the diode out and close the shutter.
    
    e.g.
        centreBeam(50, dout=d3out)"""
    print "centreBeam(%f, %r, %r, %r)" % (pinsize_um, skipx, diode.name, din.__name__)
    
    from gda.jython.commands.InputCommands import requestInput as raw_input
    
    overscan=3./1000 # Also do translation from um to mm
    orig_dx = pinx()
    orig_dy = piny()
    if abs(orig_dx) > 0.0001 or abs(orig_dy) > 0.0001:
        print "ERROR: pinx %.4f or piny %.4f is greater than 0.1um, please zero pin hole positions" % (orig_dx, orig_dy)
        return
    
    din()
    shopen()
    
    cscan piny pinsize_um*overscan 0.005 w .2 diode
    
    centre_dy = round(peak.result.pos, 3)
    diff_dy = centre_dy - orig_dy
    
    var = raw_input("Peak found at %.3f, move baseTab %.3f to centre here? (Y/n) " % (centre_dy, diff_dy))
    if var in ('y', 'Y', ''):
        print "Moving using `inc baseTab %.3f`" % diff_dy
        inc baseTab diff_dy
    else:
        print "To centre basetab use `inc baseTab %.3f`" % diff_dy
    
    if not skipx:
        cscan pinx pinsize_um*overscan 0.005 w .2 diode
        
        centre_dx = round(peak.result.pos, 3)
        diff_dx = centre_dx - orig_dx
        
        print "Peak found at %.3f, move dtransx %.3f to centre here? (Y/n/2/3/4) " % (centre_dx, diff_dx)
        var = raw_input("(if a number is selected, the measured value is multipled by this value first)")
        if var in ('y', 'Y', ''):
            print "Moving using `inc dtransx %.3f`" % diff_dx
            inc dtransx diff_dx
        if var in ('2', '3', '4'):
            diff_dx = diff_dx*(float(var))
            print "Moving using `inc dtransx %.3f`" % diff_dx
            inc dtransx diff_dx
        else:
            print "To centre dtransx use `inc dtransx %.3f`" % diff_dx
    
    if not dout==None:
        shclose()
        dout()