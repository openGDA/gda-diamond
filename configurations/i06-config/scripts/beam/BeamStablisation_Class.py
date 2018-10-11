from time import sleep
import math
from __builtin__ import object

from gdascripts.utils import caget
from gdascripts.pd.epics_pds import DisplayEpicsPVClass

exec("[m4fpitchRead, m5fpitchRead]=[None, None]")

m4fpitchRead = DisplayEpicsPVClass('m4fpitchRead','BL06I-OP-KBM-01:HFM:FPITCH:OFF','V','%f')
m5fpitchRead = DisplayEpicsPVClass('m5fpitchRead','BL06I-OP-KBM-01:VFM:FPITCH:OFF','V','%f')

class BeamStabilisation(object):
    def __init__(self, rois, leem_fov, leem_rot, m4fpitch, m5fpitch, m4fpitchRead, m5fpitchRead, psphi2):
        self.rois=rois
        self.leem_fov = leem_fov
        self.leem_rot = leem_rot
        self.m4fpitch = m4fpitch
        self.m5fpitch = m5fpitch
        self.m4fpitchRead = m4fpitchRead
        self.m5fpitchRead = m5fpitchRead
        self.psphi = psphi2
        self.M4_mum_to_Volt = 50
        self.M5_mum_to_Volt = 150
        self.maxIterations = 20
        self.maxError = 0.0035
        
    def getVerticalAsymmetry(self):
        topROI = self.getRoiAvg(1)-99
        bottomROI = self.getRoiAvg(3)-99
        #print "topRoi=", topROI, "   bottomRoi=",bottomROI
        return -(topROI-bottomROI)/(topROI+bottomROI)
    
    def getHorizontalAsymmetry(self):
        leftROI = self.getRoiAvg(4)-99
        rightROI = self.getRoiAvg(2)-99
        #print "leftRoi=", leftROI, "   rightRoi=",rightROI
        return -(rightROI - leftROI)/(rightROI + leftROI)
    
    def storeBeamPos(self):
        self.storedPos = self.getBeamPos() 
        return self.storedPos
    
    def getBeamPos(self):
        return [self.getHorizontalAsymmetry(), self.getVerticalAsymmetry()]
    
    def getStoredBeamPos(self):
        return self.storedPos
    
    def get_dS(self):
        #return the beam displacement relative to the stored position in pixel units
        newPos = self.getBeamPos()
        return [newPos[0]-self.storedPos[0], newPos[1]-self.storedPos[1] ]
    
    def rot_dS(self, dS):
        #rotate the beam displacement vector
        rotAngRad = -float(self.leem_rot.getPosition())/180.0*math.pi
        rotAngRad += float(self.psphi.getPosition())/180.0*math.pi
        dS_rotated = [0.0, 0.0]
        dS_rotated[0] = dS[0]*math.cos(rotAngRad) + dS[1]*math.sin(rotAngRad)
        dS_rotated[1] = -dS[0]*math.sin(rotAngRad) + dS[1]*math.cos(rotAngRad)  
        return dS_rotated
    
    def pixelToVolts(self, dS_rotated):
        #convert the rotated displacement vector in pixel into mirror fine pitch units (Volts)
        self.fov = float(self.leem_fov.getPosition())
        self.fovRot = self.leem_rot.getPosition()
        conv_factors = [self.M4_mum_to_Volt*1/self.fov, self.M5_mum_to_Volt*1/self.fov]
        dSrot_Volt = [-dS_rotated[0]/conv_factors[0], dS_rotated[1]/conv_factors[1]]
        return dSrot_Volt
    
    def moveBeam(self, dSrot_Volt):
        currentM4 = float(self.m4fpitchRead.getPosition())
        currentM5 = float(self.m5fpitchRead.getPosition())
        #print currentM4, currentM5
        #print currentM4+dSrot_Volt[0],currentM5+dSrot_Volt[1]
        self.m4fpitch.asynchronousMoveTo(currentM4+dSrot_Volt[0])
        self.m5fpitch.asynchronousMoveTo(currentM5+dSrot_Volt[1])
        sleep(0.5)
        return
    
    def getBeamShift(self):
        dS = self.get_dS()
        dS_rotated = self.rot_dS(dS)
        fov = float(self.leem_fov())
        return [dS_rotated[0]/1000.0*fov, dS_rotated[1]/1000.0*fov]
                
    def centerBeamSingle(self, dummyMoveFlag):
        self.setRois()
        sleep(0.15)
        dS = self.get_dS()
        dS_rotated = self.rot_dS(dS)
        dS_rot_Volt = self.pixelToVolts(dS_rotated)
        #this is just to reduce the motion as a test
        dS_rot_Volt[0]*=0.5
        dS_rot_Volt[1]*=0.5
        ####
        if not(dummyMoveFlag):
            print "moving", dS_rot_Volt
            self.moveBeam(dS_rot_Volt)
            sleep(3)
        return dS_rot_Volt
    
    def centerBeamAuto(self, dummyMoveFlag):
        print "KB fine pitch start positions: M4fpitch = ",m4fpitchRead.getPosition(), "  M5fpitch  = ",m5fpitchRead.getPosition()
        i = 0
        last_dS_rot = [1.0,1.0]
        sum_rot = 1
        print "iteration = ",i," error = ", sum_rot
        while ((i<self.maxIterations)and(sum_rot>self.maxError)):
            i+=1
            last_dS_rot = self.centerBeamSingle(dummyMoveFlag)
            sum_rot = abs(last_dS_rot[0])+abs(last_dS_rot[1])
            print "iteration = ",i," error = ", sum_rot
        if i >=  self.maxIterations:
            print "maximum iteration reached!."
      
    def getRoiAvg(self, roiNum):
        roiAvgPV = "BL06I-EA-DET-01:STAT"+str(roiNum)+":MeanValue_RBV"
        return float(caget(roiAvgPV))

