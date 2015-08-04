from gda.configuration.properties import LocalProperties
from gda.scan import ConstantVelocityRasterScan
from gdascripts.scan.rasterscans import RasterScan
from gda.epics import CAClient
import time
import math
from plotters import Plotter
from gda.jython.commands.ScannableCommands import add_default

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
        self.horizontal_plotter = Plotter("horizontal_plotter",'Horizontal',"Horizontal Gradient")
        self.vertical_plotter = Plotter("vertical_plotter",'Vertical',"Vertical Gradient")
        self.transmission_plotter = Plotter("transmission_plotter",'transmission_total',"Transmission")
        add_default(self.horizontal_plotter.getPlotter())
        add_default(self.vertical_plotter.getPlotter())
        add_default(self.transmission_plotter.getPlotter())

    def __call__(self, *args):

        # if one arg, then use that as the map size, else ignore any and all args
        if len(args) == 1:
            self.Xsize = int(args[0])
            self.Ysize = int(args[0])
        elif len(args) == 2:
            self.Xsize  = int(args[0])
            self.Ysize = int(args[1])
        # not implemented still waiting for SLS feedback
        #else :
         #   self.map_size = CAClient().get("BL08I-EA-DET-01:HDF5:ExtraDimSizeX_RBV")
          #  print "Map size will be",str(self.map_size)
        self.PrepareForCollection(self.Xsize, self.Ysize)
        self.scanargs = [self.rowScannable, 1, float(self.Ysize), 1, self.columnScannable, 1, float(self.Xsize), 1, self.andor, 0.1]
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
        self.vertical_plotter.setAxis(Xsize,Ysize)
        self.horizontal_plotter.setAxis(Xsize,Ysize)
        self.transmission_plotter.setAxis(Xsize,Ysize)

# then create the scan wrapper for map scans
#_andorrastor = Finder.getInstance().find("_andorrastor")
#andormap = AndorMap(stxmDummy.stxmDummyY,stxmDummy.stxmDummyX,_andorrastor)
#alias("andormap")
#print "Command andormap(mapSize) created for arming the Andor detector before running STXM maps"
