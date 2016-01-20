from gda.scan import ConstantVelocityRasterScan
from gdascripts.scan.rasterscans import RasterScan
from gda.epics import CAClient
import time
from plotters import Plotter
from gda.jython.commands.ScannableCommands import add_default, remove_default
from gda.factory import Finder
from gda.device.detector.addetector.triggering.HardwareTriggeredAndor import AndorTriggerMode

# For this map 2 detectors are used: Andor and Xmap.
# TODO: Move jython scripts to Java 
class XRFMap(RasterScan):

    def __init__(self,rowScannable,columnScannable,andor,vortex):
        RasterScan.__init__(self)
        self.map_size = 50 # default
        self.rowScannable = rowScannable
        self.columnScannable = columnScannable
        self.andor = andor
        self.vortex = vortex
        self.setROI1(0.25, 0.35)
        self.setROI2(0.37, 0.42)
        self.setROI3(0.45, 0.57)
        self.setROI4(0.65, 0.75)
        self.setROI5(0, 0)
        self.setROI6(0, 0)
        self.setROI7(0, 0)
        self.setROI8(0, 0)
        self.plotterList = [Plotter("roi1_plotter",'roi1_total',"ROI1")]
        self.plotterList.append(Plotter("roi2_plotter",'roi2_total',"ROI2"))
        self.plotterList.append(Plotter("roi3_plotter",'roi3_total',"ROI3"))
        self.plotterList.append(Plotter("roi4_plotter",'roi4_total',"ROI4"))
        self.plotterList.append(Plotter("roi5_plotter",'roi5_total',"ROI5"))
        self.plotterList.append(Plotter("roi6_plotter",'roi6_total',"ROI6"))
        self.plotterList.append(Plotter("roi7_plotter",'roi7_total',"ROI7"))
        self.plotterList.append(Plotter("roi8_plotter",'roi8_total',"ROI8"))
        self.collectionTime =0.1
        #default for the mode trigger is EXTERNAL_EXPOSURE
        if self.andor != None: 
            self.andor.getCollectionStrategy().setTriggerMode(AndorTriggerMode.EXTERNAL_EXPOSURE)
        self.vortex.getCollectionStrategy().getXmap().getCollectionMode().setPixelsPerBuffer(1)
        self.isTriggerModeExternal = False
        self.pixelsPerBuffer = 1
        self.plotRate = 0

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
        if (self.isTriggerModeExternal == True):
            self.prepareAndorExternalTriggerMode()
            print "Acquition Period", self.collectionTime
        else: 
            self.setAndorExternal_ExposureTriggerMode()
        if self.andor != None:
            self.scanargs = [self.rowScannable, 1, float(self.Ysize), 1, self.columnScannable, 1, float(self.Xsize), 1, self.andor, self.collectionTime, self.vortex,self.collectionTime]
            andormap.PrepareForCollection(self.Xsize, self.Ysize)
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
            # plot all points here as there is a buffer in EPICs and then all points in the buffer is sent to GDA
            plotter.getPlotter().setRate(0)

    # the setup of the trigger mode is done here because the xrfmap always use andor + xmap
    # using both detectors sometimes the Andor camera saturates due to the long exposure time required by Xmap
    def setAndorExternalTriggerMode(self,acquisitionTime):
        if self.andor != None:
            self.isTriggerModeExternal = True
            self.andor.getCollectionStrategy().setTriggerMode(AndorTriggerMode.EXTERNAL)
            #12 ms is needed for the image processing in Andor, so here the (acq period - exposure) = 12 ms, so the collection time 
            #corresponds to acquisitionTime - 12 ms
            self.collectionTime = acquisitionTime - 0.012
        
    def prepareAndorExternalTriggerMode(self):
        if self.andor != None:
            self.andor.getCollectionStrategy().setTriggerMode(AndorTriggerMode.EXTERNAL)
            self.andor.getCollectionStrategy().getAdBase().setAcquireTime(self.collectionTime)

    def setAndorExternal_ExposureTriggerMode(self):
        self.isTriggerModeExternal = False
        self.andor.getCollectionStrategy().setTriggerMode(AndorTriggerMode.EXTERNAL_EXPOSURE)
        
    def setPixelsPerBuffer(self,pixelsPerBuffer):
        self.pixelsPerBuffer = pixelsPerBuffer
        self.vortex.getCollectionStrategy().getXmap().getCollectionMode().setPixelsPerBuffer(pixelsPerBuffer)

    def getPixelsPerBuffer(self):
        return self.pixelsPerBuffer
    
    # here define the plotRate in seconds to avoid confusion, the rate in the plotter is set in ms so needs to multiply by 1000
    def setPlotRate(self,plotRate):
        self.plotRate = plotRate *1000
        
    def getPlotRate(self):
        return self.plotRate
    
    def help(self):
        print "xrfmap.setPixelsPerBuffer(pixelsPerBuffer): set up Xmap buffer size in EPICs, pixels per buffer is an int between 1 and 50.\n"
        print "xrfmap.getPixelsPerBuffer(): print the current value of Xmap pixels per Buffer in EPICs.\n"
        print "xrfmap.setAndorExternal_ExposureTriggerMode(): set up Andor to use EXTERNAL_EXPOSURE trigger. By default EXTERNAL_EXPOSURE trigger mode is used.\n"
        print "xrfmap.setAndorExternalTriggerMode(acquisitionPeriod): set up Andor to use External trigger. The acquisition period is in s.\n"
       # print "xrfmap.setPlotRate(plotRate):set up the plot rate of gdaclient. The plotRate is in s and its default value is 0.\n"
       # print "xrfmap.getPlotRate():get the value of the plot rate configured in the scan.\n"
        
# then create the scan wrapper for map scans
# col = stxmDummy.stxmDummyX
# row = stxmDummy.stxmDummyY

xrfmap = XRFMap(stxmDummy.stxmDummyY,stxmDummy.stxmDummyX,_andorrastor,_xmap)  # @UndefinedVariable
#xrfmap = XRFMap(stxmDummy.stxmDummyY,stxmDummy.stxmDummyX,None,_xmap)
print "Command xrfmap(mapSize) created for arming the XRF (Vortex) detector before running STXM maps"
