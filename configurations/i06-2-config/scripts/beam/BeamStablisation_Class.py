from time import sleep
import math
from __builtin__ import object

from gdascripts.utils import caget
from gdascripts.pd.epics_pds import DisplayEpicsPVClass
from types import ListType
from gda.device.detector.nxdetector.roi import ImutableRectangularIntegerROI
from gda.device.detector import NXDetector
from gda.device.detector.nxdetector.plugin.areadetector import ADRoiStatsPair
from gda.scan import ScanInformation
from gdaserver import pcotif
from gda.factory import Finder
from beam.AreaDetectorROIs import ROI_STAT_Pair_Class

exec("[m4fpitchRead, m5fpitchRead]=[None, None]")

m4fpitchRead = DisplayEpicsPVClass('m4fpitchRead','BL06I-OP-KBM-01:HFM:FPITCH:OFF','V','%f')
m5fpitchRead = DisplayEpicsPVClass('m5fpitchRead','BL06I-OP-KBM-01:VFM:FPITCH:OFF','V','%f')

class BeamStabilisation(object):
    def __init__(self, rois, leem_fov, leem_rot, m4fpitch, m5fpitch, m4fpitchRead, m5fpitchRead, psphi, roistat_index=[1,2,3,4], pvRootName="BL06I-EA-DET-01"):
        self.rois=rois
        self.leem_fov = leem_fov
        self.leem_rot = leem_rot
        self.m4fpitch = m4fpitch
        self.m5fpitch = m5fpitch
        self.m4fpitchRead = m4fpitchRead
        self.m5fpitchRead = m5fpitchRead
        self.psphi = psphi
        self.pvRootName=pvRootName
        self.roistat_index=roistat_index
        self.M4_mum_to_Volt = 50
        self.M5_mum_to_Volt = 150
        self.maxIterations = 20
        self.maxError = 0.0035
        
    def getVerticalAsymmetry(self):
        topROI = self.getRoiAvg(self.roistat_index[0])-99
        bottomROI = self.getRoiAvg(self.roistat_index[2])-99
        #print "topRoi=", topROI, "   bottomRoi=",bottomROI
        return -(topROI-bottomROI)/(topROI+bottomROI)
    
    def getHorizontalAsymmetry(self):
        leftROI = self.getRoiAvg(self.roistat_index[3])-99
        rightROI = self.getRoiAvg(self.roistat_index[1])-99
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
        self.setupROIs()
        i = 0
        last_dS_rot = [1.0,1.0]
        sum_rot = 1
        print "iteration = ",i," error = ", sum_rot
        try:
            self.prepareROIsForCollection(1)
            while ((i<self.maxIterations)and(sum_rot>self.maxError)):
                i+=1
                last_dS_rot = self.centerBeamSingle(dummyMoveFlag)
                sum_rot = abs(last_dS_rot[0])+abs(last_dS_rot[1])
                print "iteration = ",i," error = ", sum_rot
        except:
            self.stopROIStatsPair()
        finally:
            self.completeCollectionFromROIStatsPair()
            
        if i >=  self.maxIterations:
            print "maximum iteration reached!."
            
        return i<self.maxIterations
    
    def getRoiAvg(self, roiNum):
        roiAvgPV = self.pvRootName+":STAT"+str(roiNum)+":MeanValue_RBV"
        return float(caget(roiAvgPV))

    def calculateRotatedDisplacement(self, dS, rotAngRad):
        dS_rotated = [0.0, 0.0]
        dS_rotated[0] = dS[0] * math.cos(rotAngRad) + dS[1] * math.sin(rotAngRad)
        dS_rotated[1] = -dS[0] * math.sin(rotAngRad) + dS[1] * math.cos(rotAngRad)
        return dS_rotated

    def rot_dS(self, dS):
        #rotate the beam displacement vector
        raise NotImplementedError("Derived class must override this method.")
    
    def setupROIs(self):
        raise NotImplementedError("Derived class must override this method.")
        
    def clearROIs(self):
        raise NotImplementedError("Derived class must override this method.")
    
    def getROIStatsPair4DetectorFromGDA(self):
        raise NotImplementedError("Derived class must override this method.")
    
    def prepareROIsForCollection(self):
        raise NotImplementedError("Derived class must override this method.")
    
    def stopROIStatsPair(self):
        raise NotImplementedError("Derived class must override this method.")
    
    def completeCollectionFromROIStatsPair(self):
        raise NotImplementedError("Derived class must override this method.")

class BeamStablisationUsingAreaDetectorRoiStatPair(BeamStabilisation):
    
    def __init__(self, rois, leem_fov, leem_rot, m4fpitch, m5fpitch, m4fpitchRead, m5fpitchRead, psphi, roistat_index=[1,2,3,4], pvRootName="BL06I-EA-DET-01",detector=pcotif, roi_provider_name='pco_roi'):
        '''use the 1st 4 area detector's ROI-STAT pairs
        '''
        BeamStabilisation.__init__(self, rois, leem_fov, leem_rot, m4fpitch, m5fpitch, m4fpitchRead, m5fpitchRead, psphi, roistat_index, pvRootName)
        self.detector=detector
        self.roiProvider=Finder.find(roi_provider_name)
        
    def rot_dS(self, dS):
        #rotate the beam displacement vector
        rotAngRad = -float(self.leem_rot.getPosition())/180.0*math.pi
        rotAngRad += float(self.psphi.getPosition())/180.0*math.pi
        dS_rotated = self.calculateRotatedDisplacement(dS, rotAngRad)  
        return dS_rotated

    def setupROIs(self):
        '''update ROIs list in GDA ROI provider object but not yet send to EPICS
        This must be called when ROI is changed, and before self.prepareROIsForCollection(areadet)
        @param rois: list of rois i.e. [[x_start,y_start,x_size,y_size],[x_start,y_start,x_size,y_size],[x_start,y_start,x_size,y_size],[x_start,y_start,x_size,y_size]]
        '''
        if not type(self.rois)==ListType:
            raise Exception("Input must be a list of ROIs, each provides a list specifies [x_start,y_start,x_size,y_size]")
        i=1
        newRois=[]
        for roi in self.rois:
            newRoi=ImutableRectangularIntegerROI(roi[0],roi[1],roi[2],roi[3],'Region'+str(i))
            i +=1
            newRois.append(newRoi)
        if self.roiProvider is not None:
            self.roiProvider.updateRois(newRois)
        
    def clearROIs(self):
        '''remove all ROIs from the ROI provider
        '''
        self.roiProvider.updateRois([])
    
    def getROIStatsPair4DetectorFromGDA(self):
        ''' retrieve GDA ROI and STAT pairs for a given detector
        '''
        if not isinstance(self.detector, NXDetector):
            raise Exception("'%s' detector is not a NXDetector! " % (self.detector.getName()))
        additional_plugin_list = self.detector.getAdditionalPluginList()
        roi_stat_pairs=[]
        for each in additional_plugin_list:
            if isinstance(each, ADRoiStatsPair):
                roi_stat_pairs.append(each)
        return roi_stat_pairs
    
    def prepareROIsForCollection(self):
        '''configure ROIs and STATs plugins in EPICS for data collection with regions of interests
        '''
        for each in self.getROIStatsPair4DetectorFromGDA():
            #update ROIs and enable and configure EPICS rois and stats plugins
            try:
                each.prepareForCollection(1, ScanInformation.EMPTY)
            except:
                each.atCommandFailure()
    
    def stopROIStatsPair(self):
        '''stop or abort ROI and STAT plug-in processes. 
        This must be called when users interrupt or abort beam stabilisation process!
        '''
        for each in self.getROIStatsPair4DetectorFromGDA():
            each.stop()
    
    def completeCollectionFromROIStatsPair(self):
        '''must be called when beam stabilisation process completed!
        '''
        for each in self.getROIStatsPair4DetectorFromGDA():
            each.completeCollection()
            

class BeamStablisationUsingExtraRoiStatPair(BeamStabilisation):
    
    def __init__(self, rois, leem_fov, leem_rot, m4fpitch, m5fpitch, m4fpitchRead, m5fpitchRead, psphi, roistat_index=[7,8,9,10], pvRootName="BL06I-EA-DET-01"):
        '''use the 1st 4 area detector's ROI-STAT pairs
        '''
        BeamStabilisation.__init__(self, rois, leem_fov, leem_rot, m4fpitch, m5fpitch, m4fpitchRead, m5fpitchRead, psphi, roistat_index, pvRootName)
        self.roistatpair=ROI_STAT_Pair_Class(pvRootName)
        
    def rot_dS(self, dS):
        #rotate the beam displacement vector
        rotAngRad = -float(self.leem_rot.getPosition())/180.0*math.pi
        rotAngRad += float(self.psphi.getPosition())/180.0*math.pi
        dS_rotated = self.calculateRotatedDisplacement(dS, rotAngRad)    
        return dS_rotated

    def setupROIs(self):
        pass
        
    def prepareROIsForCollection(self):
        '''configure ROIs and STATs plug-ins in EPICS with regions of interests and its index
        '''
        if not type(self.rois)==ListType:
            raise Exception("Input must be a list of ROIs, each provides a list specifies [x_start,y_start,x_size,y_size]")

        for index, roi in zip(self.roistat_index, self.rois):
            self.roistatpair.setRoi(index, roi[0], roi[1], roi[2], roi[3])
    
    def stopROIStatsPair(self):
        '''stop or abort ROI and STAT plug-in processes. 
        This must be called when users interrupt or abort beam stabilisation process!
        '''
        for index in self.roistat_index:
            self.roistatpair.deactivateROIs(index)
    
    def completeCollectionFromROIStatsPair(self):
        '''must be called when beam stabilisation process completed!
        '''
        for index in self.roistat_index:
            self.roistatpair.deactivateROIs(index)
