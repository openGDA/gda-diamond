from gda.jython.commands.GeneralCommands import alias, vararg_alias
from gda.jython.commands.ScannableCommands import *
from gdascripts.pd.epics_pds import DisplayEpicsPVClass, EpicsReadWritePVClass
import scisoftpy as dnp
import time
import math
from gda.factory import Finder
from gdascripts.utils import caput, caget

try:
    mc1_bragg=Finder.find("mc1_bragg")
    mc2_bragg=Finder.find("mc2_bragg")
    mc2_z=Finder.find("mc2_z")
    camMono2_y=Finder.find("camMono2_y")
except:
    print("Finder section (bragg,z,mono2_y) did not work, or was not required ")
    
try:
    '''dcm1_cap_1=Finder.find("dcm1_cap_1")
    dcm1_cap_2=Finder.find("dcm1_cap_2")
    dcm2_cap_1=Finder.find("dcm2_cap_1")
    dcm2_cap_2=Finder.find("dcm2_cap_2")
    '''
    dcm1_cap_1 = DisplayEpicsPVClass('dcm1_cap_1', 'BL12I-OP-DCM-01:BEND:XTAL1:CAP1', 'microns', '%.3f')
    dcm1_cap_2 = DisplayEpicsPVClass('dcm1_cap_2', 'BL12I-OP-DCM-01:BEND:XTAL1:CAP2', 'microns', '%.3f')
    dcm2_cap_1 = DisplayEpicsPVClass('dcm2_cap_1', 'BL12I-OP-DCM-01:BEND:XTAL2:CAP1', 'microns', '%.3f')
    dcm2_cap_2 = DisplayEpicsPVClass('dcm2_cap_2', 'BL12I-OP-DCM-01:BEND:XTAL2:CAP2', 'microns', '%.3f')
except:
    print("Finder section (dcm_cap) did not work, or was not required ")

try:
    from positionCompareMotorClass import PositionCompareMotorClass
    camMono2_y = PositionCompareMotorClass("camMono2_y", "BL12I-OP-DCM-01:CAM2:Y.VAL", "BL12I-OP-DCM-01:CAM2:Y.RBV", "BL12I-OP-DCM-01:CAM2:Y.STOP", 0.002, "mm", "%.3f")
except:
    print "Failed to create camMono2_y, or it was already created."
    
    
def calcMotorPositionsForEnergy(target_energy,cap1,cap2):
    rot_factor=113.27
    cap1_factor=0.451
    cap2_factor=0.414
    z_factor=3.9539
    d_factor=226.54
    
    print "Calculating target positions..."
    crystal1= -1000.0 * rot_factor/target_energy+cap1_factor*cap1
    crystal2= -1000.0 * rot_factor/target_energy+cap2_factor*cap2
    translation = 50.0 / dnp.tan(z_factor/target_energy)
    cam = 3141. * dnp.tan(z_factor/target_energy)

    print "Calculated Positions:"
    print "mc1_bragg",crystal1;
    print "mc2_bragg",crystal2;
    print "mc2_z",translation;
    print "camMono2_y",cam;
    
    return(crystal1,crystal2,translation,cam)


def moveToBeamEnergy(target_energy):
    """
       Crystal_1 = -1000 * 113.27/E + 0.451*CAP_1
       Crystal_2 = -1000 * 113.27/E + 0.414*CAP_2
       Z = 50 / tan(226.54/E) , if tan-function expects degrees
       Z = 50 / tan(3.9539/E), if tan-function expects radians
       D = 3141 * tan(226.54/E) , see above

       E in keV
       Crystal-angles in milligree
       Z in mm
       CAP sensors in micro-m
    """

    if(target_energy > 149.0):
        print("Target energy must be in the available range (53-149 kev)")
        return
    if(target_energy < 53.0):
        print("Target energy must be in the available range (53-149 kev)")
        return

    print("Trying to clear cap sensor ring fault")
    caput("BL12I-OP-DCM-01:MACSTA2:CLRF",0)
    caput("BL12I-OP-DCM-01:MACSTA3:CLRF",0)
    time.sleep(3)
    print("Finished trying to clear cap sensor ring fault")
    
    d11=dcm1_cap_1.getPosition()
    d12=dcm1_cap_2.getPosition()
    d21=dcm2_cap_1.getPosition()
    d22=dcm2_cap_2.getPosition()
    print "Positions before moving:"
    print "dcm1_cap_1",d11
    print "dcm1_cap_2",d12
    print "dcm2_cap_1",d21
    print "dcm2_cap_2",d22
    print "mc1_bragg",mc1_bragg.getPosition();
    print "mc2_bragg",mc2_bragg.getPosition();
    print "mc2_z",mc2_z.getPosition();
    print "camMono2_y",camMono2_y.getPosition();

    #Estimate cap-sensor value from the two sensor readouts.
    cap1=(d11+d12)/2.0
    #cap2=(d21+d22)/2.0
    cap2=d22
    print "avg cap sensor readings ",cap1,cap2
    if (cap1 < -50.0 or cap1 > 150.0):
       print("Unexpected value for cap sensor 1 %f"%cap1)
       return
    if (cap2 < -50.0 or cap2 > 150.0):
       print("Unexpected value for cap sensor 2 %f"%cap2)
       return

    #call the routine to do the calculations
    (crystal1,crystal2,translation,cam)=calcMotorPositionsForEnergy(target_energy,cap1,cap2)

    #actually move the motors 
    print "MOVING motors to calculated motor positions"
    #pos((mc1_bragg,mc2_bragg,mc2_z,camMono2_y),(crystal1,crystal2,translation,cam))
    pos(camMono2_y,cam)
    pos(mc2_z, translation,mc1_bragg,crystal1,mc2_bragg,crystal2)
    #pos(mc1_bragg, crystal1)
    #pos(mc2_bragg, crystal2)
    #pos(camMono2_y, cam)
    print "FINISHED moving the motors"
    print "Monochromator at nominally ", target_energy, "keV. "

def calcBeamEnergyPositions(target_energy):
    """
       Crystal_1 = -1000 * 113.27/E + 0.451*CAP_1
       Crystal_2 = -1000 * 113.27/E + 0.414*CAP_2
       Z = 50 / tan(226.54/E) , if tan-function expects degrees
       Z = 50 / tan(3.9539/E), if tan-function expects radians
       D = 3141 * tan(226.54/E) , see above

       E in keV
       Crystal-angles in milligree
       Z in mm
       CAP sensors in micro-m
    """

    if(target_energy > 120.0):
        print("Target energy must be in the available range (53-120 kev)")
        return
    if(target_energy < 53.0):
        print("Target energy must be in the available range (53-120 kev)")
        return

    print("Trying to clear cap sensor ring fault")
    caput("BL12I-OP-DCM-01:MACSTA2:CLRF",0)
    caput("BL12I-OP-DCM-01:MACSTA3:CLRF",0)
    time.sleep(3)
    print("Finished trying to clear cap sensor ring fault")
    
    d11=dcm1_cap_1.getPosition()
    d12=dcm1_cap_2.getPosition()
    d21=dcm2_cap_1.getPosition()
    d22=dcm2_cap_2.getPosition()
    print "Positions before moving:"
    print "dcm1_cap_1",d11
    print "dcm1_cap_2",d12
    print "dcm2_cap_1",d21
    print "dcm2_cap_2",d22
    print "mc1_bragg",mc1_bragg.getPosition();
    print "mc2_bragg",mc2_bragg.getPosition();
    print "mc2_z",mc2_z.getPosition();
    print "camMono2_y",camMono2_y.getPosition();

    #Estimate cap-sensor value from the two sensor readouts.
    cap1=(d11+d12)/2.0
    #cap2=(d21+d22)/2.0
    cap2=d22
    print "avg cap sensor readings ",cap1,cap2
    if (cap1 < -50.0 or cap1 > 150.0):
       print("Unexpected value for cap sensor 1 %f"%cap1)
       return
    if (cap2 < -50.0 or cap2 > 150.0):
       print("Unexpected value for cap sensor 2 %f"%cap2)
       return

    #call the routine to do the calculations
    (crystal1,crystal2,translation,cam)=calcMotorPositionsForEnergy(target_energy,cap1,cap2)

    #do not actually move the motors 
    print "NOT MOVING motors "
    print "Positions calculated for energy ", target_energy, "keV. "



print "finished loading 'moveToBeamEnergy' "
