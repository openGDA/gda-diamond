gvPVs = ["BL15I-VA-VALVE-01",
         "BL15I-VA-VALVE-02",
         "BL15I-VA-VALVE-03",
         "BL15I-VA-VALVE-04",
         "BL15I-VA-VALVE-05",
         "BL15I-VA-VALVE-06",
         "BL15I-VA-VALVE-07",
         "BL15I-VA-VALVE-08",
         "BL15I-VA-VALVE-10",
         "BL15J-VA-VALVE-01",
         "BL15J-VA-VALVE-02",
         "BL15J-VA-VALVE-03"]

def gateValvesClose():
    for gv in gvPVs:
        print "...closing "+str(gv)+"..."
        caput(gv+":CON",1)
    print "gateValvesClose complete!"
alias gateValvesClose

def gateValvesOpen():
    for gv in gvPVs:
        print "...opening "+str(gv)+"..."
        caput(gv+":CON",2)
        sleep(1)
        caput(gv+":CON",0)
    print "gateValvesOpen complete!"
alias gateValvesOpen

print "oh1 (optics hutch) scripts loaded"