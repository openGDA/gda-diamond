
f2names = {"out"  :"0",
           "empty":"0",
           "100%" :"0",
           "spare":"1",
           "50%"  :"2",
           "10%"  :"3",
           "1%"   :"4",
           "0.1%" :"5",
           "0.01%":"6"}

f2posns = {"0":6.795,
           "1":28.295,
           "2":42.295,
           "3":56.295,
           "4":70.795,
           "5":85.295,
           "6":98.795}

f2getlist = {"100%":6.795,
           "spare" :28.295,
           "50%"   :42.295,
           "10%"   :56.295,
           "1%"    :70.795,
           "0.1%"  :85.295,
           "0.01%" :98.795}

def f2Reset():
    caput("BL15J-OP-ATTN-02:MP1:SELECT.ZRST","Out")
    caput("BL15J-OP-ATTN-02:P1:VALA",f2posns["0"])
    caput("BL15J-OP-ATTN-02:MP1:SELECT.ONST","Spare")
    caput("BL15J-OP-ATTN-02:P1:VALB",f2posns["1"])
    caput("BL15J-OP-ATTN-02:MP1:SELECT.TWST","50% flux")
    caput("BL15J-OP-ATTN-02:P1:VALC",f2posns["2"])
    caput("BL15J-OP-ATTN-02:MP1:SELECT.THST","10% flux")
    caput("BL15J-OP-ATTN-02:P1:VALD",f2posns["3"])
    caput("BL15J-OP-ATTN-02:MP1:SELECT.FRST","1% flux")
    caput("BL15J-OP-ATTN-02:P1:VALE",f2posns["4"])
    caput("BL15J-OP-ATTN-02:MP1:SELECT.FVST","0.1% flux")
    caput("BL15J-OP-ATTN-02:P1:VALF",f2posns["5"])
    caput("BL15J-OP-ATTN-02:MP1:SELECT.SXST","0.01% flux")
    caput("BL15J-OP-ATTN-02:P1:VALG",f2posns["6"])
alias f2Reset

def f2Set(fname):
    wasd1in = d1pneumatic.getPosition()
    print "closing d1"
    d1in
    fname = fname.lower()
    if fname not in f2names:
        print "Filter %s not recognised. The following can be used:" % (fname)
        print f2names.keys()
        return
    caput("BL15J-OP-ATTN-02:MP1:SELECT",f2names[fname])
    waitFor("BL15J-OP-ATTN-02:P1:INPOS","1",checkTime=0.5,timeOut=25)
    if int(wasd1in) == 0:
        print "you had d1 out; retracting d1..."
        d1out
    print "f2 set to %s" % (fname)

def f2Get():
    currentPosition = float(caget("BL15J-OP-ATTN-02:Y.RBV"))
    a = []
    for f2position in f2getlist:
        if abs(f2getlist[f2position] - currentPosition) < 0.01:
             a.append(f2position)
    if a == []:
        print "Current f2 location not recognized"
    else:
        print "Current f2 setting: " + a[-1]
alias f2Get

print "f2 (endstation filter) scripts loaded"