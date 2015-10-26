from gda.scan import ConstantVelocityRasterScan
from gdascripts.scan.rasterscans import RasterScan
from gda.epics import CAClient
import time
from plotters import Plotter
from gda.jython.commands.ScannableCommands import add_default
from gda.factory import Finder

class XRFMap(RasterScan):
     
    def __init__(self,rowScannable,columnScannable,andor,vortex):
        RasterScan.__init__(self)
        self.map_size = 50 # default
        self.rowScannable = rowScannable
        self.columnScannable = columnScannable
        self.andor = andor
        self.vortex = vortex
        finder = Finder.getInstance()
        self.andormap = finder.find("andormap")
        self.setROI1(0, 0.5)
        self.setROI2(0.5, 1)
        self.setROI3(1, 1.5)
        self.setROI4(1.5, 2)
        self.setROI5(0, 0)
        self.setROI6(0, 0)
        self.setROI7(1, 1.5)
        self.setROI8(1.5, 2)
        self.plotterList = [Plotter("roi1_plotter",'roi1_total',"ROI1")]
        self.plotterList.append(Plotter("roi2_plotter",'roi2_total',"ROI2"))
        self.plotterList.append(Plotter("roi3_plotter",'roi3_total',"ROI3"))
        self.plotterList.append(Plotter("roi4_plotter",'roi4_total',"ROI4"))
        self.plotterList.append(Plotter("roi5_plotter",'roi5_total',"ROI5"))
        self.plotterList.append(Plotter("roi6_plotter",'roi6_total',"ROI6"))
        self.plotterList.append(Plotter("roi7_plotter",'roi7_total',"ROI7"))
        self.plotterList.append(Plotter("roi8_plotter",'roi8_total',"ROI8"))

        for plotter in self.plotterList:
            add_default(plotter.getPlotter())
        
    def __call__(self, *args):

        # if one arg, then use that as the map size, else ignore any and all args
        if len(args) == 1:
            self.Xsize = int(args[0])
            self.Ysize = int(args[0])
        elif len(args) == 2:
            self.Xsize  = int(args[0])
            self.Ysize = int(args[1])
        
        self.resetPlotters(self.Xsize, self.Ysize)
        if self.andor != None:
            self.scanargs = [self.rowScannable, 1, float(self.Ysize), 1, self.columnScannable, 1, float(self.Xsize), 1, self.andor, 0.1, self.vortex,0.1]   
            self.andormap.PrepareForCollection(self.Xsize, self.Ysize)
        else:
            self.scanargs = [self.rowScannable, 1, float(self.Ysize), 1, self.columnScannable, 1, float(self.Xsize), 1, self.vortex, 0.1]       
         
        RasterScan.__call__(self,self.scanargs)
     
    def _createScan(self, args):
        myscan = ConstantVelocityRasterScan(self.scanargs)
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

    def setROI5 (self,startEnergy,stopEnergy):
        self.vortex.xmaproistats5.setRoi(self.ROIstart(startEnergy),0,self.ROIsize(startEnergy, stopEnergy),1,"roi5")

    def setROI6 (self,startEnergy,stopEnergy):
        self.vortex.xmaproistats6.setRoi(self.ROIstart(startEnergy),0,self.ROIsize(startEnergy, stopEnergy),1,"roi6")

    def setROI7 (self,startEnergy,stopEnergy):
        self.vortex.xmaproistats7.setRoi(self.ROIstart(startEnergy),0,self.ROIsize(startEnergy, stopEnergy),1,"roi7")

    def setROI8 (self,startEnergy,stopEnergy):
        self.vortex.xmaproistats8.setRoi(self.ROIstart(startEnergy),0,self.ROIsize(startEnergy, stopEnergy),1,"roi8")

    def getEnergyBinWidth(self):
        return float(CAClient().get("BL08I-EA-DET-02:DXP1:MCABinWidth_RBV"))

    def setBinSpectrumSize(self,binSize): 
        maxEnergy = 4.096       
        CAClient().put("BL08I-EA-DET-02:MCA1.NUSE",str(binSize))
        CAClient().put("BL08I-EA-DET-02:DXP1:MaxEnergy",str(maxEnergy))

    def resetPlotters(self,Xsize, Ysize):
        for plotter in self.plotterList:
            plotter.setAxis(Xsize,Ysize)

# then create the scan wrapper for map scans
# col = stxmDummy.stxmDummyX
# row = stxmDummy.stxmDummyY
finder = Finder.getInstance()
stxmDummy = finder.find("stxmDummy")
_andorrastor = finder.find("_andorrastor")
_xmap = finder.find("_xmap")
xrfmap = XRFMap(stxmDummy.stxmDummyY,stxmDummy.stxmDummyX,_andorrastor,_xmap)
#xrfmap = XRFMap(stxmDummy.stxmDummyY,stxmDummy.stxmDummyX,None,_xmap)
print "Command xrfmap(mapSize) created for arming the XRF (Vortex) detector before running STXM maps"
