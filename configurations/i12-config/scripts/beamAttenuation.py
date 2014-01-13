print "Enabling attenuator changes in GDA"

# Additional information:
# filter 1:
#    0:2mm
#    1:0mm
#    2:8mm
    
# filter2:
#    0:1mm
#    1:0mm
#    2:4mm



def moveAttenuatorsTo(totalFiltration):
    
    
    if (totalFiltration!=0 or totalFiltration!=1 or totalFiltration!=2 or totalFiltration!=3 or totalFiltration!=4 or totalFiltration!=6 or totalFiltration!=8 or totalFiltration!=9 or totalFiltration!=12):
        print "Chosen attenuation thickness not available."
        print "Possible thickness: 0mm, 1mm, 2mm, 3mm, 4mm, 6mm, 8mm, 9mm or 12mm"
        #return
    # Define variables:
    print ""
    # array containing energy, crystal1 rot, crystal 2 rot, translation, mono2 diagnostic positions, based on motor positions found 10/2013
    arr=dnp.array([[
     [0, 1, 1],
     [1, 0, 1],
     [2, 0, 1],
     [3, 0, 0],
     [4, 1, 2],
     [6, 0, 2],
     [8, 2, 1],
     [9, 2, 0],
     [12, 2, 2],
     ]])
    
    # select row with filter thickness
    
    arrTrans=arr.transpose
       
    listofFiltration=arrTrans[0,:]
    listofFiltration.flatten()

    filtrationIndex=listofFiltration.data.index(totalFiltration)
    positionsForTotalFiltration=filtrationIndex
    
    # pull out motor positions from row
    
    getMotorPositionsForEachFilter=arr[:,positionsForTotalFiltration]
   
    positionForFilter1=getMotorPositionsForEachFilter.item(1)
    positionForFilter2=getMotorPositionsForEachFilter.item(2)
    
    
    print "Closing OH2 shutter."
    caput("BL12I-PS-SHTR-01:CON", 1) # 1 is closed. 0 is open
    sleep(1)
    shstat=int(caget("BL12I-PS-SHTR-01:CON"))
    ntries=0
    while (shstat != 1): #poll the shutter to be sure it is actually closed
        print "Shutter status:", shstat
        shstat=int(caget("BL12I-PS-SHTR-01:CON"))
        ntries+=1
        sleep(1)
        if (ntries >10):
            print "ERROR: Shutter is not closed"
            return    
    print "Shutter now closed."
    
    print "Moving Attenuators."
    caput("BL12I-AL-ATTN-02:MP2:SELECT", positionForFilter1)
    caput("BL12I-AL-ATTN-02:MP3:SELECT", positionForFilter2)
    ntries=0
    while (float(caget("BL12I-AL-ATTN-02:P2:INPOS")) != 1.0 or float(caget("BL12I-AL-ATTN-02:P3:INPOS")) != 1.0):
        print "  moving ..."
        ntries+=1
        sleep(2)
        if (ntries >500):
            print "ERROR: Attenuators did not reached position within expected time frame."
            return
        
    print "Attenuators at requested thickness " + `totalThickness` + "mm. OH2 shutter closed."