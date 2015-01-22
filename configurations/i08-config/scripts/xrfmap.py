from gda.scan import ConstantVelocityRasterScan
from gdascripts.scan import rasterscans
from gdascripts.scan.rasterscans import RasterScan
from gdascripts.scan.trajscans import setDefaultScannables
from gda.epics import CAClient
import time

class XRFMap(RasterScan):
     
    def __init__(self,rowScannable,columnScannable,andor,vortex):
        RasterScan.__init__(self)
        self.map_size = 50 # default
        self.rowScannable = rowScannable
        self.columnScannable = columnScannable
        self.andor = andor
        self.vortex = vortex
        self.setROI1(0, 0.5)
        self.setROI2(0.5, 1)
        self.setROI3(1, 1.5)
        self.setROI4(1.5, 2)
                 
    def __call__(self, *args):

        # if one arg, then use that as the map size, else ignore any and all args
        if len(args) == 1:
            self.Xsize = int(args[0])
            self.Ysize = int(args[0])
        elif len(args) == 2:
            self.Xsize  = int(args[0])
            self.Ysize = int(args[1])
        
        self.resetPlotters()
        if self.andor != None:
            self.scanargs = [self.rowScannable, 1, float(self.Ysize), 1, self.columnScannable, 1, float(self.Xsize), 1, self.andor, 0.1, self.vortex,0.1]   
            andormap.PrepareForCollection()
        else:
            self.scanargs = [self.rowScannable, 1, float(self.Ysize), 1, self.columnScannable, 1, float(self.Xsize), 1, self.vortex, 0.1]       
            
        RasterScan.__call__(self,self.scanargs)
     
    def _createScan(self, args):

        # TODO create/ configure a scannable which will oberve data points and broadcast out transmission/phase-contrast to plotting system
        
        # TODO get scan size from Epics PVs to replace self.map_size
        
        # TODO check Epics PV holding STXM status as a safety check

        #rasterscan row 1 20 1 col 1 20 1 _andorrastor .1 'col'
#         args = [self.rowScannable, 1, float(self.map_size), 1, self.columnScannable, 1, float(self.map_size), 1, self.andor]
        #self.ROISetup()
        myscan = ConstantVelocityRasterScan(self.scanargs)
        
        # TODO set a PV to tell stxm the scan number
        #scanNumber = scan.getScanNumber()
        
        # TODO tell the stxm the scan number, or the file prefix at this point

        return myscan
    
    def ROIstart(self,startEnergy):
        return int(startEnergy/self.getEnergyBinWidth())
        
    def ROIsize(self,startEnergy,stopEnergy):
        return int(stopEnergy/self.getEnergyBinWidth())- self.ROIstart(startEnergy)
    #EPICs ROI is set up with points number here we set up the ROI using beam energy
    
    def setROI1 (self,startEnergy,stopEnergy): 
        self.vortex.xmaproistats1.setRoi(self.ROIstart(startEnergy),0,self.ROIsize(startEnergy, stopEnergy),1,"roi1")
         
    def setROI2 (self,startEnergy,stopEnergy):   
        self.vortex.xmaproistats2.setRoi(self.ROIstart(startEnergy),0,self.ROIsize(startEnergy, stopEnergy),1,"roi2")
    
    def setROI3 (self,startEnergy,stopEnergy):  
        self.vortex.xmaproistats3.setRoi(self.ROIstart(startEnergy),0,self.ROIsize(startEnergy, stopEnergy),1,"roi3")
        
    def setROI4 (self,startEnergy,stopEnergy):
        self.vortex.xmaproistats4.setRoi(self.ROIstart(startEnergy),0,self.ROIsize(startEnergy, stopEnergy),1,"roi4")
        
    def getEnergyBinWidth(self):
        return float(CAClient().get("BL08I-EA-DET-02:DXP1:MCABinWidth_RBV"))
    
    def setBinSpectrumSize(self,binSize): 
        maxEnergy = 4.096       
        CAClient().put("BL08I-EA-DET-02:MCA1.NUSE",str(binSize))
        CAClient().put("BL08I-EA-DET-02:DXP1:MaxEnergy",str(maxEnergy))
    
    def resetPlotters(self):
        roi1_plotter.setXArgs(0, self.Xsize, 1)
        roi1_plotter.setYArgs(0, self.Ysize, 1)
        roi2_plotter.setXArgs(0, self.Xsize, 1)
        roi2_plotter.setYArgs(0, self.Ysize, 1)
        roi3_plotter.setXArgs(0, self.Xsize, 1)
        roi3_plotter.setYArgs(0, self.Ysize, 1)
        roi4_plotter.setXArgs(0, self.Xsize, 1)
        roi4_plotter.setYArgs(0, self.Ysize, 1)
        
# then create the scan wrapper for map scans
# col = stxmDummy.stxmDummyX
# row = stxmDummy.stxmDummyY
xrfmap = XRFMap(stxmDummy.stxmDummyY,stxmDummy.stxmDummyX,_andorrastor,_xmap)
#xrfmap = XRFMap(stxmDummy.stxmDummyY,stxmDummy.stxmDummyX,None,_xmap)
print "Command xrfmap(mapSize) created for arming the XRF (Vortex) detector before running STXM maps"
