from gda.configuration.properties import LocalProperties
from gda.scan import ConstantVelocityRasterScan
from gdascripts.scan.rasterscans import RasterScan
from gda.epics import CAClient
import time
import math
from plotters import Plotter
from gda.jython.commands.ScannableCommands import add_default
from gda.device.detector.addetector.triggering.HardwareTriggeredAndor import AndorTriggerMode

class AndorMap(RasterScan):

    def __init__(self, rowScannable, columnScannable, andor):
        RasterScan.__init__(self)
        self.Xsize = 50 # default
        self.Ysize = 50 # default
        self.rowScannable = rowScannable
        self.columnScannable = columnScannable
        self.andor = andor
        self.ROISetup()
        # setup the Andor trigger to internal for snapshots by default
        self.andor.getCollectionStrategy().getAdBase().setTriggerMode(0)
        self.plotterList = [Plotter("horizontal_plotter",'Horizontal',"Horizontal Gradient")]
        self.plotterList.append(Plotter("vertical_plotter",'Vertical',"Vertical Gradient"))
        self.plotterList.append(Plotter("transmission_plotter",'transmission_total',"Transmission"))
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
        self.PrepareForCollection(self.Xsize, self.Ysize)
        self.scanargs = [self.rowScannable, 1, float(self.Ysize), 1, self.columnScannable, 1, float(self.Xsize), 1, self.andor, 0.1]
        RasterScan.__call__(self,self.scanargs)

    def _createScan(self, args):
        myscan = ConstantVelocityRasterScan(self.scanargs)
        return myscan

#configure the ROIs for both the step and raster andor objects
    def ROISetup(self):
        Xsize = self.andor.getCollectionStrategy().getAdBase().getArraySizeX_RBV()
        Ysize = self.andor.getCollectionStrategy().getAdBase().getArraySizeY_RBV()
        XmidSize = Xsize/2
        YmidSize = Ysize/2

        print "Setting up Regions of Interest for andor and _andorrastor objects..."
        self.andor.roistats1.setRoi(0,0,XmidSize,YmidSize,"quadrant1")
        self.andor.roistats2.setRoi(0,YmidSize,XmidSize,YmidSize,"quadrant2")
        self.andor.roistats3.setRoi(XmidSize,0,XmidSize,YmidSize,"quadrant3")
        self.andor.roistats4.setRoi(XmidSize,YmidSize,XmidSize,YmidSize,"quadrant4")
        self.andor.roistats5.setRoi(0,0,Xsize,Ysize,"transmission")

    def OptimizeChunk(self):
        Xsize = self.andor.getCollectionStrategy().getAdBase().getArraySizeX_RBV()
        Ysize = self.andor.getCollectionStrategy().getAdBase().getArraySizeY_RBV()
        dataType = self.andor.getCollectionStrategy().getAdBase().getDataType()
        # Each chunk is 1 MByte
        chunkSize = (1024**2)
        #pixel size in bytes
        pixelSize = (dataType+1)*2
        print "pixelSize:",pixelSize
        framesPerChunk = (chunkSize)/(Xsize*Ysize*pixelSize)
        print "framesperChunk:",framesPerChunk
        self.andor.getAdditionalPluginList()[0].setFramesChunks(framesPerChunk)

    def OpenAndorShutter(self):
        if (LocalProperties.get("gda.mode") == 'live'):
            CAClient().put("BL08I-EA-DET-01:CAM:AndorShutterMode","1")

    def PrepareForCollection(self, Xsize, Ysize):   
        self.andor.getCollectionStrategy().getAdBase().stopAcquiring()
        time.sleep(1)
        self.OpenAndorShutter()
        self.ROISetup()
        self.OptimizeChunk()
        self.resetPlotters(Xsize, Ysize)

    def resetPlotters(self, Xsize, Ysize):
        for plotter in self.plotterList:
            plotter.setAxis(Xsize,Ysize)
            #refresh the plot every 1.2 s to avoid accumulation of points in the queue
            plotter.getPlotter().setRate(1200)

# then create the scan wrapper for map scans
#_andorrastor = Finder.find("_andorrastor")
#andormap = AndorMap(stxmDummy.stxmDummyY,stxmDummy.stxmDummyX,_andorrastor)
#alias("andormap")
#print "Command andormap(mapSize) created for arming the Andor detector before running STXM maps"
