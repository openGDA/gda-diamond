    
def measureReflectivityVertical(fname, mirror_x, y_min=-2.25, y_max=2.05, y_num=21, p_min=-4.45, p_max=-4.0, p_step=0.002):
    # measures rocking curves for reflectivity as a function of Y.
    # Performs a rocking curve (defined by the inputs p_min/max/step) at various points
    # along Y (defined by y_min/max/num) at a single point in mirror_x and stores the result.
    from gda.data import NumTracker
    
    #position the mirror
    pos m1X mirror_x
    
    # position the slits
    #pos s2gapY 0.20 #or something else small
    
    # Generate the points
    s2cenY_array = dnp.linspace(y_min,y_max,y_num)
    
    # Do the loop
    for i,s2cenY_value in enumerate(s2cenY_array):
        pos s2cenY s2cenY_value
        scan m1Pitch p_min p_max p_step w .1 d2 d4 d4_over_ringCurrent
        text_string = 'Scan # %i, s2cenY = %1.5f, m1X of %3.5f . The peak (%2.3f) was at a pitch of %2.5f .' % (NumTracker("i15-1").getCurrentFileNumber(), s2cenY.getPosition(), m1X.getPosition(), maxval.result.maxval, peak.result.pos) 
        print text_string
    
