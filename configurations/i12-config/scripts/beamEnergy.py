print "setting up beamEnergy script"

from gda.jython.commands.GeneralCommands import alias, vararg_alias
import scisoftpy as dnp
import time




def setEnergy(energy):

    #check it's save to move mono, move only allowed if mono in valid mode
        
    monoMode=int(caget('BL12I-OP-DCM-01:MODERBV'))
    if (monoMode!=2):
        print "Energy change not possible. Monochromator not in valid mode."
        return
 
    # array containing energy, crystal1 rot, crystal 2 rot, translation, mono2 diagnostic positions, based on motor positions found 10/2013
    arr=dnp.array([[
     [53, -2527.1, -1946.1, 668.8, -22.1],
     [60, -2264.9, -1687.2, 757.5, -50.8],
     [70, -1984.2, -1410.9, 884.1, -84.0],
     [80, -1769.2, -1204.1, 1010.7, -104.3],
     [90, -1606.1, -1042.0, 1137.3, -122.0],
     [100, -1476.0, -910.2, 1263.8, -136.0],
     [110, -1372.1, -812.9, 1390.3, -157.6],
     [120, -1282.0, -725.2, 1516.8, -157.4],
     [130, -1209.1, -645.3, 1643.3, -165.2],
     [140, -1145.3, -582.7, 1769.8, -172.4],
     [150, -1092.1, -530.1, 1896.3, -178.2]
     ]])

    # select row with energy
    arrTrans=arr.transpose
    listofEnergies=arrTrans[0,:]
    listofEnergies.flatten()
    energyIndex=listofEnergies.data.index(energy)
    motorPositionsForRequestedEnergy=energyIndex
    # pull out motor positions from row
    getMotorPositionsForRequestedEnergy=arr[:,motorPositionsForRequestedEnergy]
    angle1=getMotorPositionsForRequestedEnergy.item(1)
    angle2=getMotorPositionsForRequestedEnergy.item(2)
    translation=getMotorPositionsForRequestedEnergy.item(3)
    camMono2position=getMotorPositionsForRequestedEnergy.item(4)

    #calculate energies from equations based on above data
    #angle1=
    #angle2=
    #translation=
    #camMono2position=

    print " *** Requested energy: " + `energy` + "keV"
    print "  Moving monochromator motors to:"
    print "  mc1_bragg: " + `angle1` + "mdeg"
    print "  mc2_bragg: " + `angle2` + "mdeg"
    print "  mc2_z:" + `translation` + "mm"
    print "  camMono2_y: " + `camMono2position` + "mm"

    #m move motors
    pos(mc1_bragg, angle1)
    pos(mc2_bragg, angle2)
    pos(mc2_z, translation)
    caput("BL12I-OP-DCM-01:CAM2:Y.VAL",camMono2position)       #camMono2 y-position
    
    value2=camMono2position
    value1=float(caget("BL12I-OP-DCM-01:CAM2:Y.RBV"))
    value=abs(value1-value2)
    ntries=0
    while (value>0.01): #poll the shutter to be sure it is actually closed
        value1=float(caget("BL12I-OP-DCM-01:CAM2:Y.RBV"))
        value=abs(value1-value2)
        ntries+=1
        sleep(1)
        if (ntries >120):
            print "ERROR: camMono2_y not reaching position"
            return
    
    print "\n Monochromator at requested energy: " + `energy` + "keV. Fine tuning may be required."
alias("setEnergy")


