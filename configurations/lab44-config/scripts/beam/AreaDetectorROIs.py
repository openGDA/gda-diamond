from gda.epics import CAClient
from time import sleep

PV_ROOT_NAME="BL06I-EA-DET-01"

class ROI_STAT_Pair_Class():
    def __init__(self, pvRootName=PV_ROOT_NAME):
        self.pvRootName=pvRootName
        self.ca = CAClient()
        return
    
    def setRoi(self, roiNum, Xstart, Ystart, Xsize, Ysize):
        roiXStartPV = self.pvRootName+":ROI"+str(roiNum)+":MinX"
        roiYStartPV = self.pvRootName+":ROI"+str(roiNum)+":MinY"
        roiXSizePV = self.pvRootName+":ROI"+str(roiNum)+":SizeX"
        roiYSizePV = self.pvRootName+":ROI"+str(roiNum)+":SizeY"
        self.ca.caput(roiXStartPV,Xstart)
        self.ca.caput(roiYStartPV,Ystart)
        self.ca.caput(roiXSizePV,Xsize)
        self.ca.caput(roiYSizePV,Ysize)
        sleep(0.1)
        self.activateStat(roiNum)
        self.activateROIs(roiNum)
        return
    
    def activateStat(self, roiNum):
        statEnablePV = self.pvRootName+":STAT"+str(roiNum)+":EnableCallbacks"
        self.ca.caput(statEnablePV, "Enable")
        
        statStatOnPV = self.pvRootName+":STAT"+str(roiNum)+":ComputeStatistics"
        self.ca.caput(statStatOnPV, "Yes")
    
    def activateROIs(self, roiNum):
        roiEnablePV = self.pvRootName+":ROI"+str(roiNum)+":EnableCallbacks"
        self.ca.caput(roiEnablePV, "Enable")
        
        roiXEnablePV = self.pvRootName+":ROI"+str(roiNum)+":EnableX"
        self.ca.caput(roiXEnablePV, "Enable")
        
        roiYEnablePV = self.pvRootName+":ROI"+str(roiNum)+":EnableY"
        self.ca.caput(roiYEnablePV, "Enable")
        
    def deactivateStat(self, roiNum):
        statEnablePV = self.pvRootName+":STAT"+str(roiNum)+":EnableCallbacks"
        self.ca.caput(statEnablePV, "Disable")
        
        statStatOnPV = self.pvRootName+":STAT"+str(roiNum)+":ComputeStatistics"
        self.ca.caput(statStatOnPV, "No")
    
    def deactivateROIs(self, roiNum):
        roiEnablePV = self.pvRootName+":ROI"+str(roiNum)+":EnableCallbacks"
        self.ca.caput(roiEnablePV, "Disable")
        
        roiXEnablePV = self.pvRootName+":ROI"+str(roiNum)+":EnableX"
        self.ca.caput(roiXEnablePV, "Disable")
        
        roiYEnablePV = self.pvRootName+":ROI"+str(roiNum)+":EnableY"
        self.ca.caput(roiYEnablePV, "Disable")

    def getRoiAvg(self, roiNum):
        roiAvgPV = self.pvRootName+":STAT"+str(roiNum)+":MeanValue_RBV"
        return float(self.ca.caget(roiAvgPV))