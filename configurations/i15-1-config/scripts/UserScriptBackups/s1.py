#cenX,cenY, gapX, gapY
s1posns = {"closed":["","","",-0.5],
           "test":["","","",-1.0]}

def s1Set(posn):
    """Sets s1 (primary slits) to a default position.
    
    Currently only \"closed\" and \"test\" are available."""
    print "Moving s1 to position \"%s\"" %posn
    try:
        for i,axis in enumerate([s1cenX,s1cenY,s1gapX,s1gapY]):
            #print i
            #print axis
            if s1posns[posn][i] != "":
                pos axis s1posns[posn][i]
                if inPosition(axis,s1posns[posn][i],.01) == True:
                    print "   %s moved to %s mm" % (axis.name,axis.getPosition())
        print "s1Set complete! New s1 position: \"%s\"" %posn
    except:
        raise NameError("s1 position \""+str(posn)+"\" not recognised! s1 has not been moved!")

def s1close():
    s1Set("closed")
alias s1close

print "s1 (primary slits) scripts loaded"