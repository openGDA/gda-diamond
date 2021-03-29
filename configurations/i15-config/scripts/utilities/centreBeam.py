# I15 routine to center diffractometer to the beam
#
# See BL Trac Ticket #5945
#
# To use, run "run('utilities/centreBeam')"

def centreBeam(pinsize_um, skipx=False, diode=d3, din=d3in, dout=None, auto=True):
    """
    This automatically centres the diffractometer to the beam. First it scans
    the pinhole to find the offset between beam and diffractometer centre, then
    it adjusts the diffractometer position to correct for the calculated offset.

    Options:
    
    If skipx is True, only centre piny rather than pinx and piny.
    The diode defaults to d3, but another can be specified if necessary.
    If a diode other than d3 is used, you should also specify the routine
        to move the diode in. This defaults to d3in.
    If dout is specified, then at the end of centreBeam() use dout to move
        the diode out and do a shclose. The default is to not move the diode
        out or close the shutters.
    If auto=False, move to the calculated peaks, but give the user a chance
        to confirm, abort or override the value of each correction.
    
    e.g.
        centreBeam(50)                     # Centre 50um pinhole
        centreBeam(50, True)               # Only centring y, skipping x
        centreBeam(50, False, d4, d4in)    # Centre both, using d4 rather than d3
        centreBeam(50, diode=d4, din=d4in) # As, above, alternate form
        centreBeam(50, auto=False)          # Centre 50um pinhole manually
    
    If dout is given then use it to take the diode out and close the shutter.
    
    e.g.
        centreBeam(50, dout=d3out)
    
    See: https://confluence.diamond.ac.uk/x/AwoCAg"""
    print "centreBeam(%f, %r, %r, %r)" % (pinsize_um, skipx, diode.name, din.__name__)
    
    from gda.jython.commands.InputCommands import requestInput as raw_input
    
    overscan=3./1000 # Also do translation from um to mm
    orig_dx = pinx()
    orig_dy = piny()
    if abs(orig_dx) > 0.005 or abs(orig_dy) > 0.005:
        print "ERROR: pinx %.4f or piny %.4f is greater than 5um, please zero pin hole positions" % (orig_dx, orig_dy)
        return
    
    din()
    shopen()
    
    cscan piny pinsize_um*overscan 0.005 w .2 diode
    
    centre_dy = round(peak.result.pos, 3)
    diff_dy = centre_dy - orig_dy
    
    if not auto:
        var = raw_input("Peak found at %.3f, move baseTab %.3f to centre here? (Y/n) " % (centre_dy, diff_dy))
    if auto or var in ('y', 'Y', ''):
        print "Moving using `inc baseTab %.3f`" % diff_dy
        inc baseTab diff_dy
    else:
        print "To centre basetab use `inc baseTab %.3f`" % diff_dy
    
    if not skipx:
        cscan pinx pinsize_um*overscan 0.005 w .2 diode
        
        centre_dx = round(peak.result.pos, 3)
        diff_dx = centre_dx - orig_dx
        
        print "Peak found at %.3f, move dtransx %.3f to centre here? (Y/n/2/3/4) " % (centre_dx, diff_dx)
        if not auto:
            var = raw_input("(if a number is selected, the measured value is multipled by this value first)")
        if auto or var in ('y', 'Y', ''):
            print "Moving using `inc dtransx %.3f`" % diff_dx
            inc dtransx diff_dx
        elif var in ('2', '3', '4'):
            diff_dx = diff_dx*(float(var))
            print "Moving using `inc dtransx %.3f`" % diff_dx
            inc dtransx diff_dx
        else:
            print "To centre dtransx use `inc dtransx %.3f`" % diff_dx
    
    if not dout==None:
        shclose()
        dout()