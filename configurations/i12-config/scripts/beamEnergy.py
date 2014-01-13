

print "setting up beamEnergy script"

from gda.jython.commands.GeneralCommands import alias, vararg_alias
import scisoftpy as dnp
import time
import math

def set_to_energy(target_energy):
    
    print "calculate Energy "
    
    charge = 1.60217646e-19;
    planks = 6.626068e-34;
    sp_light = 2.99792458e8;
    
    z_error = 17.2791  # error in z position of crystal 2 (mm)
    d1_error = 0.6594  # error in 2*theta1 (degrees)
    d2_error = -0.4669  # error in 2*theta2 (degrees)
    d0 = 0.3100  # estimated d-spacing (nm)
    h_cam = 260.7240  # starting position for height of camera (mm)
    z_cam = 3107.6098  # starting z position of camera (mm)
    wavelength_error = 6.506105185762627e-05  # error in wavelength (nm)
    
    target_wavelength = ((sp_light * planks / (target_energy * 1e-9)) / charge) / 1000
    
    target_c1 = (180/math.pi) * math.asin((target_wavelength - wavelength_error)/(2*d0)) + d1_error/2
    target_c2 = target_c1 - d1_error/2 + d2_error/2
    target_z = 50 / math.tan((2*target_c1 - d1_error)*math.pi/180) + z_error
    target_cam = (z_cam * math.tan((2*target_c1 - d1_error)*math.pi/180)) - h_cam
    
    print "target_c1  :" + `target_c1`
    print "target_c2  :" + `target_c2`
    print "target_z   :" + `target_z`
    print "target_cam :" + `target_cam`



def setEnergy(energy):

    #check it's save to move mono, move only allowed if mono in valid mode
        
    monoMode=int(caget('BL12I-OP-DCM-01:MODERBV'))
    if (monoMode!=2):
        print "Energy change not possible. Monochromator not in valid mode."
        return
 
    # array containing energy, crystal1 rot, crystal 2 rot, translation, mono2 diagnostic positions, based on motor positions found 10/2013
    arr=dnp.array([[
     [53, -2074.1, -1921.0, 668.8, -22.1],
     [60, -1826.9, -1672.4, 757.5, -50.8],
     [70, -1531.9, -1382.2, 884.1, -84.0],
     [80, -1350.1, -1205.1, 1010.7, -104.3],
     [90, -1191.0, -1046.0, 1137.3, -122.0],
     [100, -1068.3, -914.2, 1263.8, -136.0],
     [110, -956.4, -820.4, 1390.3, -157.6],
     [120, -872.3, -734.3, 1516.8, -157.4],
     [130, -796.7, -656.4, 1643.3, -165.2],
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


