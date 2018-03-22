
def hex1axes():
    ptn = diff1vomega.getPosition()
    off = diff1vomegaoffset.getPosition()
    abs = ptn - off
    if abs<0:
        abs=abs+360
    if abs>360:
        abs=abs-360
    if (abs>=0 and abs<=75) or abs>=345:
        print "X+ upstream; Y+ up"
    if abs>=75 and abs<=165:
        print "X+ down; Y+ upstream"
    if abs>=165 and abs<=255:
        print "X+ downstream; Y+ down"
    if abs>=255 and abs<=345:
        print "X+ up; Y+ downstream"
    myoff = (abs%90)-30
    print "Rotated by "+str(myoff)+" degrees"

def hex1haxes():
    ptn = diff1homega.getPosition()
    off = diff1homegaoffset.getPosition()
    abs = ptn - off
    if abs<0:
        abs=abs+360
    if abs>360:
        abs=abs-360
    if (abs>=0 and abs<=15) or abs>=285:
        print "X+ towards ring; Y+ downstream"
    if abs>=15 and abs<=105:
        print "X+ downstream; Y+ towards hall"
    if abs>=105 and abs<=195:
        print "X+ towards hall; Y+ upstream"
    if abs>=195 and abs<=285:
        print "X+ upstrean; Y+ towards ring"
    myoff = (abs%90)-60
    print "Rotated by "+str(myoff)+" degrees"

alias("hex1axes")
alias("hex1haxes")
